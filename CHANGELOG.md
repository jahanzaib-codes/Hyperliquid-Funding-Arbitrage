# 📝 Changelog

All notable changes to **Hyperliquid-Funding-Arbitrage** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-11
### Added
- Real-time funding rate connector for Hyperliquid L1 DEX info API (`metaAndAssetCtxs`).
- Centralized exchange (CEX) connectors for Binance Futures and Bybit perpetuals.
- Cross-exchange delta-neutral basis scanner calculating fee-amortized Net Spread APR.
- Cross-margin liquidation guardian and auto-rebalancing risk manager.
- Rich terminal CLI dashboard with live funding tables and arbitrage rankings (`python cli.py scan`).
- Background daemon runner with continuous opportunity alerts.
- Containerized Docker and docker-compose deployment.
- GitHub Actions CI/CD matrix and open-source governance guidelines.
