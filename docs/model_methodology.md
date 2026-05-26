# Forecasting Methodology

## Model Selection Rationale

Two primary models are evaluated per commodity, with a third available for interactive experimentation:

| Model | Description | Status |
|-------|-------------|--------|
| **AutoARIMA** | Automatic ARIMA with seasonal order selection (AIC). Captures trends and autoregressive patterns. Handles exogenous regressors. | **Primary** |
| **AutoETS** | Error/Trend/Seasonality decomposition. Strong for seasonal data. Simpler than ARIMA, fewer parameters. | **Primary** |
| AutoTheta | Theta method with decomposition. Robust for noisy series. | Optional (experimental) |

**Selection approach:** For each commodity, both primary models are fit on a training window with the last 12 months held out. The model with the lowest holdout MAE (Mean Absolute Error) is selected for the final 6-month forecast. If holdout data has fewer than 12 months (e.g., Flour with data ending in 2020), a 6-month minimum holdout is used.

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

The post-2022 model produces similar MAE to the full-series model, suggesting the 2022 shock does not materially degrade forecast quality for the near-term horizon.

---

## Islamic Calendar Exogenous Variables

Ramadan and Eid al-Fitr drive predictable demand spikes for staple commodities (especially sugar and cooking oil). Binary flags are added to training data:

- `eid_month_flag`: 1 when the month contains Eid al-Fitr
- `t_minus_1_flag`: 1 for the month before Eid (peak stockpiling)
- `t_minus_2_flag`: 1 for two months before Eid (early stockpiling)
- `t_minus_3_flag`: 1 for three months before Eid (preparatory)

**Source:** Islamic calendar dates (2007–2024) manually populated from IslamicFinder.org.

**Usage in models:** The flags are passed as exogenous regressors to AutoARIMA (which supports external regressors). AutoETS models seasonality internally and ignores these flags. The model comparison therefore inherently tests whether explicit Islamic calendar features improve forecast accuracy over pure seasonal decomposition.

**Limitation:** For the forecast period (Jun–Nov 2024), all Islamic calendar flags are 0 since Ramadan 2024 (Mar–Apr 2024) falls before the forecast window.

---

## Data Preparation

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

### Holdout Split

For each commodity, the last 12 months of available data are held out for validation. The model is trained on all preceding months, then evaluated on the holdout period.

---

## Forecast Output Structure

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

## Validation Procedure

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
SELECT COUNT(*) FROM wfp_marts.mart_price_trends
  == len(price_trends.json records)
```

Mismatch sets `pipeline.lineage.export_status = 'failed'`.

---

## Known Limitations

### Model Limitations

| Limitation | Implication |
|------------|-------------|
| Government price controls (HET for cooking oil, rice) | Model cannot anticipate policy interventions -- forecast assumes no structural breaks |
| Import tariff changes | Sudden tariff adjustments create step-changes the model treats as noise |
| El Nino / La Nina cycles | Drought effects on rice and sugar not captured without weather input data |
| Islamic calendar as AutoARIMA regressor only | AutoETS uses internal seasonality without explicit Ramadan flags |
| Forecast horizon accuracy | 1-2 month forecasts more reliable than 5-6 month. Confidence intervals widen with horizon |

### Data Limitations

| Limitation | Impact on Forecast |
|------------|-------------------|
| Retail prices only, not wholesale | Directionally correct proxy for procurement |
| Rice/Sugar/Flour: actual prices end 2020-03 | Forecasts for these commodities trained on pre-2020 data; recent dynamics not captured |
| Cooking Oil 2022 structural break | Full-series model includes pre-break data; post-2022 robustness check provided separately |
| Coverage gaps in outer islands pre-2015 | National averages partially affected for early years |
| No volume weighting | All markets weighted equally |

---

## Phase 5 Deep Dive Validation

The Phase 5 deep dive analysis (`analysis/deep_dive.py`) independently validates forecast results against trend decomposition and seasonal analysis:

### Forecast vs Trend Decomposition

| Commodity | Model | 6mo Δ | 95% CI Width | Trend Decomposition Verdict |
|-----------|-------|-------|-------------|----------------------------|
| Rice | AutoETS | +0.6% | 28.8% | **Directional** — wide CI, use for scenario planning only |
| Cooking Oil | AutoARIMA | +0.8% | 21.4% | **Directional** — post-2022 structural break reduces reliability |
| Sugar | AutoETS | +0.3% | 27.3% | **Directional** — CI too wide for operational timing decisions |
| Flour | AutoETS | +0.0% | 12.2% | **Operational** — narrowest CI, but pre-2020 data only |

### Procurement Action Zone Framework

A **Procurement Action Zone** is identified when the forecast lower 95% CI bound exceeds the current price by >5%. As of the last data point:

- **No commodity** triggers the action zone — all forecasts are essentially flat.
- The flat forecast suggests no urgency for forward-buying, but the wide CIs (12–29%) mean the model cannot rule out meaningful moves.
- **Operational recommendation**: Use 1–2 month forecasts for contract timing. Use 5–6 month projections as scenario inputs with appropriate caveats.

### Seasonal Pattern Validation

The deep dive decomposes trend into observed/trend/seasonal/residual components per commodity using a 12-month moving average:

- **Rice and Sugar** show cleanest seasonal decomposition — suitable for procurement calendar planning
- **Cooking Oil** seasonal component is distorted by the 2022 structural break (appears as 60.7% peak-to-trough "seasonality" that is actually a level shift)
- **Flour** decomposition is limited by pre-2020 data end — post-2020 dynamics not captured

### Geographic Coverage Limitation

The deep dive confirms that only **Cooking Oil** has sufficient market-level actual price data for geographic analysis. Rice, Sugar, and Flour are available only as national averages (market_id = 974) in the WFP actual-price dataset. Any geographic procurement strategy for non-oil commodities requires supplementary supplier data.

---

## Interpretation Guidance

1. **Confidence intervals** grow wider at longer horizons. Pay more attention to 1-2 month forecasts for operational decisions.
2. **Cooking Oil forecast** should be compared against the post-2022 robustness check. If they diverge, the post-2022 model is preferred for near-term decisions.
3. **Flour forecast** is based on pre-2020 data only. Recent supply chain dynamics may not be reflected.
4. **Rice and Sugar** forecasts use AutoETS, which captures seasonality but may miss recent trend changes.
5. All dashboards displaying forecast data include the footnote: *"Forecast assumes no structural breaks. 1-2 month forecasts more reliable than 5-6 month. See methodology doc for details."*
