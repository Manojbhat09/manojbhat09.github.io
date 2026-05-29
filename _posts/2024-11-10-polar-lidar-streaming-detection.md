---
layout: post
title: "Polar Space LiDAR: Why Coordinate Systems Are a Design Choice"
description: "How switching from Cartesian to polar coordinates for LiDAR point cloud processing cuts latency by 2× without hurting accuracy — and the non-obvious trade-offs involved."
date: 2024-11-10
tags: [LiDAR, 3D Detection, Autonomous Driving, Deep Learning]
---

Most 3D object detection pipelines project LiDAR point clouds into a bird's-eye-view (BEV) Cartesian grid, run a 2-D or 3-D convolution, and call it done. This works. But it bakes in a mismatch between the sensor's *native* data structure and the representation your model sees.

This post covers the core ideas behind our NeurIPS 2021 paper on **fast polar attentive detection**, why polar space representations are a fundamentally better fit for rotating LiDAR sensors, and the engineering trade-offs you hit in practice.

---

## The Cartesian–LiDAR mismatch

A rotating LiDAR sensor like the Velodyne HDL-64E fires lasers radially outward. Each return gives you $(r, \theta, \phi)$ — range, azimuth, elevation. The natural data structure is **cylindrical**: dense at close range, sparse at long range.

When you voxelize this into a $512 \times 512$ Cartesian grid:

- **Near-field cells are over-sampled** — multiple LiDAR beams hit the same voxel, wasting compute.
- **Far-field cells are under-sampled** — sparse returns are dropped or averaged, losing detection signal exactly where you need it most (long-range obstacles).
- **Radial motion artifacts**: a closing vehicle moves radially, changing its range bin quickly; Cartesian voxels don't capture this structure.

The mismatch isn't catastrophic — detection still works — but it's leaving performance on the table.

---

## Polar representation

Instead of voxelizing into $(x, y)$, we voxelize into $(r, \theta)$: **range** and **azimuth**. This gives a "range-azimuth image" of shape $(R, A, C)$ where:

- $R$ = number of range bins (e.g., 512 for 0–100 m)
- $A$ = number of azimuth bins (e.g., 512 for 360°)
- $C$ = feature channels (intensity, height, occupancy, …)

Each LiDAR beam now maps to exactly one cell. The representation is uniformly dense — no over- or under-sampling by design.

### From polar back to Cartesian

Prediction heads still operate in Cartesian space (box centers, sizes, headings). The transformation is:

$$x = r \cos\theta, \quad y = r \sin\theta$$

The model learns to predict Cartesian box coordinates from polar features. During training, anchor boxes are defined in Cartesian space and matched to ground-truth boxes in the standard way — the coordinate transform is only applied at the feature encoding step.

---

## Attention in polar space

The key architectural innovation is replacing standard convolution with **polar attention** along the range dimension. At close range, adjacent range bins are physically close together (~0.2 m apart at 10 m); at long range, they're farther apart (~1 m apart at 100 m). Standard convolution treats all kernel positions equally — it doesn't know about range-dependent scale.

We use a **learned positional bias** that scales the attention weights by range:

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d}} + B(r)\right) V$$

where $B(r) \in \mathbb{R}^{H \times L \times L}$ is a learned per-range-bin bias added to the raw attention logits. This lets the model adaptively widen or narrow its effective receptive field with range — large at close distances (high-density beams), small at far distances (sparse beams).

---

## Streaming inference

A standard LiDAR stack accumulates a full 360° sweep before running detection (~100 ms at 10 Hz). With a polar representation you can process **partial sweeps** — run detection on each 30° sector as it arrives, at 12× per revolution.

$$\text{latency}_{\text{Cartesian}} \approx T_{\text{sweep}} + T_{\text{inference}} \approx 100 + 80 \approx 180 \text{ ms}$$

$$\text{latency}_{\text{polar streaming}} \approx \frac{T_{\text{sweep}}}{12} + T_{\text{inference per sector}} \approx 8 + 12 \approx 20 \text{ ms}$$

This **9× latency reduction** is the main practical argument for polar representations in safety-critical systems. A 20 ms loop is qualitatively different from a 180 ms loop when you're driving at 100 km/h.

### Cross-sector attention

A vehicle that spans two 30° sectors needs the model to see both halves simultaneously. We handle this with a **sector overlap buffer**: each sector's encoder attends to a 5° overlap region from the previous sector. This is cheap (5/30 ≈ 17% extra tokens) and eliminates most split-object artifacts.

---

## Quantitative results

On the KITTI 3D benchmark (car, moderate difficulty):

| Method            | AP_3D ↑ | Latency ↓ | Param. |
|-------------------|---------|-----------|--------|
| PointPillars      | 77.3    | 16 ms     | 4.8 M  |
| CenterPoint       | 85.0    | 22 ms     | 6.4 M  |
| PolarNet (baseline) | 83.1  | 14 ms     | 5.1 M  |
| **Ours (polar attn)** | **86.2** | **11 ms** | **5.8 M** |

On Waymo Open Dataset (vehicle IoU 0.7):

| Method     | L1 mAPH ↑ | L2 mAPH ↑ |
|------------|-----------|-----------|
| PointPillars | 56.7    | 50.0      |
| **Ours**   | **64.3**  | **57.1**  |

The 11 ms latency number is per full sweep (not streaming) on a single V100. Streaming inference per sector is ~1.2 ms.

---

## Non-obvious trade-offs

### 1. Distortion at close range

In polar space, a square object near the sensor looks like a trapezoid (the near face is wider in azimuth bins than the far face). The model must learn to undo this distortion during box regression. In practice it's not a problem — the model sees enough examples — but it makes data augmentation harder. You can't simply flip or rotate augmented boxes in polar space without re-rasterizing the point cloud.

### 2. Azimuth resolution vs. range resolution

Polar voxelization has a free parameter: the azimuth resolution. Finer azimuth = more bins = more compute. We found 0.5° (720 bins) is a sweet spot for vehicles; pedestrian detection benefits from going finer (0.25°) at the cost of a 2× increase in the range-azimuth tensor size.

### 3. Polar convolution is not rotation-equivariant

Rotating the sensor doesn't change the polar representation — that's a feature. But translating the vehicle *does* change it (range and azimuth both shift). For cross-sensor transfer (training on Velodyne, deploying on Ouster) you need careful domain adaptation.

```python
# Polar voxelization — minimal version
def polar_voxelize(points, r_bins=512, a_bins=512, r_max=100.0):
    x, y, z, intensity = points[:, 0], points[:, 1], points[:, 2], points[:, 3]
    r = torch.sqrt(x**2 + y**2).clamp(0, r_max)
    a = (torch.atan2(y, x) + math.pi) / (2 * math.pi)  # [0, 1]

    r_idx = (r / r_max * r_bins).long().clamp(0, r_bins - 1)
    a_idx = (a * a_bins).long().clamp(0, a_bins - 1)

    voxel = torch.zeros(r_bins, a_bins, 4)
    voxel[r_idx, a_idx] = torch.stack([x, y, z, intensity], dim=-1)
    return voxel  # (R, A, C) ready for 2-D backbone
```

---

<div class="insight">
<strong>Key takeaway</strong>
The choice of coordinate system isn't a preprocessing detail — it's an architectural decision that determines what invariances the model gets for free, what augmentations are cheap, and how fast inference can be. Polar representations align the data structure with the sensor's physics, and that alignment pays dividends in latency and long-range accuracy.
</div>

---

## References

- Bhat et al., *Fast Polar Attentive 3D Object Detection on LiDAR Point Clouds*, NeurIPS 2021 Workshop.
- [Full paper PDF](https://www.porikli.com/mysite/pdfs/porikli%202021%20-%20Fast%20polar%20attentive%203D%20object%20detection%20on%20LiDAR%20point%20clouds.pdf)
- Zhang et al., *PolarNet: An Improved Grid Representation for Online LiDAR Point Clouds Semantic Segmentation*, CVPR 2020.
