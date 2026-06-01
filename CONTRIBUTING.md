# Contributing

Thanks for helping improve astock.

## Setup

```bash
git clone https://github.com/youmengde/astock.git
cd astock
python3 -m pip install -e ".[dev]"
```

## Checks

Run these before opening a PR:

```bash
python3 -m ruff check src tests
python3 -m pytest
```

## Testing rules

- Do not call real market data providers in unit tests.
- Mock AKShare responses with small DataFrames.
- Keep CLI tests deterministic.

## Pull requests

Please include:

- A short explanation of the change
- Tests for behavior changes
- README updates if user-facing commands change
