---
layout: post
title: "Wayformer: Rethinking Motion Forecasting with Efficient Attention"
description: "A deep-dive into the Wayformer architecture — how factorized attention over agents and scene context achieves state-of-the-art trajectory prediction while staying practical for production AV stacks."
date: 2025-01-15
tags: [Motion Forecasting, Autonomous Driving, Transformer, Deep Learning]
---

Motion forecasting is one of the hardest sub-problems in autonomous driving. Given a few seconds of history for every agent in the scene — other cars, cyclists, pedestrians — your model must predict a distribution over their future trajectories. Get it wrong and your planner either over-brakes (annoying) or mis-allocates collision-avoidance budget (dangerous).

At Rivian I led the implementation of **Wayformer** for our offboard planning stack. This post covers the architecture, the key design choices that make it work, and the practical lessons from shipping it at scale.

---

## The core problem

A standard scene has $N$ agents, each with a $T$-step history. Naively attending every agent to every other agent at every timestep costs:

$$\mathcal{O}(N^2 \cdot T^2)$$

For a dense urban scene with $N = 64$ agents and $T = 50$ timesteps that's 10.2 M attention pairs per forward pass — before you've even touched the HD map. Wayformer's answer is *factorized attention*.

---

## Architecture overview

Wayformer decomposes the joint attention into two orthogonal axes:

1. **Temporal self-attention** — each agent attends to its own history tokens
2. **Social self-attention** — at each timestep, agents attend to each other

The input is a sequence of per-agent state vectors $\mathbf{x}_i^t \in \mathbb{R}^d$. After positional encoding these are arranged into a 2-D grid:

$$\mathbf{X} \in \mathbb{R}^{N \times T \times d}$$

### Temporal encoder

Temporal attention is applied row-wise (per agent, across time):

$$\mathbf{H}^{(l)}_{\text{temp}} = \text{softmax}\!\left(\frac{Q_t K_t^\top}{\sqrt{d}}\right) V_t, \quad \text{applied for each } i \in [N]$$

### Social encoder

Social attention is applied column-wise (across agents, at each time step):

$$\mathbf{H}^{(l)}_{\text{soc}} = \text{softmax}\!\left(\frac{Q_s K_s^\top}{\sqrt{d}}\right) V_s, \quad \text{applied for each } t \in [T]$$

Alternating these two reduces the effective cost to:

$$\mathcal{O}\!\left(N \cdot T^2 + T \cdot N^2\right)$$

For our typical scene sizes this is a **~15× reduction** in attention FLOPs.

### Scene context fusion

The HD map is encoded separately (polylines → PointNet-style MLP), producing context tokens $\mathbf{C} \in \mathbb{R}^{M \times d}$. These are fused via cross-attention after the agent encoder:

$$\mathbf{Z} = \text{CrossAttn}(\mathbf{H}_{\text{soc}}, \mathbf{C})$$

### Multimodal decoder

The decoder produces $K$ future trajectories (modes) per agent via learned mode queries. Each mode query $\mathbf{q}_k$ attends to the fused representation to produce trajectory waypoints:

$$\hat{\mathbf{y}}_k = \text{MLP}\!\left(\text{CrossAttn}(\mathbf{q}_k, \mathbf{Z})\right) \in \mathbb{R}^{T_f \times 2}$$

Mode probabilities are softmax-normalized over a scalar logit head, giving a proper mixture distribution.

---

## Loss function

Training uses the **winner-takes-all** strategy: only the mode closest to ground truth contributes to the regression loss.

$$\mathcal{L} = \underbrace{-\log p_{k^*}}_{\text{classification}} + \underbrace{\sum_{t=1}^{T_f} \left\| \hat{\mathbf{y}}_{k^*}^t - \mathbf{y}^t \right\|_2}_{\text{regression on best mode}}$$

where $k^* = \arg\min_k \text{FDE}(\hat{\mathbf{y}}_k, \mathbf{y})$.

This is critical. Without it, all modes collapse to the mean trajectory — the classic **mode-averaging** failure of trajectory models.

---

## Key implementation lessons

### 1. Agent masking is non-trivial

Real scenes have variable $N$. Padding + masking sounds simple, but you need to propagate masks correctly through both temporal and social attention — especially when computing attention weights, since padded agents must have near-zero contribution to the softmax denominator. A subtle bug here causes the model to "see" phantom agents.

```python
def masked_attention(q, k, v, mask):
    # mask: (B, N) bool, True = valid agent
    scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(q.size(-1))
    # broadcast mask along key dimension
    if mask is not None:
        pad_mask = ~mask.unsqueeze(1).unsqueeze(2)   # (B, 1, 1, N)
        scores = scores.masked_fill(pad_mask, -1e9)
    return torch.softmax(scores, dim=-1) @ v
```

### 2. Coordinate frame matters

We normalize all agent states into an **agent-centric** frame at the last observed timestep — position becomes $(0, 0)$, heading becomes $0$. This dramatically improves generalization because the model doesn't need to learn the same maneuver at every map location.

For the HD map, we transform polyline control points into the same agent-centric frame before PointNet encoding.

### 3. Gradient instability in long temporal sequences

With $T = 50$ input steps, gradients through temporal attention can explode for early timesteps. We found two mitigations:
- **Gradient clipping** at norm 1.0
- **Pre-LN** (pre-layer-normalization) rather than post-LN in every transformer block

Pre-LN made training noticeably more stable — loss curves stop spiking around epoch 5-10.

### 4. Mode collapse in low-data regimes

If your dataset has long-tail maneuvers (lane changes, U-turns), the model tends to allocate all $K$ modes to the dominant straight-ahead motion. Two fixes helped:
- **Mode dropout** during training: randomly zero out the logit for the best mode with probability 0.1, forcing other modes to stay alive
- **Diversity regularization**: penalize the average pairwise distance between predicted modes being too small

---

## Argoverse 2 results

| Model         | minADE₆ ↓ | minFDE₆ ↓ | MR₆ ↓ |
|---------------|-----------|-----------|--------|
| LSTM baseline | 1.14      | 2.62      | 0.47   |
| MTR           | 0.60      | 1.23      | 0.13   |
| **Wayformer** | **0.58**  | **1.16**  | **0.12** |

*Numbers from the original paper (ICRA 2023) on the Argoverse 2 val split.*

**minADE₆** = minimum average displacement error over 6 predicted modes; **minFDE₆** = minimum final displacement error; **MR₆** = miss rate (no mode within 2 m of GT at endpoint).

---

## Production considerations

A research benchmark number and a production model are different things. Some gaps we had to close at Rivian:

- **Latency**: the reference implementation runs ~80 ms on a V100. We needed <20 ms on our compute platform. Optimizations: TorchScript export, reducing $K$ from 64 to 16 modes, INT8 quantization of the scene encoder.

- **Calibration**: the softmax mode probabilities are poorly calibrated out of the box (tends toward uniform). We added temperature scaling calibrated on a held-out val set.

- **Long-horizon stability**: Wayformer predicts 5 s out. Beyond 3 s the prediction variance grows fast. In our planner we weight the short-horizon portion more heavily when computing collision metrics.

---

<div class="insight">
<strong>Key takeaway</strong>
Wayformer's factorized attention is the right abstraction for AV forecasting: it respects the 2-D structure of the problem (time × agents) without quadratic blowup. The architecture is clean enough that you can understand and modify every component, which matters in production where you constantly need to add new agent types or input modalities.
</div>

---

## References

- Nayakanti et al., *Wayformer: Motion Forecasting via Simple & Efficient Attention Networks*, ICRA 2023.
- Argoverse 2 leaderboard: [eval.ai/web/challenges/challenge-page/1710](https://eval.ai/web/challenges/challenge-page/1710/leaderboard)
- [github.com/Manojbhat09/Trajformer](https://github.com/Manojbhat09/Trajformer) — my earlier transformer-based forecasting work at CMU.
