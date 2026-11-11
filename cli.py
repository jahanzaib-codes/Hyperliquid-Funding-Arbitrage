"""
Hyperliquid-Funding-Arbitrage: Interactive Terminal CLI
Visualizes live funding rates, delta-neutral spreads, and margin risk telemetry.
"""

import asyncio
import argparse
from rich.console import Console
from rich.table import Table
from src.connectors.hyperliquid_client import HyperliquidConnector
from src.connectors.cex_client import CEXConnector
from src.engine.arbitrage_scanner import FundingArbitrageScanner
from src.risk.hedging_manager import MarginHedgingGuardian

console = Console()


async def run_scanner_dashboard():
    console.print("\n[bold cyan]📡 Connecting to Hyperliquid L1 Info & CEX Funding Telemetry...[/bold cyan]\n")
    
    hyper_connector = HyperliquidConnector()
    cex_connector = CEXConnector()
    scanner = FundingArbitrageScanner(min_spread_apr=10.0)

    # Fetch rates
    hyper_rates = await hyper_connector.fetch_funding_rates()
    binance_rates = await cex_connector.fetch_binance_funding()
    bybit_rates = await cex_connector.fetch_bybit_funding()
    
    all_cex_rates = binance_rates + bybit_rates

    # 1. Display Hyperliquid Funding Table
    h_table = Table(title="⚡ Hyperliquid Perpetual Funding Universe", title_style="bold magenta")
    h_table.add_column("Perp Symbol", style="cyan")
    h_table.add_column("Mark Price", justify="right", style="green")
    h_table.add_column("Hourly Rate", justify="right", style="yellow")
    h_table.add_column("Annualized APR", justify="right", style="bold green")
    h_table.add_column("Open Interest", justify="right")

    for r in hyper_rates[:6]:
        h_table.add_row(
            r.symbol,
            f"${r.mark_price:,.2f}",
            f"{r.funding_rate*100:+.4f}%",
            f"{r.annualized_apr:+.2f}%",
            f"${r.open_interest_usd:,.0f}"
        )
    console.print(h_table)
    console.print("\n")

    # 2. Display Arbitrage Opportunities Table
    opportunities = scanner.scan_opportunities(hyper_rates, all_cex_rates)
    
    arb_table = Table(title="💰 Cross-Exchange Delta-Neutral Arbitrage Spreads", title_style="bold green")
    arb_table.add_column("Asset", style="bold cyan")
    arb_table.add_column("Long Venue", style="blue")
    arb_table.add_column("Short Venue", style="magenta")
    arb_table.add_column("Long APR", justify="right")
    arb_table.add_column("Short APR", justify="right")
    arb_table.add_column("Net Spread APR", justify="right", style="bold yellow")
    arb_table.add_column("Daily Yield ($10k)", justify="right", style="bold green")
    arb_table.add_column("Execution Direction", style="dim")

    for opp in opportunities[:6]:
        arb_table.add_row(
            opp.asset,
            opp.long_venue.value,
            opp.short_venue.value,
            f"{opp.long_apr:+.2f}%",
            f"{opp.short_apr:+.2f}%",
            f"[bold green]{opp.net_spread_apr:+.2f}%[/bold green]",
            f"${opp.estimated_daily_yield_usd:.2f}",
            opp.direction.value
        )
    console.print(arb_table)

    if opportunities:
        top = opportunities[0]
        console.print(f"\n[bold green]🎯 Top Delta-Neutral Basis Pick:[/bold green] Short [magenta]{top.short_venue.value}[/magenta] vs Long [blue]{top.long_venue.value}[/blue] on [bold]{top.asset}[/bold] yielding [bold yellow]{top.net_spread_apr}% Net APR[/bold yellow] completely market-neutral!")


def main():
    parser = argparse.ArgumentParser(description="Hyperliquid Funding Arbitrage CLI")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("scan", help="Scan live cross-exchange funding discrepancies")
    
    args = parser.parse_args()
    asyncio.run(run_scanner_dashboard())


if __name__ == "__main__":
    main()
