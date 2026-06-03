"""CLI entry point for astock."""

from __future__ import annotations

from pathlib import Path

import click
import pandas as pd

from .data import DataFetchError, get_index_quote, get_stock_quote, rank_by, screener, search_stocks
from .display import console, show_quote, show_table

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


if __name__ == "__main__":
    cli()
