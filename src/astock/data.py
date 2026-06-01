"""Data fetching layer — wraps akshare with caching and error handling."""

from __future__ import annotations

import time
from collections.abc import Callable

import akshare as ak
import pandas as pd

CACHE_TTL_SECONDS = 60
_CACHE: dict[str, tuple[float, pd.DataFrame]] = {}


class DataFetchError(RuntimeError):
    """Raised when upstream market data cannot be fetched."""


def _fetch_dataframe(func: Callable, *args, **kwargs) -> pd.DataFrame:
    """Call an akshare function and normalize empty results."""
    try:
        df = func(*args, **kwargs)
    except Exception as exc:
        raise DataFetchError(f"failed to fetch market data: {exc}") from exc
    if df is None or df.empty:
        return pd.DataFrame()
    return df


def _cached(key: str, loader: Callable[[], pd.DataFrame], ttl: int = CACHE_TTL_SECONDS) -> pd.DataFrame:
    now = time.time()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < ttl:
        return cached[1].copy()
    df = loader()
    _CACHE[key] = (now, df.copy())
    return df


def _as_number(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce")


def _filter_numeric(df: pd.DataFrame, col: str, lo: float | None, hi: float | None) -> pd.DataFrame:
    if col not in df.columns:
        return df
    values = _as_number(df, col)
    mask = values.notna()
    if lo is not None:
        mask &= values >= lo
    if hi is not None:
        mask &= values <= hi
    result = df.loc[mask].copy()
    result[col] = values.loc[mask]
    return result


# ── Real-time quotes ──────────────────────────────────────────────

def get_realtime_quotes() -> pd.DataFrame:
    """Get real-time A-share quotes (all stocks)."""
    def load() -> pd.DataFrame:
        df = _fetch_dataframe(ak.stock_zh_a_spot_em)
        if df.empty:
            return df
        col_map = {
            "序号": "index", "代码": "code", "名称": "name",
            "最新价": "price", "涨跌幅": "change_pct",
            "涨跌额": "change", "成交量": "volume",
            "成交额": "amount", "振幅": "amplitude",
            "最高": "high", "最低": "low",
            "今开": "open", "昨收": "pre_close",
            "量比": "volume_ratio", "换手率": "turnover",
            "市盈率-动态": "pe", "市净率": "pb",
            "总市值": "total_mv", "流通市值": "circ_mv",
        }
        return df.rename(columns=col_map)

    return _cached("realtime_quotes", load)


def get_stock_quote(code: str) -> pd.DataFrame:
    """Get quote for a single stock by code."""
    df = get_realtime_quotes()
    if df.empty or "code" not in df.columns:
        return pd.DataFrame()
    return df[df["code"].astype(str) == str(code)]


# ── Screener / filtering ─────────────────────────────────────────

def screener(
    min_pe: float | None = None,
    max_pe: float | None = None,
    min_pb: float | None = None,
    max_pb: float | None = None,
    min_turnover: float | None = None,
    min_change: float | None = None,
    max_change: float | None = None,
    min_mv: float | None = None,
    max_mv: float | None = None,
    limit: int = 20,
) -> pd.DataFrame:
    """Screen A-share stocks by basic financial metrics."""
    df = get_realtime_quotes()
    if df.empty:
        return df

    df = _filter_numeric(df, "pe", min_pe, max_pe)
    df = _filter_numeric(df, "pb", min_pb, max_pb)
    df = _filter_numeric(df, "turnover", min_turnover, None)
    df = _filter_numeric(df, "change_pct", min_change, max_change)
    df = _filter_numeric(df, "total_mv", min_mv, max_mv)

    return df.head(limit)


# ── Ranking ───────────────────────────────────────────────────────

def rank_by(metric: str = "change_pct", ascending: bool = False, limit: int = 20) -> pd.DataFrame:
    """Rank stocks by a given metric.

    Supported metrics: change_pct, turnover, pe, pb, total_mv, amount, volume.
    """
    df = get_realtime_quotes()
    if df.empty or metric not in df.columns:
        return pd.DataFrame()

    values = _as_number(df, metric)
    mask = values.notna()
    if metric in ("pe", "pb"):
        mask &= values > 0

    ranked = df.loc[mask].copy()
    ranked[metric] = values.loc[mask]
    return ranked.sort_values(by=metric, ascending=ascending).head(limit)


# ── Index data ────────────────────────────────────────────────────

def get_index_quote() -> pd.DataFrame:
    """Get major index quotes (SSE, SZSE, CSI)."""
    def load() -> pd.DataFrame:
        df = _fetch_dataframe(ak.stock_zh_index_spot_em)
        if df.empty:
            return df
        major = ["000001", "399001", "399006", "000016", "000300", "000905"]
        col_map = {
            "代码": "code", "名称": "name", "最新价": "price",
            "涨跌幅": "change_pct", "涨跌额": "change",
            "成交量": "volume", "成交额": "amount",
        }
        df = df.rename(columns=col_map)
        if "code" in df.columns:
            df = df[df["code"].astype(str).isin(major)]
        return df

    return _cached("index_quote", load)
