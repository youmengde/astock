"""CLI entry point for astock."""

from __future__ import annotations

from pathlib import Path

import click
import pandas as pd

from .data import DataFetchError, get_history, get_index_quote, get_realtime_quotes, get_sector_quotes, get_stock_quote, rank_by, rank_sectors, screener, search_stocks
from .display import console, show_quote, show_table
from .watchlist import add as wl_add, list_codes as wl_list, remove as wl_remove

OutputFormat = click.Choice(["table", "json", "csv"])


def _write_or_print(content: str, output: str | None):
    if output:
        Path(output).write_text(content, encoding="utf-8")
        console.print(f"[green]已写入 {output}[/green]")
    else:
        click.echo(content)


def _emit_dataframe(
    df: pd.DataFrame,
    fmt: str,
    output: str | None,
    title: str = "",
    columns: list[str] | None = None,
):
    if fmt == "json":
        _write_or_print(df.to_json(orient="records", force_ascii=False, indent=2), output)
        return
    if fmt == "csv":
        _write_or_print(df.to_csv(index=False), output)
        return
    if output:
        raise click.ClickException("--output only supports --format json or --format csv")
    show_table(df, title=title, columns=columns)


def _fetch_or_fail(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except DataFetchError as exc:
        raise click.ClickException(str(exc)) from exc


@click.group()
@click.version_option()
def cli():
    """A-share stock terminal toolkit — quotes, screening & ranking."""
    pass


@cli.command()
@click.argument("code")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def quote(code: str, fmt: str, output: str | None):
    """Show real-time quote for a stock.

    \b
    $ astock quote 000001
    $ astock quote 000001 --format json
    """
    with console.status("获取行情数据..."):
        stock = _fetch_or_fail(get_stock_quote, code)
    if fmt == "table":
        if output:
            raise click.ClickException("--output only supports --format json or --format csv")
        show_quote(code, stock)
    else:
        _emit_dataframe(stock, fmt, output)


@cli.command()
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def index(fmt: str, output: str | None):
    """Show major index quotes (上证、深证、创业板)."""
    with console.status("获取指数数据..."):
        df = _fetch_or_fail(get_index_quote)
    _emit_dataframe(df, fmt, output, title="主要指数", columns=["code", "name", "price", "change_pct", "amount"])


@cli.command()
@click.option("--min-pe", type=float, help="最小市盈率")
@click.option("--max-pe", type=float, help="最大市盈率")
@click.option("--min-pb", type=float, help="最小市净率")
@click.option("--max-pb", type=float, help="最大市净率")
@click.option("--min-turnover", type=float, help="最小换手率(%)")
@click.option("--min-change", type=float, help="最小涨跌幅(%)")
@click.option("--max-change", type=float, help="最大涨跌幅(%)")
@click.option("--min-mv", type=float, help="最小总市值(元)")
@click.option("--max-mv", type=float, help="最大总市值(元)")
@click.option("-n", "--limit", type=int, default=20, help="返回数量 (默认 20)")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def screen(fmt: str, output: str | None, **kwargs):
    """Screen stocks by financial metrics.

    \b
    $ astock screen --max-pe 30 --min-turnover 3 -n 10
    $ astock screen --max-pe 30 --format csv --output stocks.csv
    """
    limit = kwargs.pop("limit", 20)
    with console.status("筛选中..."):
        df = _fetch_or_fail(screener, limit=limit, **{k: v for k, v in kwargs.items() if v is not None})
    _emit_dataframe(df, fmt, output, title="筛选结果")


@cli.command()
@click.argument("metric", type=click.Choice(["change_pct", "turnover", "pe", "pb", "total_mv", "amount", "volume"]))
@click.option("--asc", "ascending", is_flag=True, help="升序排列 (默认降序)")
@click.option("-n", "--limit", type=int, default=20, help="返回数量 (默认 20)")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def top(metric: str, ascending: bool, limit: int, fmt: str, output: str | None):
    """Rank stocks by a metric.

    \b
    $ astock top change_pct          # 涨幅排行
    $ astock top pe --asc -n 10      # PE 最低 10 只
    $ astock top total_mv --format json
    """
    with console.status("排序中..."):
        df = _fetch_or_fail(rank_by, metric=metric, ascending=ascending, limit=limit)
    metric_names = {
        "change_pct": "涨跌幅", "turnover": "换手率", "pe": "PE",
        "pb": "PB", "total_mv": "总市值", "amount": "成交额", "volume": "成交量",
    }
    direction = "升序" if ascending else "降序"
    _emit_dataframe(df, fmt, output, title=f"{metric_names.get(metric, metric)}排行 ({direction})")


@cli.command()
@click.argument("keyword")
@click.option("-n", "--limit", type=int, default=20, help="返回数量 (默认 20)")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def search(keyword: str, limit: int, fmt: str, output: str | None):
    """Search stocks by name or code prefix.

    \b
    $ astock search 茅台
    $ astock search 60051
    $ astock search 银行 --format json
    """
    with console.status("搜索中..."):
        df = _fetch_or_fail(search_stocks, keyword=keyword, limit=limit)
    _emit_dataframe(df, fmt, output, title=f"搜索: {keyword}")


@cli.command()
@click.argument("code")
@click.option("--start", help="开始日期 YYYY-MM-DD (默认: 90 天前)")
@click.option("--end", help="结束日期 YYYY-MM-DD (默认: 今日)")
@click.option("--period", type=click.Choice(["daily", "weekly", "monthly"]), default="daily", help="K线周期")
@click.option("--adjust", type=click.Choice(["qfq", "hfq", "none"]), default="qfq", help="复权方式")
@click.option("-n", "--limit", type=int, default=30, help="返回最近 N 条 (表格模式)")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def history(code: str, start: str | None, end: str | None, period: str, adjust: str, limit: int, fmt: str, output: str | None):
    """Show historical OHLCV prices for a stock.

    \b
    $ astock history 000001
    $ astock history 000001 --start 2024-01-01 --end 2024-12-31
    $ astock history 000001 --start 2024-01-01 --format csv -o prices.csv
    """
    adjust_arg = "" if adjust == "none" else adjust
    with console.status("获取历史行情..."):
        df = _fetch_or_fail(get_history, code=code, start=start, end=end, period=period, adjust=adjust_arg)
    if fmt == "table" and not df.empty:
        df = df.tail(limit)
    _emit_dataframe(df, fmt, output, title=f"{code} 历史行情 ({period})")


@cli.group()
def sector():
    """Industry sector / board quotes (申万行业)."""
    pass


SECTOR_METRICS = click.Choice(["change_pct", "turnover", "total_mv", "up_count", "down_count"])


@sector.command("list")
@click.option("-n", "--limit", type=int, default=30, help="返回数量 (默认 30)")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def sector_list(limit: int, fmt: str, output: str | None):
    """List industry sectors with real-time quotes.

    \b
    $ astock sector list
    $ astock sector list -n 10 --format csv
    """
    with console.status("获取板块行情..."):
        df = _fetch_or_fail(get_sector_quotes)
    if not df.empty:
        df = df.head(limit)
    _emit_dataframe(df, fmt, output, title="申万行业板块")


@sector.command("top")
@click.argument("metric", type=SECTOR_METRICS)
@click.option("--asc", "ascending", is_flag=True, help="升序排列 (默认降序)")
@click.option("-n", "--limit", type=int, default=20, help="返回数量 (默认 20)")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def sector_top(metric: str, ascending: bool, limit: int, fmt: str, output: str | None):
    """Rank sectors by a metric.

    \b
    $ astock sector top change_pct
    $ astock sector top turnover --asc -n 10
    """
    with console.status("板块排序中..."):
        df = _fetch_or_fail(rank_sectors, metric=metric, ascending=ascending, limit=limit)
    metric_names = {
        "change_pct": "涨跌幅", "turnover": "换手率", "total_mv": "总市值",
        "up_count": "上涨家数", "down_count": "下跌家数",
    }
    direction = "升序" if ascending else "降序"
    _emit_dataframe(df, fmt, output, title=f"板块{metric_names.get(metric, metric)}排行 ({direction})")


@cli.group()
def watch():
    """Manage your watchlist (stored in ~/.astock/watchlist.json)."""
    pass


@watch.command("add")
@click.argument("code")
def watch_add(code: str):
    """Add a stock code to the watchlist.

    \b
    $ astock watch add 000001
    """
    if wl_add(code):
        console.print(f"[green]已添加 {code}[/green]")
    else:
        console.print(f"[yellow]{code} 已在自选列表中[/yellow]")


@watch.command("remove")
@click.argument("code")
def watch_remove(code: str):
    """Remove a stock code from the watchlist.

    \b
    $ astock watch remove 000001
    """
    if wl_remove(code):
        console.print(f"[green]已移除 {code}[/green]")
    else:
        console.print(f"[yellow]{code} 不在自选列表中[/yellow]")


@watch.command("list")
@click.option("-f", "--format", "fmt", type=OutputFormat, default="table", help="输出格式")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="写入文件(JSON/CSV)")
def watch_list(fmt: str, output: str | None):
    """Show quotes for all stocks in your watchlist.

    \b
    $ astock watch list
    $ astock watch list --format json
    """
    codes = wl_list()
    if not codes:
        console.print("[yellow]自选列表为空。用 astock watch add 000001 添加[/yellow]")
        return
    with console.status("获取自选行情..."):
        df = _fetch_or_fail(get_realtime_quotes)
    if df.empty or "code" not in df.columns:
        _emit_dataframe(df, fmt, output, title="自选股")
        return
    matched = df[df["code"].astype(str).isin(codes)]
    _emit_dataframe(matched, fmt, output, title="自选股")


if __name__ == "__main__":
    cli()
