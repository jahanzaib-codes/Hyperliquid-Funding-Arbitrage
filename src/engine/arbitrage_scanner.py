"""
Hyperliquid-Funding-Arbitrage: Cross-Exchange Delta-Neutral Scanner
Matches perpetual instruments across DEX and CEX venues to calculate pure basis yield.
"""

from typing import List, Dict, Any
from src.models.arbitrage import (
    FundingRateData,
    ArbitrageOpportunity,
    ArbitrageDirection,
    ExchangeVenue
)


class FundingArbitrageScanner:
    """Scans and ranks cross-exchange delta-neutral funding opportunities."""

    def __init__(self, min_spread_apr: float = 12.0, roundtrip_fee_pct: float = 0.08):
        self.min_spread_apr = min_spread_apr
        self.roundtrip_fee_pct = roundtrip_fee_pct  # Amortized taker/maker slippage + fee buffer

    def scan_opportunities(
        self,
        hyper_rates: List[FundingRateData],
        cex_rates: List[FundingRateData]
    ) -> List[ArbitrageOpportunity]:
        """Compares Hyperliquid funding rates against Binance/Bybit rates."""
        opportunities: List[ArbitrageOpportunity] = []
        cex_map: Dict[str, FundingRateData] = {r.symbol: r for r in cex_rates}

        for h_rate in hyper_rates:
            if h_rate.symbol not in cex_map:
                continue

            c_rate = cex_map[h_rate.symbol]
            asset_name = h_rate.symbol.replace("-PERP", "")

            # Case 1: Hyperliquid APR is higher than CEX (Short Hyperliquid, Long CEX)
            if h_rate.annualized_apr > c_rate.annualized_apr:
                gross_spread = h_rate.annualized_apr - c_rate.annualized_apr
                net_apr = gross_spread - (self.roundtrip_fee_pct * 12.0) # Amortized annual fee
                
                if net_apr >= self.min_spread_apr:
                    daily_yield = (net_apr / 365.0 / 100.0) * 10000.0 # On $10,000 size
                    opportunities.append(ArbitrageOpportunity(
                        asset=asset_name,
                        long_venue=c_rate.venue,
                        short_venue=ExchangeVenue.HYPERLIQUID,
                        long_apr=c_rate.annualized_apr,
                        short_apr=h_rate.annualized_apr,
                        net_spread_apr=round(net_apr, 2),
                        direction=ArbitrageDirection.LONG_CEX_SHORT_HYPER,
                        estimated_daily_yield_usd=round(daily_yield, 2),
                        recommended_size_usd=15000.0,
                        confidence="HIGH"
                    ))

            # Case 2: CEX APR is higher than Hyperliquid (Short CEX, Long Hyperliquid)
            elif c_rate.annualized_apr > h_rate.annualized_apr:
                gross_spread = c_rate.annualized_apr - h_rate.annualized_apr
                net_apr = gross_spread - (self.roundtrip_fee_pct * 12.0)
                
                if net_apr >= self.min_spread_apr:
                    daily_yield = (net_apr / 365.0 / 100.0) * 10000.0
                    opportunities.append(ArbitrageOpportunity(
                        asset=asset_name,
                        long_venue=ExchangeVenue.HYPERLIQUID,
                        short_venue=c_rate.venue,
                        long_apr=h_rate.annualized_apr,
                        short_apr=c_rate.annualized_apr,
                        net_spread_apr=round(net_apr, 2),
                        direction=ArbitrageDirection.LONG_HYPER_SHORT_CEX,
                        estimated_daily_yield_usd=round(daily_yield, 2),
                        recommended_size_usd=15000.0,
                        confidence="MEDIUM"
                    ))

        # Sort descending by highest Net APR
        return sorted(opportunities, key=lambda x: x.net_spread_apr, reverse=True)
