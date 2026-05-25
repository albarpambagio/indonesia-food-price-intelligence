# Implementation Plan — Indonesia Food Price Intelligence

## Project Meta

| Attribute | Value |
|-----------|-------|
| **Start Date** | 2026-05-22 |
| **Data First Accessed** | 2026-05-22 |
| **Data Source** | WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0) |
| **Target Completion** | ~16–20 working days |
| **Status** | Phase 2 Complete (+ Phase 2.5 corrections applied) |
| **Stack** | Python → DuckDB → dbt → statsforecast → Marimo → Static JSON → Next.js (Shadboard) → Cloudflare Pages |

### Parallelization Opportunities
| Phase | Can Start After | Runs Parallel With | Saves |
|-------|----------------|-------------------|-------|
| Phase 4 (EDA) | Phase 1 done (staging data available) | Phase 2 + Phase 3 | ~3–5 days |
| Phase 7 (Methodology Doc) | Phase 3 started (model decisions known) | Phase 4–6 | ~2–3 days |
| §6.6 Dashboard Init | **Phase 0** (scaffolding, zero data dependency) | Phase 1–5 | ~1 day on back-end |

**Sequential chain** (must wait): Phase 0 → 1 → 2 → 2.5 → 3 → 6 (pages). Phase 4 and 7 slot alongside, not behind.
> **Current**: Phase 1 ✅ → Phase 2 ✅ → Phase 2.5 ✅ → Phase 4 ✅ (parallel). Next: Phase 3 (Forecasting).

---

## Phase 0 — Project Setup & Data Validation Checkpoint

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Create folder structure | ✅ | `data/raw/`, `ingest/`, `transform/`, `forecast/`, `export/`, `analysis/`, `logs/`, `dashboard/public/data/` |
| 0.2 | Create `pyproject.toml` + `uv sync` | ✅ | uv-native: duckdb, dbt-duckdb, statsforecast, marimo, pandas, plotly |
| 0.3 | Init dbt project in `/transform` | ✅ | `dbt init`, configure profiles.yml for DuckDB |
| 0.4 | Init Next.js from Shadboard starter-kit in `/dashboard` | ⬜ | **DEFERRED** to Phase 6.6 |
| 0.5 | Create **`analysis/data_validation.py`** (marimo notebook) | ✅ | Interactive validation: commodity coverage, provincial coverage, priceflag distribution, unit consistency, sugar split, oil split, FX enrichment decision |
| 0.6 | Write `docs/data_validation.md` from notebook findings | ✅ | Document all 7 validation checks, scoping decisions confirmed |
| 0.7 | Load raw CSVs into `data/raw/` | ✅ | `wfp_food_prices_idn.csv` (325,240 rows), `wfp_markets_idn.csv` (224 markets) |

**Validation**: `analysis/data_validation.py` produces quantified summaries for all 7 checks.
**Marimo**: `uv run marimo edit analysis/data_validation.py`

---

## Phase 1 — Ingest & Staging (1 day)

### 1.1 Ingest
| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1.1 | `ingest/load_raw.py` — load food_prices CSV to DuckDB raw.food_prices | ✅ | 325,239 rows loaded |
| 1.1.2 | `ingest/load_raw.py` — load markets CSV to DuckDB raw.markets | ✅ | 224 rows loaded |
| 1.1.3 | Create `ingest/config.py` with `generate_run_id()` — timestamp-based run ID | ✅ | Done in Phase 0 |
| 1.1.4 | Create `pipeline.lineage` table — central run registry | ✅ | Done in Phase 0; fixed JSONB→JSON at runtime |
| 1.1.5 | Add `init_lineage()` / `update_lineage()` helper functions | ✅ | Done in Phase 0; fix: `.replace('_', ' ')` removed from `update_lineage()` |
| 1.1.6 | Split logging into per-script files: `logs/ingest.log`, `logs/transform.log`, `logs/forecast.log`, `logs/export.log` | ✅ | `pipeline_run.log` reserved for orchestration summary |

### 1.2 dbt Staging Models
| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.2.1 | `stg_food_prices.sql` — cast date, uppercase admin, trim, cast price to DECIMAL, rename priceflag, filter price<=0 | ✅ | 0 rows filtered (all prices positive) |
| 1.2.2 | `stg_markets.sql` — snake_case columns, flag national average (market_id=974), cast coordinates to FLOAT | ✅ | Added NULL admin→'NATIONAL' for market_id=974 |

### 1.3 dbt Tests
| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.3.1 | not_null: [date, commodity, market_id, price, price_flag] | ✅ | stg_food_prices — all pass |
| 1.3.2 | accepted_values: price_flag → [actual, aggregate] | ✅ | Uses `arguments:` syntax in schema.yml |
| 1.3.3 | accepted_values: pricetype → [Retail] | ✅ | |
| 1.3.4 | positive_values: price | ✅ | Custom generic test in `macros/positive_values.sql` |
| 1.3.5 | unique: market_id | ✅ | stg_markets |
| 1.3.6 | not_null: [market_id, market, admin1] | ✅ | 12/12 tests pass |

### 1.4 Row Count Reconciliation
| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.4.1 | Validate raw.food_prices COUNT = CSV line count - 1 | ✅ | 325,239 = 325,240 - 1 ✓ |
| 1.4.2 | Validate stg_food_prices COUNT ≤ raw COUNT (price<=0 filtered) | ✅ | 325,239 = 325,239 (no rows filtered) |
| 1.4.3 | Update `pipeline.lineage` with source_rows, staging_rows, status | ✅ | ingest=completed, transform=completed |

**Validation**: Row counts reconcile at every stage. All dbt tests pass. Run history queryable via `SELECT * FROM pipeline.lineage ORDER BY run_start DESC`.

---

## Phase 2 — dbt Transform (Intermediate + Mart) (4–5 days)
> **Sequential** — depends on Phase 1 (staging). Phase 4 (EDA) can run alongside this.

### 2.1 Intermediate Models
| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1.1 | `int_commodity_consolidated.sql` — map Oil variants → Cooking Oil, Sugar variants → Sugar | ✅ | Consolidation per data validation; Sugar gap <5%, Oil r>0.9 |
| 2.1.2 | `int_prices_normalised.sql` — unit normalisation, priceflag separation, island group mapping, 5 quality flags, monthly grain | ✅ | Unit normalisation skipped: all target commodities already use KG/L per data audit. Added `month` (DATE_TRUNC) column per Phase 2.5 centralization. |
| 2.1.3 | Add row-level quality flags: flag_price_le_zero, flag_null_unit, flag_non_target, flag_aggregate, flag_invalid_year | ✅ | Composite `filter_out` column; 2,116 rows pass (actual + target + valid year) |
| 2.1.4 | `int_islamic_calendar.sql` — Ramadan/Eid lookup 2007–2024, source documented | ✅ | CSV seed (transform/seeds/islamic_calendar.csv), source: IslamicFinder.org |

### 2.2 Mart Models
| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.2.1 | `mart_price_trends.sql` — monthly avg price × commodity × island_group × province, IDR + USD | ✅ | Cross-tabulated per §35; 238 rows (Cooking Oil only — see Data Finding) |
| 2.2.2 | `mart_seasonal_patterns.sql` — price index vs annual avg, harvest flags (Mar–Apr, Aug–Sep), year-end flag (Nov–Dec), Ramadan proximity flags | ✅ | 35 rows; Ramadan flags added per Phase 2.5 (flag_ramadan_eid_month, t_minus_1/2/3, t_plus_1) |
| 2.2.3 | `mart_geographic_disparity.sql` — price index vs Java baseline per island group per year, province-level, YoY change | ✅ | 34 rows; Eastern Indonesia restricted to 2015+. `yoy_change_index` added per Phase 2.5. |
| 2.2.4 | `mart_commodity_correlation.sql` — wide-format prices with lags 1–3, all 4 commodities at national level | ✅ | 165 months; 158 months have all 4 commodities. `mart_correlation_summary` created per Phase 2.5 with Pearson r per pair per lag. |

### 2.3 dbt Tests at Mart Layer
| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.3.1 | not_null: [month, commodity_consolidated, avg_price_idr] | ✅ | mart_price_trends, mart_seasonal_patterns, mart_geo_disparity |
| 2.3.2 | accepted_values: commodity_consolidated → [Rice, Cooking Oil, Sugar, Flour] | ✅ | All mart models |
| 2.3.3 | positive_values: price_idr | ✅ | All mart models |
| 2.3.4 | not_null: island_group | ✅ | mart_geo_disparity, mart_price_trends |
| 2.3.5 | accepted_values: island_group → [Java, Sumatera, Kalimantan, Sulawesi, Eastern Indonesia] | ✅ | |
| 2.3.6 | `dbt docs generate` + lineage graph screenshot | ✅ | Catalog written to target/catalog.json |

### 2.4 Row Count Reconciliation
| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.4.1 | Validate int_prices_normalised COUNT = stg_food_prices COUNT | ✅ | 325,239 = 325,239 ✓ (no rows filtered at intermediate) |
| 2.4.2 | Validate each mart COUNT ≤ int_prices_normalised (filtered) COUNT | ✅ | 2,116 filtered rows → mart_price_trends=238, mart_seasonal=35, mart_geo=34, mart_corr=165 |
| 2.4.3 | Log all counts to `logs/transform.log` + update `pipeline.lineage.mart_rows` | ✅ | Written to issues_log JSON in lineage |

**Validation**: All dbt tests pass (33/33). Row count chain: 325,239 raw → 325,239 staging → 325,239 int → 2,116 filtered → mart models. Data limitation documented: Rice/Sugar/Flour have no market-level `actual` prices — only national avg (market_id=974). Only Cooking Oil has province-level actual prices (4,236 rows across 5 island groups). `mart_commodity_correlation` provides all 4 commodities at national level (158 months).

## Phase 2.5 — Post-Implementation Corrections
> **Sequential** — identified during gap analysis after Phase 2 completion. Runs before Phase 3 to ensure downstream pages have correct data.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.5.1 | Join `int_islamic_calendar` to `mart_seasonal_patterns` — add 5 Ramadan proximity flags (T-3 to T+1) | ✅ | LEFT JOIN via STRFTIME month string matching on eid_month, t_minus_1/2/3, t_plus_1 |
| 2.5.2 | Add `yoy_change_index` to `mart_geo_disparity` — LAG-based year-over-year delta of price_index_vs_java | ✅ | PARTITION BY commodity, island_group, admin1 ORDER BY year |
| 2.5.3 | Create `mart_correlation_summary` — Pearson r for all 6 commodity pairs at lags 0-3 | ✅ | 30 rows (6 pairs × 5 lags including lag 0). Corr() from lagged values in mart_commodity_correlation |
| 2.5.4 | Centralize `DATE_TRUNC('month', date) AS month` in `int_prices_normalised` — refactor 4 mart models to use it | ✅ | Eliminates duplication risk; all marts now reference pre-truncated column |
| 2.5.5 | Fix `complete_lineage()` — add `pipeline_status` column, stop overwriting `ingest_status` | ✅ | New column tracks overall run outcome; per-phase fields untouched |
| 2.5.6 | Add intermediate schema.yml — dbt tests for all 3 intermediate models | ✅ | accepted_values, not_null, unique tests |
| 2.5.7 | Add dbt schema tests for new columns (flag_ramadan_*, pearson_r, yoy_change_index) | ✅ | not_null on all new columns |
| 2.5.8 | Update docs: LEARNINGS.md (§39-42), AGENTS.md, data_validation.md, issues_log.md, implementation-plan.md | ✅ | All 5 docs updated with gap-corrected information |
| 2.5.9 | Re-run `dbt run` + `dbt test` — verify all tests pass after changes | ⬜ | Must re-verify after all SQL edits |

**Key Deliverable**: 3 mart model corrections + 1 new model + 1 intermediate refactor + lineage table fix + all docs current.

---

## Phase 3 — Forecasting (2 days)
> **Sequential** — depends on Phase 2 (mart models). Phase 4 (EDA) and Phase 7 (doc start) can run alongside this.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | `forecast/run_forecast.py` — AutoARIMA + AutoETS per commodity on national avg prices | ⬜ | Compare AIC/BIC, cross-validation MAE on 12-month holdout |
| 3.2 | Islamic calendar exogenous variables (Ramadan/Eid binary flags) | ⬜ | Add to training data before model fit |
| 3.3 | Generate 6-month forecast (Jun–Nov 2024) with 95% CI | ⬜ | Output: `{date, commodity, forecast_price, lower_95, upper_95, model_used}` |
| 3.4 | Validate forecast output: check for NaN, negative prices, CI bounds reversal (lower > upper) | ⬜ | `validate_forecast()` logs issues to `logs/forecast.log` + updates `pipeline.lineage.forecast_status` |
| 3.5 | Create **`analysis/forecast_experimentation.py`** (marimo notebook, optional) | ⬜ | Interactive model selection: compare models per commodity live |
| 3.6 | Write `docs/model_methodology.md` | ⬜ | 7 required sections per plan |

**Key Deliverable**: `forecast.json` (validated) + `docs/model_methodology.md`

---

## Phase 4 — EDA (SCAN Framework) (1–2 days)
> **Parallel** — can start after Phase 1 (staging). Runs alongside Phase 2 + Phase 3. No dependency on mart models.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 4.1 | Create **`analysis/eda.py`** (marimo notebook) with 6 aggregate analyses: annual avg per commodity, YoY%, volatility (std/mean), island group price index vs Java, month-of-year avg, cross-commodity correlation matrix | ✅ | 15 cells, SCAN structure |
| 4.1a | **Pipeline-aware data loading** — Cell 2 reads from `raw.*` tables (not CSV), checks `pipeline.lineage`, shows run_id | ✅ | Follows `data_validation.py` fix pattern (issues_log.md #5) |
| 4.1b | **Colorblind palette + dash patterns + markers** — consistent `PALETTE_MAP`/`DASH_MAP`/`SYMBOL_MAP` across all charts | ✅ | 4-color categorical (#4C72B0/#DD8452/#55A868/#C44E52), solid/dash/dot/dashdot |
| 4.1c | **IDR number formatting** — tickformat="~s" (15K, 10M) on all price axes | ✅ | Applied via `update_layout(yaxis=dict(tickformat='~s'))` |
| 4.1d | **Insight-led annotations** — dynamic titles with computed % values, vrect season bands, vline annotations | ✅ | N1: "Surged 53%", N2: "X% Lower During Harvest", N3: "X% Premium During Ramadan" |
| 4.1e | **A4 small multiples** — one subplot per commodity with ±1 std dev error ribbon | ✅ | Replaced single 4-line chart with `make_subplots(2,2)` |
| 4.1f | **A2 bar chart** — volatility as grouped bars instead of line chart | ✅ | Discrete annual CV% better as bars |
| 4.1g | **YoY heatmap** — `px.imshow` replaces plain table for YoY% | ✅ | Pattern spotting: years × commodities |
| 4.2 | Document coverage gaps in `docs/insights_log.md` | ✅ | 5 gaps documented |
| 4.3 | Identify notable segments: cooking oil 2022 shock, rice harvest seasonality, sugar Ramadan effect, Eastern Indonesia premium | ✅ | 4 N-sections in notebook |
| 4.4 | Populate insights log with minimum 6 findings (contextual/directional/actionable) | ✅ | 7 findings, each with metric, dimension, quantified value, type, stakeholder |

**Marimo**: `marimo edit analysis/eda.py`
**Key Deliverable**: `docs/insights_log.md` with ≥6 findings

---

## Phase 5 — Deep Dive Analysis (North Star Method) (2–3 days)
> **Sequential** — depends on Phase 4 (EDA findings feed into deep dives). Phase 7 can run alongside.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5.1 | Create **`analysis/deep_dive.py`** (marimo notebook) with 4 deep dive sections | ⬜ | MARIMO-DRIVEN — interactive widgets for date range, commodity, island group |
| 5.2 | **Q1 — Price Trends + Forecast**: annual trend plot, structural breaks (2008, 2022), decompose trend/seasonal/residual, layer 6-month forecast with CI, procurement action zone identification | ⬜ | Expected: Cooking oil CAGR, forecast stability assessment |
| 5.3 | **Q2 — Seasonal Patterns**: align years to Islamic calendar, price index at T-3 to T+1 relative to Eid, avg premium per commodity, harvest season discount, year-end spike | ⬜ | Expected: Sugar Ramadan premium, rice harvest discount window |
| 5.4 | **Q3 — Geographic Disparity**: island group price index vs Java, narrowing/widening trend, province-level drill-down, lowest-cost provinces per commodity | ⬜ | Expected: Eastern Indonesia premium magnitude + trend direction |
| 5.5 | **Q4 — Commodity Correlations**: cross-correlation at lags 0–3, strongest leading pair, rolling 3-year stability, pre/post 2022 comparison | ⬜ | Expected: Rice → Flour lead relationship, post-2022 break analysis |
| 5.6 | Populate insights log with quantified findings from all 4 deep dives | ⬜ | Each finding uses template: metric, dimension, quantified finding, type, stakeholder, recommendation, confidence |

**Marimo**: `marimo edit analysis/deep_dive.py`

---

## Phase 6 — Dashboard (Shadboard + Next.js) (3–4 days)
> **Sequential (pages)** — chart implementation depends on Phase 2 (mart data) + Phase 3 (forecast) exported JSON. §6.6 init is independent.

### Page 1 — Price Trends & Forecast
| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.1.1 | KPI cards: current price + YoY% + sparkline per commodity (4 cards) | ⬜ | Wireframe [4] — always visible regardless of filter |
| 6.1.2 | Main trend + forecast chart (Recharts ComposedChart, line + area for CI) | ⬜ | Wireframe [5] — dashed separator, shaded CI, commodity toggle |
| 6.1.3 | Procurement action zone (BUY/HOLD/WATCH signals) | ⬜ | Wireframe [6] — forecast lower bound vs current price |
| 6.1.4 | YoY inflation table (sortable, red/green cells) | ⬜ | Wireframe [7] |
| 6.1.5 | Model limitations footnote (always visible) | ⬜ | Wireframe [8] |

### Page 2 — Seasonal Patterns
| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.2.1 | Procurement timing callout cards (commodity × driver) | ⬜ | Wireframe [4] — spike magnitude + consistency score |
| 6.2.2 | Seasonal heatmap: month × commodity, Gregorian calendar | ⬜ | Wireframe [5] — single-hue scale, 48 cells |
| 6.2.3 | Ramadan overlay chart: price index T-3 to T+1, all years overlaid | ⬜ | Wireframe [6] — thin year lines + bold avg line, 2022 outlier labelled |
| 6.2.4 | Harvest season chart (rice discount) + year-end chart | ⬜ | Wireframe [7][8] — shown conditionally by driver toggle |
| 6.2.5 | Seasonal summary table (TanStack, sortable) | ⬜ | Wireframe [9] — lead time column is most actionable |

### Page 3 — Geographic Disparity
| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.3.1 | KPI cards: price index per island group (5 cards) | ⬜ | Wireframe [4] — Java=100, clickable to filter |
| 6.3.2 | Indonesia choropleth map (GeoJSON + Recharts/D3) with year slider + animate | ⬜ | Wireframe [5] — island group granularity, year animation |
| 6.3.3 | Island group comparison line chart (5 series, Java baseline) | ⬜ | Wireframe [6] — gap narrowing/widening readability |
| 6.3.4 | Province drill-down table (TanStack, coverage column) | ⬜ | Wireframe [7] — honesty column for data gaps |

### Page 4 — Commodity Signals
| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.4.1 | Leading indicator callout cards (top 2 relationships, plain language) | ⬜ | Wireframe [4] — Category Manager audience, no r values |
| 6.4.2 | Correlation matrix heatmap (4×4, asymmetric, lag selector) | ⬜ | Wireframe [5] — row leads column label |
| 6.4.3 | Commodity pair scatter chart (pre/post 2022 dot split) | ⬜ | Wireframe [6] |
| 6.4.4 | Rolling correlation stability chart (3-year window, 2022 marker) | ⬜ | Wireframe [7] — most analytically honest visual |
| 6.4.5 | Procurement implication card (plain language, post-2022 caveat) | ⬜ | Wireframe [8] — analytical centrepiece of page |
| 6.4.6 | Full correlation detail table (TanStack, pre/post 2022 columns) | ⬜ | Wireframe [9] — differentiation column |

### 6.6 Dashboard Init (moved from Phase 0)
> **Parallel** — zero data dependency. Can run any time after Phase 0. No need to wait for pipeline phases.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.6.1 | Init Next.js from Shadboard starter-kit in `/dashboard` | ⬜ | `npx shadcn@latest init`, 4-page nav route group |
| 6.6.2 | Strip Shadboard boilerplate (avatar, command palette, fullscreen, theme switch, etc.) | ⬜ | Per LEARNINGS.md §34 — surgical removal of dead code |
| 6.6.3 | Configure `next.config.mjs` for static export | ⬜ | `output: 'export'` |

### Global Filters + Export + Deploy
| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.7.1 | Global filters: Commodity, Island Group, Year Range slider | ⬜ | Persist across all 4 pages |
| 6.7.2 | `export/export_json.py` — query all 4 mart models + forecast → static JSON | ⬜ | Writes to `dashboard/public/data/` |
| 6.7.3 | Add `verify_export()` to export_json.py — validates mart row count matches JSON record count per file | ⬜ | Checks: missing columns, row count, nulls in critical fields |
| 6.7.4 | Log export results to `logs/export.log` + update `pipeline.lineage.export_status` | ⬜ | |
| 6.7.5 | Build: `npm run build` | ⬜ | |
| 6.7.6 | Deploy to Cloudflare Pages (connect GitHub repo) | ⬜ | |
| 6.7.7 | Verify live URL on mobile | ⬜ | |

---

## Phase 7 — Forecasting Methodology Documentation (1 day)
> **Parallel** — can start once Phase 3 model decisions are made (AutoARIMA vs AutoETS, CV results). Runs alongside Phase 4–6.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 7.1 | Problem statement: grain, horizon, what/why | ⬜ | `docs/model_methodology.md` |
| 7.2 | Data preparation: national avg, actual prices only, monthly grain, Islamic calendar regressors | ⬜ | |
| 7.3 | Model candidates: AutoARIMA, AutoETS, AutoTheta — what each does | ⬜ | |
| 7.4 | Model selection: CV approach, holdout, MAE/RMSE, final model per commodity | ⬜ | |
| 7.5 | Confidence intervals: plain language explanation of 95% CI, procurement action zone | ⬜ | |
| 7.6 | Known limitations: 5 items per plan | ⬜ | Gov price controls, tariff shocks, El Niño, calendar approximation, policy unpredictability |
| 7.7 | How to re-run: step-by-step retraining instructions | ⬜ | |

---

## Phase 8 — Insights, Recommendations & Write-up (1 day)
> **Sequential** — depends on all prior phases. Reads insights from Phase 4+5, screenshots from Phase 6, methodology from Phase 7.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 8.1 | README: business scenario (3–4 sentences) | ⬜ | |
| 8.2 | README: exec-driven questions (4 bullets) | ⬜ | |
| 8.3 | README: pipeline architecture (Mermaid diagram) | ⬜ | Raw CSV → DuckDB → dbt → statsforecast → export_json.py → Shadboard → CF Pages |
| 8.4 | README: dbt lineage graph screenshot | ⬜ | |
| 8.5 | README: key findings (4–6 quantified bullets) | ⬜ | |
| 8.6 | README: dashboard preview (4 screenshots) | ⬜ | |
| 8.7 | README: recommendations mapped to stakeholders | ⬜ | Procurement Analyst + Category Manager |
| 8.8 | README: data limitations + validation findings | ⬜ | Pre-empt interview questions |
| 8.9 | README: forecasting methodology summary + link | ⬜ | |
| 8.10 | README: reproduction instructions | ⬜ | |
| 8.11 | README: lessons learned | ⬜ | Honest reflection |
| 8.12 | Finalize `docs/insights_log.md` with all 3 insight types: contextual, directional, actionable | ⬜ | |
| 8.13 | Live URL pinned in README and GitHub repo description | ⬜ | |

---

## Validation Checklist

- [x] Phase 0: Data validation checks completed, scoping decisions documented
- [x] `pipeline.lineage` table created with run_id tracking
- [x] Row count reconciliation at every pipeline stage
- [x] Row-level quality flags carried through to mart models
- [x] dbt staging tests pass (not_null, accepted_values, positive_values, unique)
- [x] dbt mart tests pass (not_null, accepted_values, positive_values)
- [x] dbt docs generate produces lineage graph
- [x] Phase 2.5 corrections: Ramadan flags joined, YoY delta added, correlation summary created, DATE_TRUNC centralized, lineage table fixed
- [ ] Forecast output validated (no NaN, negative, or reversed CI)
- [ ] Export verified: JSON record count == mart row count
- [ ] EDA: ≥6 findings in insights log
- [ ] Deep dive: all 4 exec questions answered with quantified findings
- [ ] All 4 dashboard pages functional with global filters
- [ ] Page 1: forecast with CI, buy signals, YoY table, limitations footnote
- [ ] Page 2: action cards, heatmap, Ramadan overlay, driver toggle
- [ ] Page 3: choropleth map with year slider, province table with coverage column
- [ ] Page 4: correlation matrix, scatter, stability chart, implication card
- [ ] Mobile responsive on all pages
- [ ] Static export build passes
- [ ] Cloudflare Pages deployment successful
- [ ] README complete with live URL

---

## Key EDA Findings (To Be Confirmed)

(Placeholder — populated after Phase 4)

1. **Cooking oil structural break**: 2022 global supply shock + export ban created permanent level shift
2. **Sugar Ramadan premium**: Most consistent seasonal effect across 17 years
3. **Eastern Indonesia premium**: Persistent geographic disparity, narrowing/widening per commodity

---

## Commit Strategy

Solo portfolio project — commit per phase on `main`. No branches needed unless experimenting.

| Phase | Commit Message | Scope |
|-------|---------------|-------|
| Phase 0 | `feat: project setup + data validation checkpoint` | Folder structure, dbt init, config, validation |
| Phase 1 | `feat: ingest & dbt staging models` | Pipeline layer 1 |
| Phase 2 | `feat: dbt intermediate + mart models` | Analytical core |
| Phase 2.5 | `fix: post-implementation corrections (ramadan, correlation, lineage, docs)` | Gap fixes |
| Phase 3 | `feat: forecast models + methodology doc` | Modelling |
| Phase 4 | `feat: EDA notebook + insights log` | Analysis |
| Phase 5 | `feat: deep dive analysis notebook` | Analysis |
| Phase 6 | `feat: dashboard (Next.js + Shadboard + export)` | Frontend |
| Phase 7 | `docs: methodology documentation` | Docs |
| Phase 8 | `docs: README, insights, recommendations` | Final packaging |

**Rules**:
- Conventional Commits (`feat:`, `docs:`, `fix:`)
- No `--no-verify` unless hooks are slow
- Phase 6 can be split per page if diff is large
- Push after each phase for backup + GitHub activity graph

---

## Blockers & Notes

| Date | Blocker | Resolution |
|------|---------|------------|
| 2026-05-25 | **Data Finding**: Rice/Sugar/Flour have no market-level `actual` prices — only national average (market_id=974, price_flag='actual'). Cooking Oil is the only commodity with province-level actual price data (4,236 rows). | Accepted as WFP data constraint. `mart_commodity_correlation` provides all 4 at national level (158 months). Dashboard Pages 2/3 will document limitation. |
