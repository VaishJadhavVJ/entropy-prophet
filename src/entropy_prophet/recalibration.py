import math
from typing import List, Dict, Any
from .models import MarketState, ReasoningPath
from .entropy import calculate_path_entropy, calculate_ensemble_entropy

def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))

def logit(p: float) -> float:
    # Clamp p to avoid division by zero or log of zero
    p_clamped = max(1e-5, min(1 - 1e-5, p))
    return math.log(p_clamped / (1 - p_clamped))

def recalibrate_probability(
    paths: List[ReasoningPath],
    market: MarketState,
    alpha: float = 0.5,
    beta: float = 0.5,
    liquidity_threshold: float = 50000.0
) -> Dict[str, Any]:
    """
    Recalibrates the raw LLM prediction probability by factoring in:
      1. Average Intra-path Reasoning Entropy (step-by-step uncertainty).
      2. Inter-path Ensemble Entropy (divergence across different reasoning paths).
      3. Prediction Market Liquidity & Price.

    Formula / Strategy:
      - We start with the mean raw prediction from the LLM paths.
      - High reasoning/ensemble entropy implies we should shrink the LLM's probability
        towards the market consensus (the market price) because the LLM is uncertain/divided.
      - If market liquidity is low (less than liquidity_threshold), we trust the market price LESS,
        so we shrink the market's influence and default closer to the LLM's raw average prediction.
      - High market liquidity means the market is robust; if LLM entropy is high, we pull strongly
        towards the market price.
    """
    if not paths:
        return {"recalibrated_probability": market.yes_price, "mean_raw_prob": 0.5, "status": "no_paths"}

    # 1. Compute LLM predictions and uncertainties
    probabilities = [p.final_prediction_probability for p in paths]
    mean_raw_prob = sum(probabilities) / len(probabilities)
    
    # Intra-path entropy (average uncertainty within each chain of thought)
    avg_intra_entropy = sum(calculate_path_entropy(p) for p in paths) / len(paths)
    
    # Inter-path entropy (divergence across reasoning paths)
    inter_path_divergence = calculate_ensemble_entropy(paths)
    
    # Combined LLM Uncertainty (0 to 1 normalized range for calibration scaling)
    # Let's normalize/clamp the combined entropy
    combined_entropy = (avg_intra_entropy * alpha) + (inter_path_divergence * beta)
    
    # 2. Compute Market Weight based on liquidity and spread
    # Liquidity scaling: 0 (no liquidity) to 1 (high liquidity)
    liquidity_factor = market.liquidity_usd / (market.liquidity_usd + liquidity_threshold)
    # Spread penalty: higher spread reduces confidence in market price
    spread_factor = max(0.0, 1.0 - market.spread)
    
    market_confidence = liquidity_factor * spread_factor
    
    # 3. Probability Shrinkage / Interpolation
    # The weight of the market consensus is proportional to LLM uncertainty AND market confidence.
    # If the LLM has high entropy (uncertainty) and the market has high confidence, we trust the market more.
    market_weight = sigmoid(combined_entropy * 8 - 2) * market_confidence
    # Clamp market_weight to [0, 0.9] to avoid ignoring the LLM completely
    market_weight = min(0.9, max(0.0, market_weight))
    
    # Perform interpolation in logit space for better calibration characteristics
    try:
        llm_logit = logit(mean_raw_prob)
        market_logit = logit(market.yes_price)
        
        recalibrated_logit = (1.0 - market_weight) * llm_logit + market_weight * market_logit
        recalibrated_prob = sigmoid(recalibrated_logit)
    except Exception:
        # Fallback to linear interpolation in probability space if logit fails
        recalibrated_prob = (1.0 - market_weight) * mean_raw_prob + market_weight * market.yes_price

    return {
        "event_id": market.event_id,
        "mean_raw_probability": mean_raw_prob,
        "market_price": market.yes_price,
        "recalibrated_probability": recalibrated_prob,
        "intra_path_entropy": avg_intra_entropy,
        "inter_path_entropy": inter_path_divergence,
        "combined_entropy": combined_entropy,
        "market_confidence": market_confidence,
        "market_weight_applied": market_weight
    }
