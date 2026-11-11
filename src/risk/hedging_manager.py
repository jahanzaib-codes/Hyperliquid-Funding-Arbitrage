"""
Hyperliquid-Funding-Arbitrage: Dynamic Risk & Margin Guardian
Maintains delta neutrality, audits collateral ratios, and prevents cross-exchange liquidation.
"""

from typing import Dict, Any, List
from src.models.arbitrage import DeltaNeutralPosition, MarginHealthStatus, ExchangeVenue


class MarginHedgingGuardian:
    """Safeguards delta-neutral positions against short squeeze liquidations."""

    def __init__(self, target_margin_ratio: float = 0.35, liquidation_warning_threshold: float = 0.15):
        self.target_margin_ratio = target_margin_ratio
        self.liquidation_warning_threshold = liquidation_warning_threshold

    def audit_position_health(self, position: DeltaNeutralPosition) -> List[MarginHealthStatus]:
        """Audits collateral ratios on both long and short venues."""
        reports = []

        # Long leg margin health
        long_ratio = position.long_margin_ratio
        long_safe = long_ratio > self.liquidation_warning_threshold
        long_rebalance = long_ratio < 0.22

        reports.append(MarginHealthStatus(
            venue=position.long_venue,
            total_margin_usd=round(position.notional_size_usd * long_ratio, 2),
            maintenance_margin_req_usd=round(position.notional_size_usd * 0.05, 2),
            free_collateral_usd=round(position.notional_size_usd * (long_ratio - 0.05), 2),
            margin_ratio_pct=round(long_ratio * 100.0, 1),
            is_safe=long_safe,
            requires_rebalance=long_rebalance
        ))

        # Short leg margin health
        short_ratio = position.short_margin_ratio
        short_safe = short_ratio > self.liquidation_warning_threshold
        short_rebalance = short_ratio < 0.22

        reports.append(MarginHealthStatus(
            venue=position.short_venue,
            total_margin_usd=round(position.notional_size_usd * short_ratio, 2),
            maintenance_margin_req_usd=round(position.notional_size_usd * 0.05, 2),
            free_collateral_usd=round(position.notional_size_usd * (short_ratio - 0.05), 2),
            margin_ratio_pct=round(short_ratio * 100.0, 1),
            is_safe=short_safe,
            requires_rebalance=short_rebalance
        ))

        return reports
