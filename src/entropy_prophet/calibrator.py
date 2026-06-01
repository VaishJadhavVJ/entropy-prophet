# Probability Recalibrator combining Chain-of-Thought entropy and Market Liquidity
import math
from typing import Dict, Any
from pydantic import BaseModel
from .chain_of_thought import CoTAnalysis
from .prophet_client import ProphetArenaMarket

class CalibrationResult(BaseModel):
    original_forecast: float
    recalibrated_forecast: float
    market_price: float
    mean_entropy: float
    liquidity_score: float
    entropy_adjustment: float
    market_influence_weight: float
    confidence_interval: tuple[float, float]

class ProphetCalibrator:
    """
    Recalibrates LLM forecast probabilities using:
    - Reasoning-step entropy (how certain/uncertain the LLM's internal thinking was)
    - Market liquidity (how efficient and well-capitalized the prediction market is)
    
    If reasoning entropy is HIGH:
    - The LLM's explicit forecast is likely overconfident/noisier. We should pull the
      forecast back towards the market price OR 0.5 (maximum uncertainty).
      
    If market liquidity is HIGH:
    - The market price itself contains highly robust collective information. We should
      place more weight on the market price as an anchor.
      
    If reasoning entropy is LOW and market liquidity is LOW:
    - The LLM possesses high reasoning coherence relative to a weak, thin market. 
      We should preserve or even boost the LLM's original forecast over market price.
    """
    def __init__(self, base_entropy_threshold: float = 0.5):
        self.base_entropy_threshold = base_entropy_threshold

    def recalibrate(
        self, 
        cot_analysis: CoTAnalysis, 
        market: ProphetArenaMarket
    ) -> CalibrationResult:
        original_p = cot_analysis.final_raw_probability
        market_p = market.yes_price
        
        # Calculate scores
        mean_entropy = cot_analysis.mean_entropy
        liq_score = market.liquidity.liquidity_score
        
        # Determine weight to give to market price vs LLM forecast
        # Formula: weight of market increases with market liquidity AND increases with reasoning entropy
        # When reasoning entropy is high, LLM is confused -> trust market more.
        # When liquidity is high, market is highly efficient -> trust market more.
        
        # Normalize entropy weight (arbitrary scaling)
        entropy_factor = min(1.0, mean_entropy / 1.5)
        
        # Market Influence Weight: balance of liquidity & LLM self-doubt
        # Base weight starts at 0.3, scales up to 0.9 based on conditions
        market_influence_weight = 0.3 + (0.4 * liq_score) + (0.2 * entropy_factor)
        market_influence_weight = min(0.95, max(0.05, market_influence_weight))
        
        # Calculate adjustment towards the market price
        # recalibrated_p = (1 - weight) * original_p + weight * market_p
        recalibrated_p = (1.0 - market_influence_weight) * original_p + market_influence_weight * market_p
        
        # Add small entropy-scaling smoothing (towards 0.5) if entropy is exceptionally high
        # to counteract global overconfidence (calibration drift)
        entropy_adjustment = 0.0
        if mean_entropy > self.base_entropy_threshold:
            # Overconfidence penalty: pull closer to 50%
            pull_to_fifty = (mean_entropy - self.base_entropy_threshold) * 0.1
            entropy_adjustment = (0.5 - recalibrated_p) * min(0.3, pull_to_fifty)
            recalibrated_p += entropy_adjustment
            
        # Ensure boundaries
        recalibrated_p = min(0.99, max(0.01, recalibrated_p))
        
        # Confidence interval approximation
        # Spreads with higher entropy and lower liquidity
        interval_width = 0.05 + (0.15 * mean_entropy) + (0.10 * (1.0 - liq_score))
        low_bound = max(0.01, recalibrated_p - interval_width)
        high_bound = min(0.99, recalibrated_p + interval_width)
        
        return CalibrationResult(
            original_forecast=original_p,
            recalibrated_forecast=round(recalibrated_p, 4),
            market_price=market_p,
            mean_entropy=round(mean_entropy, 4),
            liquidity_score=round(liq_score, 4),
            entropy_adjustment=round(entropy_adjustment, 4),
            market_influence_weight=round(market_influence_weight, 4),
            confidence_interval=(round(low_bound, 4), round(high_bound, 4))
        )
