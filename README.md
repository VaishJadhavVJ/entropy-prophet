# Entropy Prophet

**Entropy-based calibration for LLM prediction market forecasting**

Live dashboard: https://entropy-prophet-dashboard.vercel.app

---

## The Problem

LLMs achieve strong forecasting accuracy on prediction market events but consistently underperform market baselines in terms of returns. The gap is calibration — models output overconfident probabilities, especially near event resolution when their knowledge is stale but the market is updating in real time.

## The Hypothesis

Reasoning-step entropy, measured via self-consistency sampling, is a real-time calibration signal. When an LLM's reasoning steps show high variance across multiple runs, the model's confidence is inflated. Compressing that probability toward uncertainty improves calibration without touching accuracy.

## Background

This project is motivated by a key finding in *LLM-as-a-Prophet: Understanding Predictive Intelligence with Prophet Arena* (Yang et al., arXiv:2510.17638): LLMs achieve strong forecasting accuracy on prediction market events but consistently underperform market baselines in terms of returns. The paper identifies several bottlenecks — including slower information aggregation near resolution and miscalibrated confidence.

This project proposes entropy-based recalibration as a mechanism to close that gap. The approach is grounded in prior work on Process Reward Models (PRM) and entropy-based selective step verification in LLM reasoning chains, extended to the prediction market calibration problem.

Evaluation uses [Prophet Arena](https://prophetarena.co) as the live benchmark.

## Architecture

**Layer 1 — Built**
- Internal entropy via GLM-5.1 self-consistency sampling (N=3 runs)
- Shannon entropy computation across reasoning steps
- Entropy-weighted recalibration of output probability

**Layer 2 — In Progress**
- Cross-source disagreement signal (multi-model entropy)
- Price insurgency detection (market surprise calibration)

## Results

First real Brier scores incoming **June 10, 2026** when CPI resolves.

Benchmark: **Prophet Arena** — evaluated on macroeconomic prediction market events (Fed decisions, CPI, central bank rates).

## Stack

| Component | Technology |
|---|---|
| Forecasting agent | Python, GLM-5.1 (ZhipuAI), OpenAI-compatible API |
| Benchmark | Prophet Arena CLI |
| Dashboard | Next.js 16, Recharts, Tailwind CSS |

## Project Structure

```
entropy-prophet/
├── src/entropy_prophet/
│   ├── models.py          # Prediction events, market states, CoT steps
│   ├── entropy.py         # Shannon entropy over reasoning steps
│   ├── recalibration.py   # Entropy-weighted probability recalibration
│   └── prophet_arena.py   # Prophet Arena interface
├── agent.py               # GLM-5.1 self-consistency sampling agent
├── predictions_econ.json  # Latest predictions (read by dashboard)
├── events_econ.json       # Macroeconomic event definitions
├── entropy-prophet-dashboard/  # Next.js live dashboard
└── tests/
```

## References

Yang et al. (2025). *LLM-as-a-Prophet: Understanding Predictive Intelligence with Prophet Arena*. arXiv:2510.17638. University of Chicago / Haifeng Xu et al.

---

**Author:** Vaishnavi Jadhav · [github.com/VaishJadhavVJ](https://github.com/VaishJadhavVJ)
