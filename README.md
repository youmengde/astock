# astock

A-share stock terminal toolkit — real-time quotes, screening, ranking, and script-friendly JSON/CSV output.

<p align="center">
  <img src="https://img.shields.io/github/license/youmengde/astock" />
  <img src="https://img.shields.io/github/actions/workflow/status/youmengde/astock/ci.yml?branch=master" />
</p>

## Features

- Real-time A-share quotes from the terminal
- Stock screening by PE, PB, turnover, price change, and market cap
- Rankings for gainers, turnover, PE/PB, volume, and market cap
- Major China index overview
- Rich terminal tables plus JSON/CSV output for scripts
- No data API key required

## Install

This project is not published to PyPI yet. Install from source:

```bash
git clone https://github.com/youmengde/astock.git
cd astock
python3 -m pip install -e .
```

For development:

```bash
python3 -m pip install -e ".[dev]"
```

## Usage

### Get a stock quote

```bash
astock quote 000001
astock quote 000001 --format json
```

### View major indices

```bash
astock index
astock index --format csv
```

### Screen stocks

```bash
# Low PE, high turnover
astock screen --max-pe 30 --min-turnover 3 -n 10

# Save results as CSV
astock screen --max-pe 30 --min-turnover 3 --format csv --output stocks.csv
```

### Rankings

```bash
# Top gainers
astock top change_pct

# Lowest PE
astock top pe --asc -n 10

# Largest market cap as JSON
astock top total_mv --format json
```

## Output formats

All data commands support:

```bash
--format table  # default
--format json
--format csv
--output FILE   # json/csv only
```

## Data Source

Stock data is provided by [AKShare](https://github.com/akfamily/akshare) via public market data sources such as East Money (东方财富). Availability depends on the upstream data provider and network connectivity.

## Disclaimer

This tool is for information and research only. It is not financial advice. Market data may be delayed, incomplete, or unavailable. Verify data before making investment decisions.

## Development

```bash
python3 -m pip install -e ".[dev]"
python3 -m ruff check src tests
python3 -m pytest
```

Tests mock the data provider and do not depend on real market data.

## License

[MIT](LICENSE)
