"""
Hyperliquid-Funding-Arbitrage: Daemon Entrypoint
Continuous background monitoring daemon for delta-neutral funding rate discrepancies.
"""

import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from src.connectors.hyperliquid_client import HyperliquidConnector
from src.connectors.cex_client import CEXConnector
from src.engine.arbitrage_scanner import FundingArbitrageScanner

load_dotenv()
console = Console()


async def main():
    min_spread = float(os.getenv("MIN_NET_APR_THRESHOLD", "12.0"))
    console.print("\n" + "="*60)
    console.print("[bold cyan]🚀 Hyperliquid Delta-Neutral Arbitrage Daemon Active[/bold cyan]")
    console.print(f"  Minimum Spread Filter: [green]{min_spread}% Net APR[/green]")
    console.print(f"  Monitoring Venues: [magenta]Hyperliquid L1 DEX, Binance Futures, Bybit Perps[/magenta]")
    console.print("="*60 + "\n")

    hyper = HyperliquidConnector()
    cex = CEXConnector()
    scanner = FundingArbitrageScanner(min_spread_apr=min_spread)

    try:
        while True:
            hyper_rates = await hyper.fetch_funding_rates()
            binance_rates = await cex.fetch_binance_funding()
            bybit_rates = await cex.fetch_bybit_funding()

            opps = scanner.scan_opportunities(hyper_rates, binance_rates + bybit_rates)
            if opps:
                top = opps[0]
                console.print(f"[bold green]🔔 High-Yield Opportunity:[/bold green] Short [magenta]{top.short_venue.value}[/magenta] vs Long [blue]{top.long_venue.value}[/blue] on [bold]{top.asset}[/bold] -> [bold yellow]{top.net_spread_apr}% Net APR[/bold yellow] (Daily: ${top.estimated_daily_yield_usd:.2f} on $10k)")
            else:
                console.print("[dim]Scanning 100+ perpetual markets... No spread exceeding threshold currently.[/dim]")
            
            await asyncio.sleep(60)
    except (asyncio.CancelledError, KeyboardInterrupt):
        console.print("\n[yellow]Daemon shutting down cleanly.[/yellow]")


if __name__ == "__main__":
    asyncio.run(main())
