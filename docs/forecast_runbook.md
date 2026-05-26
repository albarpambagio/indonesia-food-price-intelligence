# Forecast Runbook

Operational guide for running the forecast pipeline. Methodology details in [`model_methodology.md`](./model_methodology.md).

## Prerequisites

- Python environment with dependencies installed (`uv sync`)
- DuckDB database at `data/wfp.duckdb` with `wfp_intermediate.int_prices_normalised` populated
- Islamic calendar seed file at `transform/seeds/islamic_calendar.csv`

## Step-by-Step

```bash
# 1. Activate environment (if not already)
uv sync

# 2. Run the forecast pipeline
uv run python forecast/run_forecast.py
```

The script:
1. Loads national average prices from DuckDB (`wfp_intermediate.int_prices_normalised`)
2. Loads Islamic calendar flags from seed CSV
3. For each commodity (Rice, Cooking Oil, Sugar, Flour):
   - Splits into training (all but last 12 months) and holdout (last 12 months)
   - Fits AutoARIMA and AutoETS on training data
   - Forecasts holdout, computes MAE for each model
   - Selects best model, retrains on full data
   - Forecasts 6 months ahead with 95% confidence intervals
4. Runs Cooking Oil post-2022 robustness check separately
5. Validates all forecast values (NaN check, negative check, CI reversal check)
6. Writes `dashboard/public/data/forecast.json`
7. Logs results to `logs/forecast.log`
8. Updates `pipeline.lineage` table with status

## Output

| File | Description |
|------|-------------|
| `dashboard/public/data/forecast.json` | Full forecast data for dashboard |
| `logs/forecast.log` | Detailed run log with per-commodity MAE |
| `pipeline.lineage` | Status record in DuckDB |

## Re-Run Scenarios

| Scenario | Command | Expected Duration |
|----------|---------|-----------------|
| Full forecast (all 4 commodities) | `uv run python forecast/run_forecast.py` | ~30 seconds |
| After dbt rebuild | `cd transform && dbt build && cd .. && uv run python forecast/run_forecast.py` | ~2 minutes |
| After new data load | Run ingest → dbt build → forecast in sequence via `pipeline_orchestrator.ipynb` | ~3 minutes |
