"""DuckDB data access layer for the dashboard.

All queries go through this module — pages never query DuckDB directly.
Uses @functools.lru_cache for in-process caching (survives across callbacks).
"""

import functools
import json
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "wfp.duckdb")
FORECAST_PATH = str(PROJECT_ROOT / "dashboard" / "public" / "data" / "forecast.json")
SCHEMA = "wfp_marts"


def _connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH, read_only=True)


@functools.lru_cache(maxsize=32)
def load_mart(name: str, **filters: str | int | float) -> pd.DataFrame:
    """Load a mart model from DuckDB with optional WHERE clauses.

    Args:
        name: Mart model name (e.g. 'mart_price_trends_national').
        **filters: Column-value pairs added as WHERE clauses.

    Returns:
        DataFrame with the query results.
    """
    query = f"SELECT * FROM {SCHEMA}.{name}"
    conditions = []
    values = []
    for col, val in filters.items():
        if val is not None and val != "All":
            conditions.append(f"{col} = ?")
            values.append(val)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY 1"

    conn = _connect()
    try:
        df = conn.execute(query, values).fetchdf()
    finally:
        conn.close()
    return df


@functools.lru_cache(maxsize=8)
def load_forecast_data() -> pd.DataFrame:
    """Load forecast data from the static JSON file."""
    with open(FORECAST_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    records = raw.get("data", [])
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


@functools.lru_cache(maxsize=8)
def load_forecast_metadata() -> dict:
    """Load forecast metadata (models, data_source_note, etc.)."""
    with open(FORECAST_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return raw.get("metadata", {})


def get_latest_prices(df: pd.DataFrame, commodity_col: str = "commodity_consolidated") -> pd.DataFrame:
    """Get the most recent price per commodity from a trends DataFrame."""
    if df.empty:
        return df
    latest = (
        df.sort_values("month")
        .groupby(commodity_col)
        .tail(1)
        .reset_index(drop=True)
    )
    return latest


def compute_yoy_delta(df: pd.DataFrame, price_col: str = "avg_price_idr") -> pd.DataFrame:
    """Add a YoY% column to a DataFrame with monthly price data.

    Assumes the DataFrame has a 'month' column (string or date).
    """
    if df.empty or price_col not in df.columns:
        return df
    df = df.copy()
    df["_month_dt"] = pd.to_datetime(df["month"])
    df["_year"] = df["_month_dt"].dt.year
    df["_month_num"] = df["_month_dt"].dt.month

    prev = df.copy()
    prev["_year"] = prev["_year"] + 1
    merged = df.merge(
        prev[["commodity_consolidated", "_year", "_month_num", price_col]],
        on=["commodity_consolidated", "_year", "_month_num"],
        how="left",
        suffixes=("", "_prev"),
    )
    prev_col = f"{price_col}_prev"
    if prev_col in merged.columns:
        merged["yoy_pct"] = merged.apply(
            lambda r: round((r[price_col] - r[prev_col]) / r[prev_col] * 100, 1)
            if r[prev_col] and r[prev_col] > 0 else None,
            axis=1,
        )
    else:
        merged["yoy_pct"] = None

    merged.drop(columns=["_month_dt", "_year", "_month_num"], inplace=True, errors="ignore")
    return merged
