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
