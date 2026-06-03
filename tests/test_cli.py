import json

import pandas as pd
from click.testing import CliRunner

from astock import cli as cli_module
from astock.cli import cli
from astock.data import DataFetchError


def sample_df():
    return pd.DataFrame([
        {"code": "000001", "name": "平安银行", "price": 10.5, "change_pct": 1.2, "turnover": 3.5, "pe": 12, "pb": 0.8, "total_mv": 1000000000}
    ])


def test_top_json(monkeypatch):
    monkeypatch.setattr(cli_module, "rank_by", lambda **kwargs: sample_df())
    result = CliRunner().invoke(cli, ["top", "pe", "--format", "json"])

    assert result.exit_code == 0
    assert json.loads(result.output)[0]["code"] == "000001"


def test_screen_csv(monkeypatch):
    monkeypatch.setattr(cli_module, "screener", lambda **kwargs: sample_df())
    result = CliRunner().invoke(cli, ["screen", "--format", "csv"])

    assert result.exit_code == 0
    assert "code,name,price" in result.output


def test_output_file(monkeypatch, tmp_path):
    monkeypatch.setattr(cli_module, "rank_by", lambda **kwargs: sample_df())
    out = tmp_path / "stocks.json"
    result = CliRunner().invoke(cli, ["top", "pe", "--format", "json", "--output", str(out)])

    assert result.exit_code == 0
    assert json.loads(out.read_text())[0]["code"] == "000001"


def test_data_error_is_click_error(monkeypatch):
    def fail(**kwargs):
        raise DataFetchError("network down")

    monkeypatch.setattr(cli_module, "rank_by", fail)
    result = CliRunner().invoke(cli, ["top", "pe"])

    assert result.exit_code != 0
    assert "network down" in result.output


def test_history_json(monkeypatch):
    sample = pd.DataFrame([
        {"date": "2024-01-02", "code": "000001", "open": 10.0, "close": 10.5, "high": 10.6, "low": 9.9, "volume": 1000, "change_pct": 5.0},
    ])
    monkeypatch.setattr(cli_module, "get_history", lambda **kwargs: sample)

    result = CliRunner().invoke(cli, ["history", "000001", "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["date"] == "2024-01-02"
    assert data[0]["close"] == 10.5


def test_history_forwards_options(monkeypatch):
    captured = {}

    def fake(**kwargs):
        captured.update(kwargs)
        return pd.DataFrame()

    monkeypatch.setattr(cli_module, "get_history", fake)
    result = CliRunner().invoke(cli, ["history", "000001", "--start", "2024-01-01", "--end", "2024-01-31", "--adjust", "none"])

    assert result.exit_code == 0
    assert captured["code"] == "000001"
    assert captured["start"] == "2024-01-01"
    assert captured["end"] == "2024-01-31"
    # --adjust none should map to empty string for the data layer
    assert captured["adjust"] == ""
