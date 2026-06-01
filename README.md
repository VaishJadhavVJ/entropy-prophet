# entropy-prophet

`entropy-prophet` is a proof-of-concept system that tests whether **reasoning-step entropy** in Large Language Model (LLM) chain-of-thought (CoT), combined with **prediction market liquidity**, can be used to recalibrate the LLM's forecast probabilities on prediction market events.

The predictions are evaluated against events from **Prophet Arena** (or its mock data representations).

## Core Idea
1. **Reasoning-Step Entropy (CoT Entropy):** 
   When an LLM generates a Chain of Thought (CoT), we analyze its token or reasoning-step transitions. Higher entropy across multiple generated paths or during step-by-step reasoning denotes a lack of confidence or higher epistemic uncertainty.
2. **Market Liquidity:** 
   Prediction markets provide strong consensus signals, but low-liquidity markets might be highly volatile or mispriced. High liquidity represents robust consensus.
3. **Probability Recalibration:** 
   We combine the LLM's subjective forecast confidence (and its structural reasoning entropy) with market-state metrics (like depth, volume, or spread) to perform Bayesian or log-odds recalibration of the forecast probability, producing a more accurate and robust probability estimate.

## Project Structure
- `src/entropy_prophet/`: Core Python library.
  - `models.py`: Data models for Prediction Events, Market States, and CoT steps.
  - `entropy.py`: Logic for calculating reasoning-step and token transitions entropy.
  - `recalibration.py`: Algorithms combining entropy and liquidity to produce recalibrated probabilities.
  - `prophet_arena.py`: Interface to load/mock prediction market data from Prophet Arena.
- `tests/`: Automated unit tests.
- `demo.py`: Executable workflow showcasing the pipeline.
