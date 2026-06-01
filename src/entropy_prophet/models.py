# Models representing markets, predictions, and Chain-of-Thought states
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MarketState(BaseModel):
    """Represents the current state of a prediction market event."""
    event_id: str
    title: str
    yes_price: float = Field(..., description="Current market price for 'YES' outcome, between 0.0 and 1.0")
    liquidity_usd: float = Field(..., description="Total liquidity or volume in USD")
    spread: float = Field(..., description="Bid-ask spread, between 0.0 and 1.0")
    volume_24h: float = Field(default=0.0, description="24-hour trading volume in USD")

class CoTStep(BaseModel):
    """Represents a single step in a Chain-of-Thought reasoning path."""
    step_number: int
    content: str
    entropy: float = Field(..., description="The average Shannon entropy of the tokens generated in this step")
    confidence: Optional[float] = Field(None, description="Optional probability or confidence rating self-reported in this step")

class ReasoningPath(BaseModel):
    """Represents one complete Chain-of-Thought generation path (sample) for a prediction."""
    path_id: str
    steps: List[CoTStep]
    final_prediction_probability: float = Field(..., description="The final predicted probability of 'YES' output by the model (0.0 to 1.0)")
    raw_generation: str

class PredictionRequest(BaseModel):
    """Represents the prompt/event details passed to the LLM for prediction."""
    event_id: str
    prompt: str
    market_state: MarketState
