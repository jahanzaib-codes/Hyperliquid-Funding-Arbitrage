"""
Hyperliquid-Funding-Arbitrage: Data Models
Defines Pydantic data schemas for cross-exchange funding telemetry,
delta-neutral yield calculation, and portfolio margin health.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ExchangeVenue(str, Enum):
    HYPERLIQUID = "HYPERLIQUID"
    BINANCE = "BINANCE"
    BYBIT = "BYBIT"


class ArbitrageDirection(str, Enum):
    LONG_CEX_SHORT_HYPER = "LONG_CEX_SHORT_HYPER"
    LONG_HYPER_SHORT_CEX = "LONG_HYPER_SHORT_CEX"


class FundingRateData(BaseModel):
    venue: ExchangeVenue
    symbol: str
    mark_price: float = Field(..., gt=0.0)
    funding_rate: float
    funding_interval_hours: int = Field(default=1)
    annualized_apr: float
    open_interest_usd: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class ArbitrageOpportunity(BaseModel):
    asset: str
    long_venue: ExchangeVenue
    short_venue: ExchangeVenue
    long_apr: float
    short_apr: float
    net_spread_apr: float = Field(..., description="Annualized net percentage yield after fee amortization")
    direction: ArbitrageDirection
    liquidity_score: float = Field(default=1.0, ge=0.0, le=1.0)
    estimated_daily_yield_usd: float = Field(default=0.0)
    recommended_size_usd: float = Field(default=10000.0)
    confidence: str = Field(default="HIGH")


class DeltaNeutralPosition(BaseModel):
    position_id: str
    symbol: str
    long_venue: ExchangeVenue
    short_venue: ExchangeVenue
    entry_basis: float
    notional_size_usd: float
    accumulated_funding_usd: float = Field(default=0.0)
    current_net_pnl_usd: float = Field(default=0.0)
    long_margin_ratio: float = Field(default=0.35)
    short_margin_ratio: float = Field(default=0.35)
    status: str = Field(default="ACTIVE")


class MarginHealthStatus(BaseModel):
    venue: ExchangeVenue
    total_margin_usd: float
    maintenance_margin_req_usd: float
    free_collateral_usd: float
    margin_ratio_pct: float
    is_safe: bool
    requires_rebalance: bool
