import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest.config import LINEAGE_TABLE_DDL

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "wfp.duckdb")
SEED_CSV = str(PROJECT_ROOT / "transform" / "seeds" / "islamic_calendar.csv")
OUTPUT_DIR = PROJECT_ROOT / "dashboard" / "public" / "data"
LOG_DIR = PROJECT_ROOT / "logs"
COMMODITIES = ["Rice", "Cooking Oil", "Sugar", "Flour"]
FORECAST_H = 6
HOLDOUT_MONTHS = 12

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_DIR / "forecast.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def get_national_prices() -> pd.DataFrame:
    conn = duckdb.connect(DB_PATH, read_only=True)
    query = """
        SELECT
            DATE_TRUNC('month', date) AS ds,
            commodity_consolidated AS unique_id,
            AVG(price_idr) AS y
        FROM wfp_intermediate.int_prices_normalised
        WHERE commodity_consolidated IS NOT NULL
          AND price_idr > 0
          AND unit IS NOT NULL
          AND EXTRACT(YEAR FROM date) BETWEEN 2007 AND 2024
        GROUP BY ds, commodity_consolidated
        ORDER BY ds, commodity_consolidated
    """
    df = conn.execute(query).fetchdf()
    conn.close()
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"] = df["y"].astype(float)
    return df


def load_islamic_calendar() -> pd.DataFrame:
    cal = pd.read_csv(SEED_CSV)
    for col in ["ramadan_start", "eid_date"]:
        cal[col] = pd.to_datetime(cal[col])
    cal["eid_month"] = cal["eid_date"].dt.to_period("M").astype(str)
    cal["t_minus_1"] = (cal["eid_date"] - pd.DateOffset(months=1)).dt.to_period("M").astype(str)
    cal["t_minus_2"] = (cal["eid_date"] - pd.DateOffset(months=2)).dt.to_period("M").astype(str)
    cal["t_minus_3"] = (cal["eid_date"] - pd.DateOffset(months=3)).dt.to_period("M").astype(str)
    return cal


def add_islamic_flags(df: pd.DataFrame, cal: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()
    df["ym"] = df["ds"].dt.to_period("M").astype(str)
    flags = ["eid_month_flag", "t_minus_1_flag", "t_minus_2_flag", "t_minus_3_flag"]
    for flag in flags:
        df[flag] = 0
    for _, row in cal.iterrows():
        for col, flag in [("eid_month", "eid_month_flag"), ("t_minus_1", "t_minus_1_flag"),
                          ("t_minus_2", "t_minus_2_flag"), ("t_minus_3", "t_minus_3_flag")]:
            df.loc[df["ym"] == row[col], flag] = 1
    return df, flags


def get_future_exog(cal: pd.DataFrame, start: str, periods: int, commodity: str) -> pd.DataFrame:
    dates = pd.date_range(start=start, periods=periods, freq="MS")
    fdf = pd.DataFrame({"unique_id": commodity, "ds": dates})
    fdf["ym"] = fdf["ds"].dt.to_period("M").astype(str)
    flags = ["eid_month_flag", "t_minus_1_flag", "t_minus_2_flag", "t_minus_3_flag"]
    for flag in flags:
        fdf[flag] = 0
    for _, row in cal.iterrows():
        for col, flag in [("eid_month", "eid_month_flag"), ("t_minus_1", "t_minus_1_flag"),
                          ("t_minus_2", "t_minus_2_flag"), ("t_minus_3", "t_minus_3_flag")]:
            fdf.loc[fdf["ym"] == row[col], flag] = 1
    return fdf[["unique_id", "ds"] + flags]


def holdout_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    mask = ~np.isnan(actual) & ~np.isnan(predicted)
    if mask.sum() == 0:
        return float("inf")
    return float(np.mean(np.abs(actual[mask] - predicted[mask])))


def extract_forecast_values(fcast: pd.DataFrame, train_unique_id: str, commodity: str) -> list[dict]:
    model_cols = [c for c in fcast.columns if c not in ("unique_id", "ds")]
    if not model_cols:
        return []
    chosen = model_cols[0]
    lo_col = f"{chosen}-lo-95"
    hi_col = f"{chosen}-hi-95"

    results = []
    for _, row in fcast.iterrows():
        results.append({
            "date": row["ds"].strftime("%Y-%m-%d"),
            "forecast_price": round(float(row[chosen]), 2),
            "lower_95": round(float(row.get(lo_col, row[chosen])), 2) if lo_col in row else None,
            "upper_95": round(float(row.get(hi_col, row[chosen])), 2) if hi_col in row else None,
        })
    return results


def fit_and_forecast(
    full_hist: pd.DataFrame,
    cal: pd.DataFrame,
    commodity: str,
) -> dict[str, Any]:
    hist_id = full_hist[full_hist["unique_id"] == commodity].copy()
    if len(hist_id) < 24:
        logger.warning("  %s: insufficient data (%d months)", commodity, len(hist_id))
        return {"commodity": commodity, "error": "insufficient_data"}

    hist_id = hist_id.sort_values("ds").reset_index(drop=True)

    hist_with_flags, exog_cols = add_islamic_flags(hist_id, cal)

    cutoff = hist_with_flags["ds"].max() - pd.DateOffset(months=HOLDOUT_MONTHS)
    train = hist_with_flags[hist_with_flags["ds"] <= cutoff].reset_index(drop=True)
    test = hist_with_flags[hist_with_flags["ds"] > cutoff].reset_index(drop=True)

    if len(test) < 3:
        cutoff = hist_with_flags["ds"].max() - pd.DateOffset(months=6)
        train = hist_with_flags[hist_with_flags["ds"] <= cutoff].reset_index(drop=True)
        test = hist_with_flags[hist_with_flags["ds"] > cutoff].reset_index(drop=True)

    if len(test) < 2:
        logger.warning("  %s: not enough holdout data (%d months)", commodity, len(test))
        return {"commodity": commodity, "error": "insufficient_holdout"}

    logger.info("  %s: train=%d months, test=%d months", commodity, len(train), len(test))

    models = [
        AutoARIMA(season_length=12),
        AutoETS(season_length=12),
    ]
    sf = StatsForecast(models=models, freq="MS", n_jobs=1)
    sf.fit(df=train[["unique_id", "ds", "y"]])
    holdout_preds = sf.forecast(h=len(test), df=train[["unique_id", "ds", "y"]])

    mae_scores = {}
    for m in holdout_preds.columns:
        if m in ("unique_id", "ds") or "-lo-" in m or "-hi-" in m:
            continue
        model_name = m.split("-")[0] if "-" in m else m
        mae = holdout_mae(test["y"].values, holdout_preds[m].values)
        mae_scores[model_name] = mae

    best_model = min(mae_scores, key=mae_scores.get)
    logger.info("  %s holdout MAE: %s", commodity, {k: f"{v:.1f}" for k, v in mae_scores.items()})
    logger.info("  %s best model: %s", commodity, best_model)

    best_arima = best_model == "AutoARIMA"
    final_model = [AutoARIMA(season_length=12) if best_arima else AutoETS(season_length=12)]
    sf_final = StatsForecast(models=final_model, freq="MS", n_jobs=1)

    if best_arima:
        sf_final.fit(df=hist_with_flags[["unique_id", "ds", "y"] + exog_cols])
        future_exog = get_future_exog(cal, "2024-06-01", FORECAST_H, commodity)
        fcast = sf_final.forecast(h=FORECAST_H, df=hist_with_flags[["unique_id", "ds", "y"] + exog_cols],
                                  X_df=future_exog, level=[95])
    else:
        sf_final.fit(df=hist_id[["unique_id", "ds", "y"]])
        fcast = sf_final.forecast(h=FORECAST_H, df=hist_id[["unique_id", "ds", "y"]], level=[95])

    historical = []
    for _, row in hist_id.iterrows():
        historical.append({
            "date": row["ds"].strftime("%Y-%m-%d"),
            "actual_price": round(float(row["y"]), 2),
        })

    forecast_data = extract_forecast_values(fcast, commodity, commodity)
    for f in forecast_data:
        f["model_used"] = best_model

    result: dict[str, Any] = {
        "commodity": commodity,
        "best_model": best_model,
        "holdout_mae": round(mae_scores.get(best_model, 0.0), 2),
        "mae_scores": {k: round(v, 2) for k, v in mae_scores.items()},
        "historical": historical,
        "forecast": forecast_data,
    }

    if commodity == "Cooking Oil":
        result["post2022"] = fit_cooking_oil_post2022(hist_id, cal, commodity)

    return result


def fit_cooking_oil_post2022(
    hist: pd.DataFrame, cal: pd.DataFrame, commodity: str
) -> dict[str, Any]:
    post2022 = hist[hist["ds"] >= "2022-01-01"].copy()
    if len(post2022) < 6:
        return {"warning": f"Insufficient post-2022 data ({len(post2022)} months, need 6+)"}

    logger.info("  Cooking Oil post-2022 robustness check (%d months)", len(post2022))
    post_with_flags, exog_cols = add_islamic_flags(post2022, cal)

    post_train = post_with_flags[post_with_flags["ds"] < "2024-01-01"].reset_index(drop=True)
    post_test = post_with_flags[post_with_flags["ds"] >= "2024-01-01"].reset_index(drop=True)

    if len(post_test) < 2:
        return {"warning": "Insufficient holdout data"}

    models = [AutoARIMA(season_length=12), AutoETS(season_length=12)]
    sf = StatsForecast(models=models, freq="MS", n_jobs=1)
    sf.fit(df=post_train[["unique_id", "ds", "y"]])
    holdout_preds = sf.forecast(h=len(post_test), df=post_train[["unique_id", "ds", "y"]])

    mae_scores = {}
    for m in holdout_preds.columns:
        if m in ("unique_id", "ds") or "-lo-" in m or "-hi-" in m:
            continue
        mae = holdout_mae(post_test["y"].values, holdout_preds[m].values)
        mae_scores[m] = mae

    best_model = min(mae_scores, key=mae_scores.get)
    best_arima = best_model == "AutoARIMA"
    final_model = [AutoARIMA(season_length=12) if best_arima else AutoETS(season_length=12)]
    sf_final = StatsForecast(models=final_model, freq="MS", n_jobs=1)

    if best_arima:
        sf_final.fit(df=post_with_flags[["unique_id", "ds", "y"] + exog_cols])
        future_exog = get_future_exog(cal, "2024-06-01", FORECAST_H, commodity)
        fcast = sf_final.forecast(h=FORECAST_H,
                                  df=post_with_flags[["unique_id", "ds", "y"] + exog_cols],
                                  X_df=future_exog, level=[95])
    else:
        sf_final.fit(df=post2022[["unique_id", "ds", "y"]])
        fcast = sf_final.forecast(h=FORECAST_H, df=post2022[["unique_id", "ds", "y"]], level=[95])

    forecast_data = extract_forecast_values(fcast, commodity, commodity)
    for f in forecast_data:
        f["model_used"] = best_model

    return {
        "model": best_model,
        "holdout_mae": round(mae_scores.get(best_model, 0.0), 2),
        "forecast": forecast_data,
    }


def validate_forecast(combined_data: list[dict]) -> list[str]:
    errors = []
    for rec in combined_data:
        fp = rec.get("forecast_price")
        if fp is not None:
            if np.isnan(fp) or np.isinf(fp):
                errors.append(f"Invalid forecast_price for {rec.get('commodity')} on {rec.get('date')}: {fp}")
            if fp <= 0:
                errors.append(f"Non-positive forecast_price for {rec.get('commodity')} on {rec.get('date')}: {fp}")
            lo = rec.get("lower_95")
            hi = rec.get("upper_95")
            if lo is not None and hi is not None and lo > hi:
                errors.append(f"CI reversal for {rec.get('commodity')} on {rec.get('date')}: lower={lo} > upper={hi}")
    return errors


def update_lineage(run_id: str, status: str, issues: list[str] | None = None) -> None:
    try:
        conn = duckdb.connect(DB_PATH)
        conn.execute("CREATE SCHEMA IF NOT EXISTS pipeline")
        conn.execute(LINEAGE_TABLE_DDL)
        conn.execute("""
            INSERT INTO pipeline.lineage (run_id, forecast_status, issues_log)
            VALUES (?, ?, ?::JSON)
            ON CONFLICT (run_id)
            DO UPDATE SET forecast_status = EXCLUDED.forecast_status,
                          issues_log = EXCLUDED.issues_log
        """, [run_id, status, json.dumps({"forecast_issues": issues or []})])
        conn.close()
    except Exception as e:
        logger.warning("Could not update lineage: %s", e)


def main() -> None:
    run_id = datetime.now(timezone.utc).strftime("pipeline_%Y%m%d_%H%M%S")
    logger.info("=" * 60)
    logger.info("Forecast run started | run_id=%s", run_id)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Loading national prices from DuckDB...")
        prices = get_national_prices()
        logger.info("  Loaded %d records", len(prices))

        logger.info("Loading Islamic calendar data...")
        cal = load_islamic_calendar()

        models_meta = {}
        combined_data = []
        all_forecasts_valid = True
        validation_errors = []
        skipped_commodities: list[str] = []

        for commodity in COMMODITIES:
            logger.info("Processing %s...", commodity)
            result = fit_and_forecast(prices, cal, commodity)

            if "error" in result:
                logger.warning("  Skipping %s: %s", commodity, result["error"])
                skipped_commodities.append(commodity)
                continue

            models_meta[commodity] = {
                "selected": result["best_model"],
                "holdout_mae": result["holdout_mae"],
                "mae_scores": result["mae_scores"],
            }

            for h in result["historical"]:
                combined_data.append({"date": h["date"], "commodity": commodity,
                                      "actual_price": h["actual_price"]})

            for f in result["forecast"]:
                combined_data.append({"date": f["date"], "commodity": commodity,
                                      "forecast_price": f["forecast_price"],
                                      "lower_95": f["lower_95"],
                                      "upper_95": f["upper_95"],
                                      "model_used": f["model_used"]})

            if commodity == "Cooking Oil" and "post2022" in result:
                p22 = result["post2022"]
                if "warning" in p22:
                    logger.info("  Post-2022 check: %s", p22["warning"])
                else:
                    models_meta["Cooking Oil_post2022_robustness"] = {
                        "selected": p22["model"],
                        "holdout_mae": p22["holdout_mae"],
                    }
                    for f in p22["forecast"]:
                        combined_data.append({"date": f["date"], "commodity": "Cooking Oil",
                                              "forecast_price": f["forecast_price"],
                                              "model_used": f["model_used"],
                                              "scenario": "post2022_robustness"})

        validation_errors = validate_forecast(combined_data)
        if skipped_commodities:
            validation_errors.append(f"Skipped commodities (insufficient data): {', '.join(skipped_commodities)}")
        if validation_errors:
            all_forecasts_valid = False
            logger.warning("Forecast validation found %d issue(s)", len(validation_errors))
            for e in validation_errors:
                logger.warning("  %s", e)

        min_ds = prices["ds"].min()
        max_ds = prices["ds"].max()
        commodity_data_end = {
            k: v["max"].strftime("%Y-%m-%d")
            for k, v in prices.groupby("unique_id")["ds"].agg(["min", "max"]).iterrows()
        }

        output = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "data_start": min_ds.strftime("%Y-%m-%d"),
                "data_end": max_ds.strftime("%Y-%m-%d"),
                "forecast_horizon": f"{FORECAST_H}_months",
                "forecast_start": (max_ds + pd.DateOffset(months=1)).strftime("%Y-%m-%d"),
                "forecast_end": (max_ds + pd.DateOffset(months=FORECAST_H)).strftime("%Y-%m-%d"),
                "commodity_data_end": commodity_data_end,
                "models": models_meta,
                "limitations": (
                    "Forecast assumes no structural breaks (policy interventions, "
                    "import tariff changes, El Nino cycles). 1-2 month forecasts "
                    "more reliable than 5-6 month. Confidence intervals widen "
                    "explicitly with horizon. Cooking Oil includes a post-2022 "
                    "robustness check due to the 2022 price shock."
                ),
            },
            "data": combined_data,
        }

        output_path = OUTPUT_DIR / "forecast.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        logger.info("Forecast written to %s (%d records)", output_path, len(combined_data))

        status = "completed" if all_forecasts_valid else "completed_with_warnings"
        update_lineage(run_id, status, validation_errors)
        logger.info("Forecast run complete | status=%s | run_id=%s", status, run_id)

    except Exception as e:
        logger.exception("Forecast run failed: %s", e)
        update_lineage(run_id, "failed", [str(e)])
        sys.exit(1)


if __name__ == "__main__":
    main()
