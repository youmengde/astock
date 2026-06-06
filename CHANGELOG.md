# Changelog

## v0.1.1 — 2026-06-06

- Added `astock search` to find stocks by name or code prefix.
- Added `astock history` for OHLCV history with date range, period and adjust options.
- Added `astock watch` group (add / remove / list) for a local watchlist persisted in `~/.astock/watchlist.json`.
- Quote, screen, top, history and watch list commands all support `--format table|json|csv` and `--output FILE`.

## v0.1.0 — 2026-06-02

- Added JSON/CSV output for data commands.
- Improved market data error handling.
- Added numeric-safe filtering and ranking.
- Added tests, CI, and contributor documentation.
