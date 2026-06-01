"""CLI entry point for astock."""

from __future__ import annotations

import click

from .data import get_realtime_quotes, get_stock_quote, screener, rank_by, get_index_quote
from .display import console, show_table, show_quote


@click.group()
@click.version_option()
def cli():
    """A-share stock terminal toolkit — quotes, screening & ranking."""
    pass


@cli.command()
@click.argument("code")
def quote(code: str):
    """Show real-time quote for a stock.

    \b
    $ astock quote 000001
    """
    with console.status("获取行情数据..."):
        df = get_realtime_quotes()
    if df.empty:
        console.print("[red]获取数据失败，请检查网络连接[/red]")
        return
    stock = df[df["code"] == code]
    show_quote(code, stock)


@cli.command()
def index():
    """Show major index quotes (上证、深证、创业板)."""
    with console.status("获取指数数据..."):
        df = get_index_quote()
    show_table(df, title="主要指数", columns=["code", "name", "price", "change_pct", "amount"])


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
def screen(**kwargs):
    """Screen stocks by financial metrics.

    \b
    $ astock screen --max-pe 30 --min-turnover 3 -n 10
    """
    limit = kwargs.pop("limit", 20)
    with console.status("筛选中..."):
        df = screener(limit=limit, **{k: v for k, v in kwargs.items() if v is not None})
    show_table(df, title="筛选结果")


@cli.command()
@click.argument("metric", type=click.Choice(["change_pct", "turnover", "pe", "pb", "total_mv", "amount", "volume"]))
@click.option("--asc", "ascending", is_flag=True, help="升序排列 (默认降序)")
@click.option("-n", "--limit", type=int, default=20, help="返回数量 (默认 20)")
def top(metric: str, ascending: bool, limit: int):
    """Rank stocks by a metric.

    \b
    $ astock top change_pct          # 涨幅排行
    $ astock top pe --asc -n 10      # PE 最低 10 只
    $ astock top total_mv            # 市值排行
    """
    with console.status("排序中..."):
        df = rank_by(metric=metric, ascending=ascending, limit=limit)
    metric_names = {
        "change_pct": "涨跌幅", "turnover": "换手率", "pe": "PE",
        "pb": "PB", "total_mv": "总市值", "amount": "成交额", "volume": "成交量",
    }
    direction = "升序" if ascending else "降序"
    show_table(df, title=f"{metric_names.get(metric, metric)}排行 ({direction})")


if __name__ == "__main__":
    cli()
