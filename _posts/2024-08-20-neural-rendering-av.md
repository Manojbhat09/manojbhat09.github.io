---
layout: post
title: "Neural Rendering for Autonomous Vehicle Simulation"
description: "How NeRF-based scene representations are replacing hand-crafted 3-D asset pipelines in AV simulation — what we built at Rivian, and where the method still breaks down."
date: 2024-08-20
tags: [Generative AI, Autonomous Driving, Deep Learning, Robotics]
---

Simulation is the backbone of AV development. You can't test a software update on 10 million real miles every sprint — you simulate them. But classical simulation (hand-crafted 3-D assets, rule-based sensor models) has a fundamental gap: **the simulated world doesn't look like the real world**, and perception models trained or evaluated in simulation don't transfer cleanly.

Neural rendering — specifically **Neural Radiance Fields (NeRF)** and its derivatives — offers a different deal: reconstruct a photorealistic, controllable scene representation directly from real sensor logs. At Rivian we ran a hackathon exploring this for our autonomy stack, which resulted in a patent. This post is a technical write-up of what we built, what worked, and what surprised us.

---

## Why simulation fidelity matters so much

Consider a simple example: a perception model that detects vehicles. In classical simulation, vehicles are rendered as textured 3-D meshes under an approximated sensor model. In the real world, LiDAR returns are affected by surface reflectivity, material properties, rain drops, and sensor-specific scan patterns — none of which the classical model captures faithfully.

The consequence: **models trained heavily on simulated data exhibit a domain gap** when deployed on real sensor feeds. The gap is manageable but persistent, and closing it absorbs significant engineering effort (domain randomization, sim-to-real transfer, data augmentation).

Neural rendering directly sidesteps the asset pipeline. Instead of modeling scenes analytically, it fits a continuous function:

$$f_\theta: (\mathbf{x}, \mathbf{d}) \to (\mathbf{c}, \sigma)$$

mapping a 3-D point $\mathbf{x}$ and view direction $\mathbf{d}$ to color $\mathbf{c}$ and volume density $\sigma$. Volume rendering then integrates along camera rays to produce photorealistic images.

---

## The AV-specific challenges

Standard NeRF works beautifully for static scenes captured from a single viewpoint cluster (a table, a face, a room). AV data breaks all of these assumptions:

### 1. Dynamic agents

A parked truck is fine. A moving cyclist is a disaster — it occupies different spatial positions in each frame, creating a ghosted, semi-transparent artifact in the reconstructed field. Standard NeRF conflates dynamic content with static structure.

**Fix:** Decompose the scene into a static background NeRF and a set of per-object NeRFs, each tracked in their own object-centric coordinate frame. The transformation for object $k$ at time $t$:

$$\mathbf{x}_{\text{obj}} = R_k(t)^\top (\mathbf{x}_{\text{world}} - \mathbf{t}_k(t))$$

This requires running a 3-D object tracker on the sensor logs to extract per-object poses, then optimizing each object NeRF in its canonical frame.

### 2. Sparse viewpoint coverage

A camera mounted on a vehicle driving down a road sees each scene element from a narrow cone of viewpoints — not the hemisphere of views that makes vanilla NeRF work. The reconstruction is underconstrained: many possible scene geometries explain the same sparse observations.

**Fix:** Regularize with a depth prior from LiDAR. For each training ray, we supervise the expected depth against the LiDAR range reading at that pixel:

$$\mathcal{L}_\text{depth} = \left\| \hat{d} - d_\text{LiDAR} \right\|_1, \quad \hat{d} = \int_0^\infty t \cdot T(t)\sigma(t)\,dt$$

This dramatically stabilizes reconstruction in areas with limited viewpoint diversity (building facades, overhead structures).

### 3. Sensor modality gap

AV stacks run multiple sensors: cameras, LiDAR, radar. A NeRF trained on camera images can synthesize novel camera views, but it can't directly synthesize LiDAR point clouds for testing the perception stack.

**Fix:** Extend the radiance field to output LiDAR intensity and expected range in addition to RGB. The LiDAR model casts rays in the LiDAR scan pattern and integrates density to predict range and intensity. You get a single unified scene representation that renders both modalities.

---

## What we built at Rivian

The hackathon prototype combined three components:

1. **Instant-NGP backbone** (hash-encoded NeRF) for fast scene optimization — ~15 min per log segment on 4× A100s vs. hours for vanilla NeRF.

2. **Object-centric decomposition** using detections from our production perception stack to initialize object pose tracks, then jointly refine scene and object representations.

3. **LiDAR branch**: a two-head network outputting both RGB (camera supervision) and $(r, \text{intensity})$ (LiDAR supervision) from the same density field.

The key result: for static/semi-static scenes, we could synthesize sensor data from novel viewpoints that was indistinguishable from real data to our perception model (measured by detection AP on held-out synthetic vs. real comparisons). For fully dynamic scenes (busy intersections), quality degraded — handling fast-moving agents remains an open problem.

---

## What still breaks

**Fast motion.** A cyclist traveling at 25 km/h moves ~0.7 m per frame at 10 Hz. Our object tracking + per-object NeRF approach handles this if tracking is accurate. When the 3-D tracker loses the object (occlusion, crowded scenes), the NeRF degrades significantly.

**Long log segments.** NeRF optimized over a 60-second log (~600 frames) covers more of the scene but is much harder to optimize than a 10-second clip. The scene changes (parked cars entering/leaving), and the neural field has no way to represent time-varying static structure cleanly.

**Radar.** We didn't extend the model to radar. Radar reflections have fundamentally different physics (specular multipath, Doppler) that don't map naturally to a density-based volume.

---

## Where this is going

The next frontier is **generative NeRF** — instead of reconstructing a scene from real sensor data, generate plausible new scenes conditioned on map layout and agent behavior specifications. Several groups (Waymo, Wayve, and academic labs) are building diffusion-model-based approaches that output driving video conditioned on scene graphs. This would allow testing perception and planning on scenarios that have never occurred in the real dataset.

<div class="insight">
<strong>Thesis</strong>
Neural rendering isn't replacing simulation — it's replacing the asset pipeline. The physics simulation (dynamics, sensor timing, actuator models) stays. What changes is how scene geometry and appearance are represented: from hand-crafted meshes and textures to learned continuous fields fit directly to real-world sensor logs.
</div>

---

## References

- Mildenhall et al., *NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis*, ECCV 2020.
- Müller et al., *Instant Neural Graphics Primitives*, SIGGRAPH 2022.
- Tancik et al., *Block-NeRF: Scalable Large Scene Neural View Synthesis*, CVPR 2022.
- UniSim, *A Neural Closed-Loop Sensor Simulator*, CVPR 2023 (Waymo).
