# Forecasting Methodology

## Table of Contents

- [1. Problem Statement](#1-problem-statement)
- [2. Data Preparation](#2-data-preparation)
  - [National Average Prices](#national-average-prices)
  - [Data Coverage](#data-coverage)
  - [Islamic Calendar Regressors](#islamic-calendar-regressors)
  - [Holdout Split](#holdout-split)
- [3. Model Candidates Evaluated](#3-model-candidates-evaluated)
- [4. Model Selection Process](#4-model-selection-process)
  - [Holdout Validation Approach](#holdout-validation-approach)
  - [Per-Commodity Results](#per-commodity-results)
  - [Cooking Oil: Post-2022 Robustness Check](#cooking-oil-post-2022-robustness-check)
  - [Forecast vs Trend Decomposition Validation](#forecast-vs-trend-decomposition-validation)
- [5. Confidence Intervals](#5-confidence-intervals)
  - [What Is a 95% Confidence Interval?](#what-is-a-95-confidence-interval)
  - [Procurement Action Zone](#procurement-action-zone)
  - [Interpretation Guidance](#interpretation-guidance)
- [6. Known Limitations](#6-known-limitations)
  - [Model Limitations](#model-limitations)
  - [Data Limitations](#data-limitations)
  - [Foundational Caveat](#foundational-caveat)
- [7. Re-Running the Forecast](#7-re-running-the-forecast)
- [Appendix A: Forecast Output Structure](#appendix-a-forecast-output-structure)
- [Appendix B: Validation Procedure](#appendix-b-validation-procedure)
- [Appendix C: Seasonal Pattern Validation](#appendix-c-seasonal-pattern-validation)

---

## 1. Problem Statement

**What:** National average monthly retail prices for 4 staple commodities — Rice, Cooking Oil, Sugar, Flour — sourced from WFP Indonesia market price data (Jan 2007–May 2024).

**Grain:** Monthly. All prices are month-end averages across markets, aggregated to national level.

**Horizon:** 6-month rolling forecast (Jun 2024 – Nov 2024), updated when new WFP data becomes available.

**Why:** Procurement teams at Indonesian FMCG companies need forward price visibility to time bulk purchase contracts, manage margin risk, and inform budget planning. The forecast provides directional price estimates with explicit confidence intervals, enabling scenario-based planning rather than point-estimate decisions.

**Audience:** Category Managers and Procurement Analysts who are comfortable with ranges and probabilities but not necessarily with time-series statistics.

---

## 2. Data Preparation

### National Average Prices

Prices are aggregated from `wfp_intermediate.int_prices_normalised`:

```sql
SELECT DATE_TRUNC('month', date) AS ds,
       commodity_consolidated AS unique_id,
       AVG(price_idr) AS y
FROM wfp_intermediate.int_prices_normalised
WHERE commodity_consolidated IS NOT NULL
  AND price_idr > 0
  AND unit IS NOT NULL
  AND EXTRACT(YEAR FROM date) BETWEEN 2007 AND 2024
GROUP BY ds, commodity_consolidated
```

**Key difference from mart models:** The forecasting query includes both `actual` and `aggregate` price flags, whereas dashboard mart models use `actual` only. This ensures sufficient data for commodities where market-level actual prices are sparse (Rice, Sugar, Flour: actual data ends 2020-03; Cooking Oil: continuous through 2024-12).

### Data Coverage

| Commodity | Months | Date Range | Data End |
|-----------|--------|------------|----------|
| Rice | 208 | Jan 2007 – May 2024 | May 2024 |
| Cooking Oil | 215 | Jan 2007 – Dec 2024 | Dec 2024 |
| Sugar | 208 | Jan 2007 – May 2024 | May 2024 |
| Flour | 158 | Jan 2007 – Mar 2020 | Mar 2020 |

### Islamic Calendar Regressors

Ramadan and Eid al-Fitr drive predictable demand spikes for staple commodities (especially sugar and cooking oil). Binary flags are added to training data:

- `eid_month_flag`: 1 when the month contains Eid al-Fitr
- `t_minus_1_flag`: 1 for the month before Eid (peak stockpiling)
- `t_minus_2_flag`: 1 for two months before Eid (early stockpiling)
- `t_minus_3_flag`: 1 for three months before Eid (preparatory)

**Source:** Islamic calendar dates (2007–2024) manually populated from IslamicFinder.org, stored as `transform/seeds/islamic_calendar.csv`.

**Usage in models:** Flags are passed as exogenous regressors to AutoARIMA (which supports external regressors). AutoETS models seasonality internally and ignores these flags.

**Comparability note:** This creates a confounded comparison — model architecture and regressor presence vary simultaneously. We accept this trade-off because: (a) AutoETS does not support exogenous regressors in this implementation, (b) the primary decision is which deployed model produces better forecasts (not isolating the effect of regressors), and (c) the comparability hazard is concentrated in Ramadan-adjacent months, not the full series.

**Limitation:** For the forecast period (Jun–Nov 2024), all Islamic calendar flags are 0 since Ramadan 2024 (Mar–Apr 2024) falls before the forecast window.

### Holdout Split

For each commodity, the last 12 months of available data are held out for validation. If fewer than 12 months exist (e.g., Flour ending 2020-03), a minimum 6-month holdout is used. The model is trained on all preceding months, then evaluated on the holdout period.

---

## 3. Model Candidates Evaluated

Three candidate models are evaluated per commodity:

| Model | Description | Status |
|-------|-------------|--------|
| **AutoARIMA** | Automatic ARIMA with seasonal order selection (AIC). Captures trends and autoregressive patterns. Supports exogenous regressors (Islamic calendar flags). | Primary |
| **AutoETS** | Error/Trend/Seasonality decomposition. Strong for seasonal data. Fewer parameters than ARIMA, lower overfitting risk. Does not use external regressors. | Primary |
| AutoTheta | Theta method with decomposition. Robust for noisy series. | Optional (experimental) |

AutoTheta is available in the `forecast_experimentation.py` notebook for interactive exploration but is not run in the production pipeline.

---

## 4. Model Selection Process

### Holdout Validation Approach

For each commodity:
1. Training window = all data up to `last_date - 12 months`
2. Holdout window = last 12 months of data
3. Fit both AutoARIMA (season_length=12) and AutoETS (season_length=12) on training window
4. Forecast the holdout period
5. Select model with lowest holdout MAE (Mean Absolute Error)
6. Retrain selected model on full dataset and forecast 6 months ahead

**Note on validation strategy:** A single holdout is used rather than walk-forward (rolling-origin) validation because Islamic calendar regressors introduce lookahead leakage across folds — a flag like `t_minus_1_flag` depends on knowing future Ramadan dates, which would be inconsistent under multiple origins. A multi-origin walk-forward that excludes regressor-dependent months from evaluation is the natural next enhancement.

**Why MAE?** Mean Absolute Error is chosen over RMSE (penalizes large errors quadratically, harder to interpret in IDR) and MAPE (asymmetric, undefined at zero, inflates error for low-price commodities like Flour at ~9,500 IDR vs Rice at ~14,500 IDR). MAE expresses average error in the same unit as price (IDR), which maps directly to procurement cost impact. The trade-off is that MAE underweights outlier months (e.g., 2022 Cooking Oil shock), but this aligns with the forecasting goal — directional accuracy across typical conditions, not worst-case fit.

### Per-Commodity Results

| Commodity | Selected Model | Holdout MAE (IDR) | Train Months |
|-----------|---------------|-------------------|-------------|
| Rice | AutoETS | 794.2 | 196 |
| Cooking Oil | AutoARIMA | 1,714.2 | 203 |
| Sugar | AutoETS | 1,230.4 | 196 |
| Flour | AutoETS | 23.1 | 146 |

### Cooking Oil: Post-2022 Robustness Check

Cooking Oil experienced a structural break in 2022 (export ban + global price shock). A separate model is trained on post-2022 data (36 months) as a robustness check:

| Model | Holdout MAE (IDR) |
|-------|-------------------|
| AutoARIMA (post-2022) | 1,710.8 |

The post-2022 model produces similar MAE to the full-series model, suggesting the 2022 shock does not materially degrade forecast quality for the near-term horizon. Both forecasts are stored in `forecast.json` for dashboard comparison.

### Forecast vs Trend Decomposition Validation

The Phase 5 deep dive validates forecast results against independent trend decomposition:

| Commodity | Model | 6mo Δ | 95% CI Width | Verdict |
|-----------|-------|-------|-------------|---------|
| Rice | AutoETS | +0.6% | 28.8% | Directional — wide CI, scenario planning only |
| Cooking Oil | AutoARIMA | +0.8% | 21.4% | Directional — post-2022 break reduces reliability |
| Sugar | AutoETS | +0.3% | 27.3% | Directional — CI too wide for operational timing |
| Flour | AutoETS | +0.0% | 12.2% | Pre-2020 only — narrow CI reflects stable pre-COVID prices, not forecast reliability. Do not use operationally. |

---

## 5. Confidence Intervals

### What Is a 95% Confidence Interval?

A 95% confidence interval means: **if we ran this forecasting process 100 times (on different historical periods), the actual price would fall inside the shaded range about 95 times out of 100.**

In procurement terms:
- **Narrower CI** (e.g., Flour at ±6%) = higher confidence. The model sees a clear, stable pattern.
- **Wider CI** (e.g., Rice at ±14%) = lower confidence. More uncertainty in the price trajectory.
- The CI **widens at longer horizons** — 5–6 month forecasts are inherently less certain than 1–2 month.

### Procurement Action Zone

A **Procurement Action Zone** is triggered when the forecast lower 95% bound exceeds the current price by >5%. This would indicate a high probability of price increase, warranting forward-buying.

As of the last data point:
- **No commodity** triggers the action zone — all forecasts are essentially flat.
- The flat forecast suggests no urgency for forward-buying, but wide CIs (12–29%) mean the model cannot rule out meaningful moves.
- **Operational recommendation:** Use 1–2 month forecasts for contract timing decisions. Use 5–6 month projections as scenario inputs with appropriate caveats.

### Interpretation Guidance

1. Pay more attention to **1-2 month forecasts** for operational decisions — CI width increases at longer horizons.
2. **Cooking Oil forecast** should be compared against the post-2022 robustness check. If they diverge, the post-2022 model is preferred for near-term decisions.
3. **Flour forecast** is based on pre-2020 data only — recent supply chain dynamics are not reflected.
4. **Rice and Sugar** use AutoETS, which captures seasonality well but may miss recent trend changes.
5. All dashboards displaying forecast data include the footnote: *"Forecast assumes no structural breaks. 1-2 month forecasts more reliable than 5-6 month. See methodology doc for details."*

---

## 6. Known Limitations

### Model Limitations

| Limitation | Implication |
|------------|-------------|
| Government price controls (HET for cooking oil, rice) | Model cannot anticipate policy interventions — forecast assumes no structural breaks |
| Import tariff changes | Sudden tariff adjustments create step-changes the model treats as noise |
| El Nino / La Nina cycles | Drought effects on rice and sugar not captured without weather input data |
| Islamic calendar as AutoARIMA regressor only | AutoETS uses internal seasonality without explicit Ramadan flags |
| Forecast horizon accuracy degrades | 1-2 month forecasts reliable; 5-6 month projections are directional only |

### Data Limitations

| Limitation | Impact on Forecast |
|------------|-------------------|
| Retail prices only, not wholesale | Directionally correct proxy for procurement decisions |
| Rice/Sugar/Flour: actual prices end 2020-03 | Forecasts trained on pre-2020 data; recent dynamics not captured |
| Cooking Oil 2022 structural break | Full-series model includes pre-break data; post-2022 check provided separately |
| Coverage gaps in outer islands pre-2015 | National averages partially affected for early years |
| No volume weighting | All markets weighted equally |

### Foundational Caveat

> This model describes patterns in historical data — it does not predict policy.

---

## 7. Re-Running the Forecast

See [`docs/forecast_runbook.md`](./forecast_runbook.md) for step-by-step instructions, prerequisites, output files, and re-run scenarios.

---

## Appendix A: Forecast Output Structure

**Script:** `forecast/run_forecast.py`

**Output file:** `dashboard/public/data/forecast.json`

```json
{
  "metadata": {
    "generated_at": "2026-05-25T...",
    "data_end": "2024-05-01",
    "forecast_horizon": "6_months",
    "forecast_start": "2024-06-01",
    "forecast_end": "2024-11-01",
    "models": {
      "Rice": { "selected": "AutoETS", "holdout_mae": 794.2 },
      "Cooking Oil": { "selected": "AutoARIMA", "holdout_mae": 1714.2 },
      "Cooking Oil_post2022_robustness": { "selected": "AutoARIMA", "holdout_mae": 1710.8 },
      "Sugar": { "selected": "AutoETS", "holdout_mae": 1230.4 },
      "Flour": { "selected": "AutoETS", "holdout_mae": 23.1 }
    },
    "limitations": "..."
  },
  "data": [
    {"date": "2007-01-01", "commodity": "Rice", "actual_price": 5000.0},
    {"date": "2024-06-01", "commodity": "Rice",
     "forecast_price": 14780.3, "lower_95": 13825.9, "upper_95": 15734.7, "model_used": "AutoETS"}
  ]
}
```

Each record contains either `actual_price` (historical) or `forecast_price` / `lower_95` / `upper_95` (forecast). The dashboard uses `actual_price` for the historical line and `forecast_price` + confidence interval for the forecast segment.

### Other Exported Files

| File | Source | Records |
|------|--------|---------|
| `price_trends.json` | `mart_price_trends` | 238 |
| `seasonal_patterns.json` | `mart_seasonal_patterns` | 35 |
| `geographic_disparity.json` | `mart_geo_disparity` | 34 |
| `commodity_correlation.json` | `mart_commodity_correlation` | 165 |
| `correlation_summary.json` | `mart_correlation_summary` | 24 |

---

## Appendix B: Validation Procedure

### Forecast Validation (`forecast/run_forecast.py`)

Post-generation checks for each forecast record:

| Check | Condition | Action |
|-------|-----------|--------|
| NaN check | `forecast_price` is NaN or Inf | Log error, set status to `completed_with_warnings` |
| Negative price | `forecast_price <= 0` | Log error, set status to `completed_with_warnings` |
| CI reversal | `lower_95 > upper_95` | Log error, set status to `completed_with_warnings` |

All validation results are logged to `logs/forecast.log` and recorded in `pipeline.lineage.forecast_status`.

### Export Verification (`export/export_json.py`)

Each exported JSON file is verified against its source mart:

```
SELECT COUNT(*) FROM wfp_marts.mart_price_trends == len(price_trends.json records)
```

Mismatch sets `pipeline.lineage.export_status = 'failed'`.

---

## Appendix C: Seasonal Pattern Validation

The deep dive decomposes trend into observed/trend/seasonal/residual components per commodity using a 12-month moving average:

- **Rice and Sugar** show cleanest seasonal decomposition — suitable for procurement calendar planning
- **Cooking Oil** seasonal component is distorted by the 2022 structural break (appears as 60.7% peak-to-trough "seasonality" that is actually a level shift)
- **Flour** decomposition is limited by pre-2020 data end — post-2020 dynamics not captured
