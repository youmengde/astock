"""Data fetching layer — wraps akshare with caching and error handling."""

from __future__ import annotations

import time
from functools import lru_cache

import akshare as ak
import pandas as pd


def _safe(func, *args, **kwargs) -> pd.DataFrame:
    """Call akshare function, return empty DataFrame on failure."""
    try:
        df = func(*args, **kwargs)
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


# ── Real-time quotes ──────────────────────────────────────────────

def get_realtime_quotes() -> pd.DataFrame:
    """Get real-time A-share quotes (all stocks)."""
    df = _safe(ak.stock_zh_a_spot_em)
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
    df = df.rename(columns=col_map)
    return df


def get_stock_quote(code: str) -> pd.DataFrame:
    """Get quote for a single stock by code."""
    df = get_realtime_quotes()
    if df.empty:
        return df
    return df[df["code"] == code]


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

    for col, lo, hi in [
        ("pe", min_pe, max_pe),
        ("pb", min_pb, max_pb),
    ]:
        if col not in df.columns:
            continue
        df = df[pd.to_numeric(df[col], errors="coerce").notna()]
        if lo is not None:
            df = df[df[col].astype(float) >= lo]
        if hi is not None:
            df = df[df[col].astype(float) <= hi]

    if "turnover" in df.columns and min_turnover is not None:
        df = df[pd.to_numeric(df["turnover"], errors="coerce").notna()]
        df = df[df["turnover"].astype(float) >= min_turnover]

    if "change_pct" in df.columns:
        df = df[pd.to_numeric(df["change_pct"], errors="coerce").notna()]
        if min_change is not None:
            df = df[df["change_pct"].astype(float) >= min_change]
        if max_change is not None:
            df = df[df["change_pct"].astype(float) <= max_change]

    for col, lo, hi in [("total_mv", min_mv, max_mv)]:
        if col not in df.columns:
            continue
        df = df[pd.to_numeric(df[col], errors="coerce").notna()]
        if lo is not None:
            df = df[df[col].astype(float) >= lo]
        if hi is not None:
            df = df[df[col].astype(float) <= hi]

    return df.head(limit)


# ── Ranking ───────────────────────────────────────────────────────

def rank_by(metric: str = "change_pct", ascending: bool = False, limit: int = 20) -> pd.DataFrame:
    """Rank stocks by a given metric.

    Supported metrics: change_pct, turnover, pe, pb, total_mv, amount, volume.
    """
    df = get_realtime_quotes()
    if df.empty:
        return df
    if metric not in df.columns:
        return pd.DataFrame()
    df = df[pd.to_numeric(df[metric], errors="coerce").notna()]
    # For PE/PB, exclude negative values (loss-making companies)
    if metric in ("pe", "pb"):
        df = df[df[metric].astype(float) > 0]
    df = df.sort_values(by=metric, ascending=ascending)
    return df.head(limit)


# ── Index data ────────────────────────────────────────────────────

def get_index_quote() -> pd.DataFrame:
    """Get major index quotes (SSE, SZSE, CSI)."""
    df = _safe(ak.stock_zh_index_spot_em)
    if df.empty:
        return df
    # Filter major indices
    major = ["000001", "399001", "399006", "000016", "000300", "000905"]
    col_map = {
        "代码": "code", "名称": "name", "最新价": "price",
        "涨跌幅": "change_pct", "涨跌额": "change",
        "成交量": "volume", "成交额": "amount",
    }
    df = df.rename(columns=col_map)
    if "code" in df.columns:
        df = df[df["code"].isin(major)]
    return df
