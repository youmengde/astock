# astock

A-share stock terminal toolkit — real-time quotes, screening & ranking from the command line.

<p align="center">
  <img src="https://img.shields.io/pypi/v/astock" />
  <img src="https://img.shields.io/pypi/pyversions/astock" />
  <img src="https://img.shields.io/github/license/youmengde/astock" />
</p>

## Features

- **Real-time quotes** — fetch live A-share stock data from the terminal
- **Stock screening** — filter by PE, PB, turnover, market cap, and more
- **Ranking** — top gainers, lowest PE, highest turnover, etc.
- **Index overview** — SSE, SZSE, ChiNext at a glance
- **Beautiful output** — Rich-powered terminal tables with color-coded changes

## Install

```bash
pip install astock
```

## Usage

### Get a stock quote

```bash
astock quote 000001
```

### View major indices

```bash
astock index
```

### Screen stocks

```bash
# Low PE, high turnover
astock screen --max-pe 30 --min-turnover 3 -n 10

# Positive change, reasonable PB
astock screen --min-change 0 --max-pb 5 -n 15
```

### Rankings

```bash
# Top gainers
astock top change_pct

# Lowest PE (ascending)
astock top pe --asc -n 10

# Largest market cap
astock top total_mv

# Most active
astock top amount -n 15
```

## Screenshots

```
$ astock top change_pct -n 5

          涨跌幅排行 (降序)
┌────┬──────┬──────────┬────────┬────────┬────────┐
│ #  │ 代码 │ 名称     │ 最新价 │ 涨跌%  │ 换手率 │
├────┼──────┼──────────┼────────┼────────┼────────┤
│ 1  │ 301… │ 新股     │  45.20 │ 20.00% │ 55.32% │
│ 2  │ 688… │ 科创股   │  32.10 │ 19.98% │ 42.15% │
└────┴──────┴──────────┴────────┴────────┴────────┘
```

## Data Source

Stock data is provided by [AKShare](https://github.com/akfamily/akshare) via East Money (东方财富). No API key required.

## Development

```bash
git clone https://github.com/youmengde/astock.git
cd astock
pip install -e ".[dev]"
```

## License

[MIT](LICENSE)
