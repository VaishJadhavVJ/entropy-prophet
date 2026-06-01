# Interface with Prophet Arena simulation framework and fetch market details.
import math
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class MarketLiquidity(BaseModel):
    volume: float = Field(default=0.0, description="Total traded volume of the market")
    open_interest: float = Field(default=0.0, description="Current open interest")
    bid_ask_spread: float = Field(default=0.05, description="Spread as percentage of current mid-price")
    depth_bids: float = Field(default=1000.0, description="Sum of bid sizes near the mid price")
    depth_asks: float = Field(default=1000.0, description="Sum of ask sizes near the mid price")

    @property
    def liquidity_score(self) -> float:
        """
        Calculates a normalized liquidity score between 0.0 and 1.0.
        High volume & high open interest, low bid-ask spread = High liquidity (1.0).
        """
        if self.volume <= 0:
            return 0.0
            
        # Logarithmic scaling for volume
        vol_score = min(1.0, math.log10(self.volume + 1) / 6.0) # Assume 1,000,000 is maximum scaling
        
        # Spread impact (lower spread -> higher liquidity)
        spread_score = max(0.0, 1.0 - (self.bid_ask_spread / 0.20)) # Max penalty at 20% spread
        
        return 0.6 * vol_score + 0.4 * spread_score

class ProphetArenaMarket(BaseModel):
    market_id: str
    question: str
    yes_price: float
    no_price: float
    liquidity: MarketLiquidity
    is_resolved: bool = False
    resolution: Optional[str] = None

class ProphetArenaClient:
    """
    Mock/Interface client for interacting with Prophet Arena contracts, 
    matching prediction market schemas.
    """
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or "https://api.prophetarena.xyz"

    def get_market(self, market_id: str) -> ProphetArenaMarket:
        """
        Fetches prediction market data including prices and liquidity metrics.
        Returns mock data if not connected to active endpoint.
        """
        # Return mock structures reflecting realistic Prophet Arena market parameters
        if "rate-cut" in market_id:
            return ProphetArenaMarket(
                market_id=market_id,
                question="Will the Federal Reserve cut rates by 25bps or more in September?",
                yes_price=0.68,
                no_price=0.32,
                liquidity=MarketLiquidity(
                    volume=245000.0,
                    open_interest=85000.0,
                    bid_ask_spread=0.015,
                    depth_bids=12500.0,
                    depth_asks=14000.0
                )
            )
        elif "election" in market_id:
            return ProphetArenaMarket(
                market_id=market_id,
                question="Will candidates participate in at least three televised debates?",
                yes_price=0.42,
                no_price=0.58,
                liquidity=MarketLiquidity(
                    volume=12000.0,
                    open_interest=3200.0,
                    bid_ask_spread=0.065,
                    depth_bids=1500.0,
                    depth_asks=1200.0
                )
            )
        else:
            # Default fallback low-liquidity market
            return ProphetArenaMarket(
                market_id=market_id,
                question=f"Will custom prediction event {market_id} resolve YES?",
                yes_price=0.50,
                no_price=0.50,
                liquidity=MarketLiquidity(
                    volume=500.0,
                    open_interest=200.0,
                    bid_ask_spread=0.15,
                    depth_bids=100.0,
                    depth_asks=100.0
                )
            )

    def fetch_all_markets(self) -> List[ProphetArenaMarket]:
        return [
            self.get_market("fed-rate-cut-sep"),
            self.get_market("us-election-debates"),
            self.get_market("custom-test-event")
        ]
