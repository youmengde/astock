import pandas as pd

from astock.display import show_quote, show_table


def test_show_table_empty_does_not_crash():
    show_table(pd.DataFrame())


def test_show_quote_zero_change_does_not_crash():
    df = pd.DataFrame([
        {"code": "000001", "name": "平安银行", "price": "10.5", "change_pct": "0", "open": "10", "high": "11", "low": "9", "pre_close": "10.5", "volume": "10000", "amount": "1000000", "turnover": "1", "pe": "12", "pb": "1", "total_mv": "1000000000"}
    ])
    show_quote("000001", df)


def test_show_quote_bad_numeric_does_not_crash():
    df = pd.DataFrame([
        {"code": "000001", "name": "平安银行", "price": "-", "change_pct": "-", "open": "-", "high": "-", "low": "-", "pre_close": "-", "volume": "-", "amount": "-", "turnover": "-", "pe": "-", "pb": "-", "total_mv": "-"}
    ])
    show_quote("000001", df)
