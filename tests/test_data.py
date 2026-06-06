import pandas as pd
import pytest

from astock import data
from astock.data import DataFetchError, get_history, get_realtime_quotes, get_sector_quotes, rank_by, rank_sectors, screener, search_stocks


@pytest.fixture(autouse=True)
def clear_cache():
    data._CACHE.clear()
    yield
    data._CACHE.clear()


def sample_quotes():
    return pd.DataFrame(
        [
            {"代码": "000001", "名称": "平安银行", "最新价": "10.5", "涨跌幅": "1.2", "换手率": "3.5", "市盈率-动态": "12", "市净率": "0.8", "总市值": "1000000000"},
            {"代码": "000002", "名称": "万科A", "最新价": "8.2", "涨跌幅": "-2.1", "换手率": "1.0", "市盈率-动态": "100", "市净率": "1.5", "总市值": "2000000000"},
            {"代码": "000003", "名称": "测试", "最新价": "3.2", "涨跌幅": "0", "换手率": "5.0", "市盈率-动态": "2", "市净率": "0", "总市值": "300000000"},
            {"代码": "000004", "名称": "亏损", "最新价": "6.6", "涨跌幅": "3", "换手率": "2.0", "市盈率-动态": "-5", "市净率": "2.0", "总市值": "400000000"},
        ]
    )


def test_get_realtime_quotes_renames_columns(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_zh_a_spot_em", sample_quotes)

    df = get_realtime_quotes()

    assert {"code", "name", "price", "change_pct", "pe", "pb"}.issubset(df.columns)
    assert df.iloc[0]["code"] == "000001"


def test_screener_filters_numeric_values(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_zh_a_spot_em", sample_quotes)

    df = screener(max_pe=30, min_turnover=3)

    assert list(df["code"]) == ["000001", "000003"]


def test_rank_by_sorts_as_numbers(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_zh_a_spot_em", sample_quotes)

    df = rank_by("pe", ascending=True)

    assert list(df["code"]) == ["000003", "000001", "000002"]


def test_fetch_error_is_visible(monkeypatch):
    def fail():
        raise RuntimeError("boom")

    monkeypatch.setattr(data.ak, "stock_zh_a_spot_em", fail)

    with pytest.raises(DataFetchError, match="boom"):
        get_realtime_quotes()


def test_search_by_name_and_code(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_zh_a_spot_em", sample_quotes)

    by_name = search_stocks("银行")
    assert list(by_name["code"]) == ["000001"]

    by_code = search_stocks("00000")
    assert len(by_code) == 4

    by_partial = search_stocks("万科")
    assert list(by_partial["code"]) == ["000002"]


def sample_history():
    return pd.DataFrame(
        [
            {"日期": "2024-01-02", "股票代码": "000001", "开盘": "10.0", "收盘": "10.5", "最高": "10.6", "最低": "9.9", "成交量": "1000", "涨跌幅": "5.0"},
            {"日期": "2024-01-03", "股票代码": "000001", "开盘": "10.5", "收盘": "10.2", "最高": "10.7", "最低": "10.1", "成交量": "800", "涨跌幅": "-2.86"},
        ]
    )


def test_get_history_renames_columns_and_forwards_args(monkeypatch):
    captured = {}

    def fake_hist(symbol, period, start_date, end_date, adjust):
        captured.update(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
        return sample_history()

    monkeypatch.setattr(data.ak, "stock_zh_a_hist", fake_hist)

    df = get_history("000001", start="2024-01-01", end="2024-01-31", period="daily", adjust="qfq")

    assert captured == {
        "symbol": "000001",
        "period": "daily",
        "start_date": "20240101",
        "end_date": "20240131",
        "adjust": "qfq",
    }
    assert {"date", "open", "close", "high", "low", "volume", "change_pct"}.issubset(df.columns)
    assert list(df["date"]) == ["2024-01-02", "2024-01-03"]


def test_get_history_defaults_dates_when_omitted(monkeypatch):
    captured = {}

    def fake_hist(symbol, period, start_date, end_date, adjust):
        captured.update(start_date=start_date, end_date=end_date)
        return pd.DataFrame()

    monkeypatch.setattr(data.ak, "stock_zh_a_hist", fake_hist)

    get_history("000001")

    # Both should be 8-digit compact dates
    assert len(captured["start_date"]) == 8 and captured["start_date"].isdigit()
    assert len(captured["end_date"]) == 8 and captured["end_date"].isdigit()


def sample_sectors():
    return pd.DataFrame(
        [
            {"板块代码": "BK01", "板块名称": "银行", "最新价": "1200.5", "涨跌幅": "2.3", "换手率": "0.5", "总市值": "5000000000", "上涨家数": "38", "下跌家数": "2", "领涨股票": "招商银行", "排名": "1"},
            {"板块代码": "BK02", "板块名称": "房地产", "最新价": "800.2", "涨跌幅": "-1.5", "换手率": "2.0", "总市值": "2000000000", "上涨家数": "20", "下跌家数": "30", "领涨股票": "万科A", "排名": "2"},
            {"板块代码": "BK03", "板块名称": "科技", "最新价": "1500.0", "涨跌幅": "5.0", "换手率": "4.5", "总市值": "8000000000", "上涨家数": "100", "下跌家数": "15", "领涨股票": "中兴通讯", "排名": "3"},
        ]
    )


def test_get_sector_quotes_renames_columns(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_board_industry_name_em", sample_sectors)

    df = get_sector_quotes()

    assert {"code", "name", "price", "change_pct", "total_mv", "up_count", "down_count"}.issubset(df.columns)
    assert list(df["code"]) == ["BK01", "BK02", "BK03"]


def test_rank_sectors_by_change_pct(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_board_industry_name_em", sample_sectors)

    df = rank_sectors("change_pct", ascending=False)

    assert list(df["code"]) == ["BK03", "BK01", "BK02"]
    df_asc = rank_sectors("change_pct", ascending=True)
    assert list(df_asc["code"]) == ["BK02", "BK01", "BK03"]


def test_rank_sectors_empty_on_missing_metric(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_board_industry_name_em", sample_sectors)

    df = rank_sectors("nonexistent")
    assert df.empty


def test_get_sector_quotes_empty_on_fetch_empty(monkeypatch):
    monkeypatch.setattr(data.ak, "stock_board_industry_name_em", lambda: pd.DataFrame())

    df = get_sector_quotes()
    assert df.empty


def test_sector_help_in_cli(monkeypatch):
    """Smoke-test that the sector command group is wired up."""
    from click.testing import CliRunner
    from astock.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["sector", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "top" in result.output
