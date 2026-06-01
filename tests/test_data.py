import pandas as pd
import pytest

from astock import data
from astock.data import DataFetchError, get_realtime_quotes, rank_by, screener


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
