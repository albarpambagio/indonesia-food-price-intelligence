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


def get_latest_prices(
    df: pd.DataFrame, commodity_col: str = "commodity_consolidated"
) -> pd.DataFrame:
    """Get the most recent price per commodity from a trends DataFrame."""
    if df.empty:
        return df
    latest = df.sort_values("month").groupby(commodity_col).tail(1).reset_index(drop=True)
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
            lambda r: (
                round((r[price_col] - r[prev_col]) / r[prev_col] * 100, 1)
                if r[prev_col] and r[prev_col] > 0
                else None
            ),
            axis=1,
        )
    else:
        merged["yoy_pct"] = None

    merged.drop(columns=["_month_dt", "_year", "_month_num"], inplace=True, errors="ignore")
    return merged


@functools.lru_cache(maxsize=8)
def load_islamic_calendar() -> pd.DataFrame:
    """Load Islamic calendar from DuckDB int_islamic_calendar model."""
    conn = _connect()
    try:
        df = conn.execute(
            "SELECT year, eid_date, eid_month FROM wfp_intermediate.int_islamic_calendar ORDER BY year"
        ).fetchdf()
    finally:
        conn.close()
    if not df.empty:
        df["eid_date"] = pd.to_datetime(df["eid_date"])
    return df


def compute_heatmap_matrix(df_national: pd.DataFrame) -> pd.DataFrame:
    """Compute 4x12 matrix: commodity x month_of_year, values = mean premium % vs annual avg.

    Returns DataFrame with columns: commodity_consolidated, month_num (1-12), premium_pct.
    """
    if df_national.empty:
        return pd.DataFrame(columns=["commodity_consolidated", "month_num", "premium_pct"])

    df = df_national.copy()
    df["_year"] = pd.to_datetime(df["month"]).dt.year
    df["_month_num"] = pd.to_datetime(df["month"]).dt.month

    annual_avg = (
        df.groupby(["commodity_consolidated", "_year"])["avg_price_idr"].mean().reset_index()
    )
    annual_avg.columns = ["commodity_consolidated", "_year", "_annual_avg"]

    df = df.merge(annual_avg, on=["commodity_consolidated", "_year"], how="left")
    df["price_index"] = (df["avg_price_idr"] / df["_annual_avg"]) * 100

    result = (
        df.groupby(["commodity_consolidated", "_month_num"])["price_index"].mean().reset_index()
    )
    result.columns = ["commodity_consolidated", "month_num", "premium_pct"]
    result["premium_pct"] = result["premium_pct"] - 100
    return result


def compute_ramadan_overlay(
    df_national: pd.DataFrame,
    commodity: str,
    islamic_cal: pd.DataFrame,
) -> pd.DataFrame:
    """Compute price index relative to Eid al-Fitr for one commodity.

    Returns DataFrame with columns: year, month_relative, price_index.
    month_relative ranges from -2 to +1 (months relative to Eid).
    """
    if df_national.empty or islamic_cal.empty:
        return pd.DataFrame(columns=["year", "month_relative", "price_index"])

    commodity_df = df_national[df_national["commodity_consolidated"] == commodity].copy()
    if commodity_df.empty:
        return pd.DataFrame(columns=["year", "month_relative", "price_index"])

    commodity_df["_month_dt"] = pd.to_datetime(commodity_df["month"])
    commodity_df["_year"] = commodity_df["_month_dt"].dt.year
    commodity_df["_month_num"] = commodity_df["_month_dt"].dt.month

    annual_avg = commodity_df.groupby("_year")["avg_price_idr"].mean().reset_index()
    annual_avg.columns = ["_year", "_annual_avg"]
    commodity_df = commodity_df.merge(annual_avg, on="_year", how="left")
    commodity_df["price_index"] = (
        commodity_df["avg_price_idr"] / commodity_df["_annual_avg"]
    ) * 100

    cal = islamic_cal[["year", "eid_date"]].copy()
    cal["eid_month_num"] = cal["eid_date"].dt.month
    cal["eid_year"] = cal["eid_date"].dt.year

    cal_lookup = cal[["year", "eid_year", "eid_month_num"]].copy()

    merged = commodity_df.merge(
        cal_lookup,
        left_on="_year",
        right_on="year",
        how="inner",
    )

    price_month_num = merged["_month_num"].values
    eid_month_num = merged["eid_month_num"].values
    price_year = merged["_year"].values
    eid_year_vals = merged["eid_year"].values

    merged["month_relative"] = (price_year - eid_year_vals) * 12 + (price_month_num - eid_month_num)

    result = merged[merged["month_relative"].between(-2, 1)][
        ["year", "month_relative", "price_index"]
    ].copy()
    result["year"] = result["year"].astype(int)
    return result.sort_values(["year", "month_relative"]).reset_index(drop=True)


def compute_action_windows(
    df_national: pd.DataFrame,
    driver: str,
    islamic_cal: pd.DataFrame,
) -> pd.DataFrame:
    """Compute per-commodity action window stats for a given seasonal driver.

    Returns DataFrame with columns:
    commodity, spike_pct, consistency_score, total_years, lead_months, data_scope.
    """
    if df_national.empty:
        return pd.DataFrame(
            columns=[
                "commodity",
                "spike_pct",
                "consistency_score",
                "total_years",
                "lead_months",
                "data_scope",
            ]
        )

    driver_months_map = {
        "Harvest": [3, 4, 8, 9],
        "Year-End": [11, 12],
    }

    df = df_national.copy()
    df["_month_dt"] = pd.to_datetime(df["month"])
    df["_year"] = df["_month_dt"].dt.year
    df["_month_num"] = df["_month_dt"].dt.month

    annual_avg = (
        df.groupby(["commodity_consolidated", "_year"])["avg_price_idr"].mean().reset_index()
    )
    annual_avg.columns = ["commodity_consolidated", "_year", "_annual_avg"]
    df = df.merge(annual_avg, on=["commodity_consolidated", "_year"], how="left")
    df["price_index"] = (df["avg_price_idr"] / df["_annual_avg"]) * 100

    results = []
    for commodity in sorted(df["commodity_consolidated"].unique()):
        commodity_df = df[df["commodity_consolidated"] == commodity].copy()

        if driver == "Ramadan":
            if islamic_cal.empty:
                continue
            cal = islamic_cal[["year", "eid_date"]].copy()
            cal["eid_month_num"] = cal["eid_date"].dt.month
            cal["eid_year"] = cal["eid_date"].dt.year
            cal_lookup = cal[["year", "eid_year", "eid_month_num"]].copy()
            merged = commodity_df.merge(
                cal_lookup,
                left_on="_year",
                right_on="year",
                how="inner",
            )
            price_month_num = merged["_month_num"].values
            eid_month_num_vals = merged["eid_month_num"].values
            price_year = merged["_year"].values
            eid_year_vals = merged["eid_year"].values
            merged["month_relative"] = (price_year - eid_year_vals) * 12 + (
                price_month_num - eid_month_num_vals
            )
            driver_data = merged[merged["month_relative"].between(-2, 0)]
            non_driver_data = merged[~merged["month_relative"].between(-2, 0)]
        elif driver in driver_months_map:
            driver_data = commodity_df[commodity_df["_month_num"].isin(driver_months_map[driver])]
            non_driver_data = commodity_df[
                ~commodity_df["_month_num"].isin(driver_months_map[driver])
            ]
        else:
            continue

        if driver_data.empty or non_driver_data.empty:
            continue

        driver_avg = driver_data["price_index"].mean()
        non_driver_avg = non_driver_data["price_index"].mean()

        if non_driver_avg == 0:
            continue

        spike_pct = round((driver_avg - non_driver_avg) / non_driver_avg * 100, 1)

        yearly_driver = driver_data.groupby("_year")["price_index"].mean()
        yearly_annual = commodity_df.groupby("_year")["price_index"].mean()
        years_with_spike = sum(
            1
            for y in yearly_driver.index
            if y in yearly_annual.index and yearly_driver[y] > yearly_annual[y]
        )
        total_years = len(yearly_driver)
        consistency_score = f"{years_with_spike}/{total_years}" if total_years > 0 else "0/0"

        lead_months_map = {
            "Ramadan": "2 months before Eid",
            "Harvest": "Mar-Apr or Aug-Sep",
            "Year-End": "Nov-Dec",
        }

        results.append(
            {
                "commodity": commodity,
                "spike_pct": spike_pct,
                "consistency_score": consistency_score,
                "total_years": total_years,
                "lead_months": lead_months_map.get(driver, ""),
                "data_scope": "national",
            }
        )

    result_df = pd.DataFrame(results)
    if not result_df.empty:
        result_df = result_df[result_df["spike_pct"].abs() > 1]
        result_df = result_df.sort_values("spike_pct", ascending=False).reset_index(drop=True)
    return result_df
