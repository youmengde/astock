"""Rich terminal display helpers."""

from __future__ import annotations

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

DISPLAY_COLUMNS = {
    "code": "代码",
    "name": "名称",
    "price": "最新价",
    "change_pct": "涨跌%",
    "change": "涨跌额",
    "volume": "成交量",
    "amount": "成交额",
    "turnover": "换手率",
    "pe": "PE",
    "pb": "PB",
    "total_mv": "总市值",
    "circ_mv": "流通市值",
    "amplitude": "振幅",
    "high": "最高",
    "low": "最低",
    "open": "今开",
    "pre_close": "昨收",
}

DEFAULT_COLUMNS = ["code", "name", "price", "change_pct", "turnover", "pe", "pb", "total_mv"]


def _to_float(val) -> float | None:
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _fmt_val(col: str, val) -> str:
    """Format a cell value for display."""
    v = _to_float(val)
    if v is None:
        return "-" if pd.isna(val) else str(val)
    if col in ("change_pct", "turnover", "amplitude"):
        return f"{v:.2f}%"
    if col in ("price", "change", "high", "low", "open", "pre_close"):
        return f"{v:.2f}"
    if col in ("pe", "pb"):
        return f"{v:.1f}" if v > 0 else "-"
    if col in ("total_mv", "circ_mv"):
        if v >= 1e12:
            return f"{v / 1e12:.1f}万亿"
        if v >= 1e8:
            return f"{v / 1e8:.1f}亿"
        return f"{v:.0f}"
    if col in ("amount",):
        if v >= 1e8:
            return f"{v / 1e8:.1f}亿"
        return f"{v:.0f}万"
    if col in ("volume",):
        if v >= 1e8:
            return f"{v / 1e8:.1f}亿"
        if v >= 1e4:
            return f"{v / 1e4:.1f}万"
        return f"{v:.0f}"
    return str(val)


def _change_style(val) -> str:
    """Return rich style based on change value."""
    v = _to_float(val)
    if v is None:
        return ""
    if v > 0:
        return "bold red"
    if v < 0:
        return "bold green"
    return ""


def _style_text(text: str, style: str) -> str:
    return f"[{style}]{text}[/{style}]" if style else text


def show_table(df: pd.DataFrame, title: str = "", columns: list[str] | None = None):
    """Render a DataFrame as a Rich table."""
    if df.empty:
        console.print("[yellow]暂无数据[/yellow]")
        return

    cols = columns or [c for c in DEFAULT_COLUMNS if c in df.columns]
    table = Table(title=title, show_lines=False, pad_edge=False)
    table.add_column("#", style="dim", width=4)

    for col in cols:
        header = DISPLAY_COLUMNS.get(col, col)
        table.add_column(header, justify="right" if col not in ("code", "name") else "left")

    for i, (_, row) in enumerate(df.iterrows(), 1):
        values = []
        for col in cols:
            val = row.get(col)
            text = _fmt_val(col, val)
            if col == "change_pct":
                text = _style_text(text, _change_style(val))
            values.append(text)
        table.add_row(str(i), *values)

    console.print(table)


def show_quote(code: str, df: pd.DataFrame):
    """Show detailed quote for a single stock."""
    if df.empty:
        console.print(f"[yellow]未找到股票 {code}[/yellow]")
        return
    row = df.iloc[0]
    console.print()
    style = _change_style(row.get("change_pct", 0))
    price = _style_text(_fmt_val("price", row.get("price")), style)
    change_pct = _style_text(_fmt_val("change_pct", row.get("change_pct")), style)
    console.print(f"  [bold]{row.get('name', '')}[/bold]  {row.get('code', '')}", style="bold")
    console.print(f"  最新价: {price}  涨跌幅: {change_pct}")
    console.print(f"  今开: {_fmt_val('open', row.get('open'))}  最高: {_fmt_val('high', row.get('high'))}  最低: {_fmt_val('low', row.get('low'))}  昨收: {_fmt_val('pre_close', row.get('pre_close'))}")
    console.print(f"  成交量: {_fmt_val('volume', row.get('volume'))}  成交额: {_fmt_val('amount', row.get('amount'))}  换手率: {_fmt_val('turnover', row.get('turnover'))}")
    console.print(f"  PE: {_fmt_val('pe', row.get('pe'))}  PB: {_fmt_val('pb', row.get('pb'))}  总市值: {_fmt_val('total_mv', row.get('total_mv'))}")
    console.print()
