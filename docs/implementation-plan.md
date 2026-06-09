# Implementation Plan — Indonesia Food Price Intelligence

## Project Meta

| Attribute | Value |
|-----------|-------|
| **Start Date** | 2026-05-22 |
| **Data First Accessed** | 2026-05-22 |
| **Data Source** | WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0) |
| **Target Completion** | ~16–20 working days |
| **Status** | Phase 0–5 ✅, Phase 5f ✅, Phase 3f ✅, Phase 5g ✅. **Phase 6**: Pages 1–2 complete (Price Trends & Forecast + Seasonal Patterns). UX audit pass (v5) on Page 1. Pages 3–4 pending. |
| **Stack** | Python → DuckDB → dbt → statsforecast → Marimo → Static JSON → **Marimo (native UI, mo.ui + mo.state)** → **Hugging Face Spaces (WASM)** |

### Parallelization Opportunities
| Phase | Can Start After | Runs Parallel With | Saves |
|-------|----------------|-------------------|-------|
| Phase 4 (EDA) | Phase 1 done (staging data available) | Phase 2 + Phase 3 | ~3–5 days |
| Phase 7 (Methodology Doc) | Phase 3 started (model decisions known) | Phase 4–6 | ~2–3 days |
| §6.6 Dashboard Init | **Phase 0** (scaffolding, zero data dependency) | Phase 1–5 | ~1 day on back-end |

**Sequential chain** (must wait): Phase 0 → 1 → 2 → 2.5 → 3 → 6 (pages). Phase 4 and 7 slot alongside, not behind.
> **Current**: Phase 0+1 ✅ → Phase 2 ✅ → Phase 2.5 ✅ → Phase 3 ✅ → Phase 3e ✅ → Phase 4 ✅ → Phase 5 ✅ → Phase 5f ✅ → Phase 3f ✅ → Phase 5g ✅ → **Phase 6 🟡 (Pages 1–2 complete, Pages 3–4 pending)**

---

## Phase 0 — Project Setup & Data Validation Checkpoint

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Create folder structure | ✅ | `data/raw/`, `ingest/`, `transform/`, `forecast/`, `export/`, `analysis/`, `logs/`, `dashboard/public/data/` (dashboard/ deleted 2026-06-08, will re-create on rebuild) |
| 0.2 | Create `pyproject.toml` + `uv sync` | ✅ | uv-native: duckdb, dbt-duckdb, statsforecast, marimo, pandas, plotly |
| 0.3 | Init dbt project in `/transform` | ✅ | `dbt init`, configure profiles.yml for DuckDB |
| 0.4 | Init Dash app skeleton in `/dashboard` (`app.py`, `pages/`, `components/`, `data_access.py`, `_data/snapshot.py`, `Dockerfile`, `README_HF.md`, `.dockerignore`) | ⬜ | **DEFERRED** to Phase 6 — plan documented 2026-06-02. **SUPERSEDED 2026-06-08** — rebuild as Marimo notebook (no Dash, no Docker). See §6.MARIMO. |
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
| 1.1.7 | `run_pipeline.py` — orchestrator chaining ingest → dbt run → dbt test → row-count reconciliation → lineage | ✅ | Closes duckdb before spawning dbt subprocess to avoid file-lock. Guards `conn.close()` per LEARNINGS.md §24. |
| 1.1.8 | Engineering fixes: quote-wrap SQL idents, idempotent loads (DROP TABLE + CREATE TABLE), absolute paths for subprocess safety, raise instead of sys.exit in reconcile | ✅ | `ingest/config.py` uses `'"{k}" = ?'` in dynamic SET. `load_raw.py` uses `DROP TABLE IF EXISTS` + `CREATE TABLE AS` for clean re-runs. |

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
**Orchestration**: `uv run python run_pipeline.py` runs full pipeline end-to-end (16s total).
**Fix: data_validation.py** — reads from existing `raw.*` tables in DuckDB instead of reloading CSVs. Shows ingest run info from lineage table.
**Fix: docs/issues_log.md** — structured issue tracker documenting 6 pipeline/data quality issues with resolution status.
**Fix: docs/LEARNINGS.md** — 3 new sections (§36 quote-wrapping, §37 idempotent loads, §38 pipeline reconciliation).

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

**Validation**: All dbt tests pass (55/55 + 4 exposures). Row count chain: 325,239 raw → 325,239 staging → 325,239 int → 2,116 filtered → mart models. Data limitation documented: Rice/Sugar/Flour have no market-level `actual` prices — only national avg (market_id=974). Only Cooking Oil has province-level actual prices (4,236 rows across 5 island groups). `mart_commodity_correlation` provides all 4 commodities at national level (158 months).

**dbt audit per dbt-agent-skills** — post-Phase 2.5 evaluation closed 9 gaps:
- FK `relationships` test (Tier 1 critical), `packages.yml`, `_exposures.yml`, `_seeds.yml`
- `filter_out` invariant singular test, `accepted_values` on `unit`
- Dead config removal, unused column cleanup, expanded source column docs
- All 11 generic tests verified with correct `arguments:` syntax for dbt 1.11.11

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
| 2.5.9 | Re-run `dbt run` + `dbt test` — verify all tests pass after changes | ✅ | 66/66 pass, 0 errors, 0 warnings |
| 2.5.10 | **dbt Labs audit** — 6-dimension evaluation per dbt-agent-skills; close 9 gaps | ✅ | See AGENTS.md § "dbt Implementation Evaluation" for full delta |

**Key Deliverable**: 3 mart model corrections + 1 new model + 1 intermediate refactor + lineage table fix + all docs current + 9 audit gaps closed (33→55 tests).

---

## Phase 3 — Forecasting + Export (2–3 days)
> **Sequential** — depends on Phase 2 (mart models). Phase 7 (doc start) runs alongside this.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | Add `_loaded_at` column to `load_raw.py` | ✅ | Already implemented — flag was stale |
| 3.2 | `forecast/run_forecast.py` — AutoARIMA + AutoETS | ✅ | 403-line script, per-commodity holdout |
| 3.3 | Islamic calendar exogenous variables | ✅ | eid_month/t-1/t-2/t-3 binary flags |
| 3.4 | Generate 6-month forecast with 95% CI | ✅ | Output: `{date, commodity, forecast_price, lower_95, upper_95, model_used}` |
| 3.5 | Validate forecast output | ✅ | `validate_forecast()` NaN/negative/CI reversal checks |
| 3.6 | `export/export_json.py` | ✅ | 5 mart models → JSON |
| 3.7 | `verify_export()` row count check | ✅ | DB count == JSON record count |
| 3.8 | Export logging + lineage update | ✅ | `logs/export.log` + `pipeline.lineage.export_status` |
| 3.9 | Update `run_pipeline.py` — forecast + export steps | ⚠️ | Step tracking bug — fixed in 3.12 |
| 3.10 | `analysis/forecast_experimentation.py` | ✅ | 261-line marimo notebook |
| 3.11 | `docs/model_methodology.md` | ✅ | 190-line doc, 7 required sections |
| 3.12 | **Fix: `run_pipeline.py` error handler sets wrong column** | ✅ | Tracks active step; updates correct `*_status` on failure |
| 3.13 | **Fix: Deduplicate `pipeline.lineage` DDL** | ✅ | Full schema in forecast/export (matches `config.py`) |
| 3.14 | **Fix: Hardcoded forecast metadata dates** | ✅ | Computed dynamically from actual data per commodity |
| 3.15 | **Fix: Track skipped commodities in forecast status** | ✅ | Sets `completed_with_warnings` when commodities skipped |
| 3.16 | **Fix: DuckDB connection lock in export** | ✅ | `read_only=True` in export connection |
| 3.17 | **Fix: Add `t_minus_3` to `forecast_experimentation.py`** | ✅ | Parity with production script |
| 3.18 | **Fix: Standardize status value** | ✅ | `completed_with_warnings` in both forecast + export |

**Key Deliverable**: `forecast.json` (validated) + all 5 mart JSONs + `docs/model_methodology.md` + 7 gap fixes

### Phase 3f — Pipeline Gap-Closing (post-Phase-5f)
> **Sequential** — gap assessment across all non-dashboard phases after Phase 5f completion. Fixes span dbt, forecast, export, orchestration, and Python config.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3f.1 | **P1: Ramadan `t_plus_1` cross-year bug** — Dec Eid `t_plus_1` (Jan next year) missed by single-year join | ✅ | Changed ramadan CTE from `EXTRACT(YEAR FROM m.month) = c.year` to `IN (c.year, c.year + 1)` with `BOOL_OR()` in `mart_seasonal_patterns.sql` |
| 3f.2 | **P1: Forecast data source divergence** — forecast uses all price data (incl. `aggregate`) while dashboard plots `actual`-only | ✅ | Added `data_source_note` to `forecast.json` metadata documenting the divergence transparently |
| 3f.3 | **P2: Hardcoded `"2024-06-01"` in `get_future_exog()`** — 2 instances in `run_forecast.py` | ✅ | Replaced with commodity-specific `forecast_start` computed from `hist_id["ds"].max() + 1 month` |
| 3f.4 | **P2: Fragmented `run_id`** — forecast and export generated separate IDs from pipeline orchestrator | ✅ | `run_pipeline.py` passes `run_id` as CLI arg; both scripts accept `sys.argv[1]` with fallback |
| 3f.5 | **P2: `transform.log` empty** — dbt stdout not routed to dedicated log | ✅ | Replaced in-python handler with direct file append via `subprocess` `--log-path` flag |
| 3f.6 | **P3: 85-line `fit_and_forecast()`** — violated LEARNINGS.md §64 function-split pattern | ✅ | Extracted `prepare_commodity_data()` + `select_best_model()` helpers |
| 3f.7 | **P3: `mart_geo_disparity` Rice/Sugar/Flour filter undocumented** — only Cooking Oil has market-level actual prices | ✅ | Added inline SQL comment + column description in `_marts__models.yml` |
| 3f.8 | **P3: `mart_correlation_summary` asymmetry** — 6 directional pairs, not all 12 reverse pairs | ✅ | Documented asymmetry with header note + expanded column descriptions |
| 3f.9 | **P3: PEP 723 `==` exact version pins** — brittle for marimo notebooks | ✅ | Changed `==` to `>=` in `analysis/eda.py` + `analysis/forecast_experimentation.py` |
| 3f.10 | **P4: Lineage DDL duplicated** — same `CREATE SCHEMA` + `LINEAGE_TABLE_DDL` in forecast and export | ✅ | Replaced inline DDL with `ensure_lineage_table()` call from `ingest/config.py` |
| 3f.11 | **Verify all fixes** — run full pipeline end-to-end | ✅ | `dbt build` 66/66 PASS. Pipeline 59.4s. Unified `run_id` across all phases. |

**Key Deliverable**: 11 gaps closed across dbt (1), forecast/export (7), orchestration (2), Python config (1). Full pipeline verified end-to-end.

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
| 4.5 | **G8: Pipeline quality flag distribution** — new C2 cell querying `wfp_intermediate.int_prices_normalised` for all 5 filter flags + pass rate | ✅ | 325,239 total → 2,116 pass (0.65% yield). Non-target = 78% of filtered rows |
| 4.6 | **G5: USD price trends** — extend A1 to include USD-denominated price line chart for FX-adjusted comparison | ✅ | Confirms IDR trends are real, not inflation-driven |
| 4.7 | **G4: Lagged correlation matrix** — new A5b cell reading `wfp_marts.mart_correlation_summary`, showing all 6 pairs × 4 lags | ✅ | Best lag per pair identified (Oil→Flour: lag 3 strongest at r=0.8885) |
| 4.8 | **G7: Market coverage by island group** — new A6 cell counting distinct markets + provinces per island group | ✅ | Java: 72 markets, 6 provinces. Total 214 Cooking Oil markets |
| 4.9 | **G2: Islamic calendar Ramadan** — refactored N3 Sugar section to join `wfp_intermediate.int_islamic_calendar` by year instead of hardcoded [3,4,5] | ✅ | eid_month + T-1/2/3 computed per year. Ramadan shifts ~11 days/yr |
| 4.10 | **G3: Forecast quality** — new N5 cell reading `forecast.json`, showing holdout MAE per commodity + model selection from metadata | ✅ | Rice best accuracy, Cooking Oil worst (post-2022 structural break) |
| 4.11 | **G1+G6: Mart reconciliation + export validation** — new R1+R2 cells comparing EDA mart queries vs JSON record counts | ✅ | All 5 mart→JSON exports verified. Row-count chain: raw → staging → int → marts |
| 4.12 | Update summary table to 10 findings + `insights_log.md` with gap-closing results | ✅ | 3 new findings: pipeline yield, forecast accuracy, export integrity |

**Marimo**: `marimo edit analysis/eda.py`
**Key Deliverable**: `docs/insights_log.md` with ≥10 findings. Pipeline reconciliation against all 5 marts + JSON exports.

---

## Phase 4.5 — EDA Notebook Improvement Plan (1 day)
> **Sequential** — structural review of `analysis/eda.py` against `retail_sales/analysis/eda_notebook.py` patterns. Leverages existing learnings (§57–66, AGENTS.md §385–403) — does NOT re-document patterns already followed.

### Already Followed (existing patterns in `analysis/eda.py`)

| Pattern | Source | Status |
|---------|--------|--------|
| Query marts, not duplicate pipeline logic | LEARNINGS.md §57 | ✅ Already queries `int_prices_normalised` directly |
| `mo.persistent_cache` + named cells | LEARNINGS.md §58 + AGENTS.md §390/394 | ✅ `def data_load():` with `@mo.persistent_cache` |
| Interactive filters (dropdown + slider) | LEARNINGS.md §59 + AGENTS.md §400 | ✅ `def filters():` with commodity/island/year controls |
| PEP 723 script header | LEARNINGS.md §62 + AGENTS.md §387 | ✅ `# /// script` block present |
| Script mode detection | LEARNINGS.md §63 + AGENTS.md §388 | ✅ `is_script_mode` in setup cell |
| One transformation per cell | LEARNINGS.md §64 + AGENTS.md §390 | ✅ 18 cells, single concern each |
| `mo.stop()` for empty data | LEARNINGS.md §65 + AGENTS.md §392 | ✅ In `data_load` cell after query |
| Named cells (not `__`) | AGENTS.md §389 | ✅ All cells use `def setup():`, `def data_load():`, etc. |

### Completed

| # | Change | Commit |
|---|--------|--------|
| 4.5.1 | ✅ `fmt_idr()`, `fmt_pct()`, `fmt_short_idr()` added to `setup()` cell — all inline f-strings updated | `df28dc5` |
| 4.5.2 | ✅ `> **Insight:**` blockquote added to all 15 analytical cells that were missing it | `df28dc5` |
| 4.5.3 | ✅ All 19 sections renumbered from `### A1:` → `## 01 — A1:` format | `df28dc5` |
| 4.5.4 | ✅ 12 derived values (CAGR, peak/trough, best/worst MAE) pre-computed and interpolated into narrative | `df28dc5` |
| 4.5.5 | ✅ All insights rewritten from descriptive to prescriptive (e.g., "Front-run Ramadan by T-2 months") | `df28dc5` |
| 4.5.6 | ✅ `reconciliation()` refactored to return-based cell wrapped in `mo.lazy()` — queries deferred until visible | `df28dc5` |
| 4.5.7 | ✅ Summary findings table updated with `(see §N)` cross-references to all 19 chart sections | `df28dc5` |

**Key Deliverable**: ✅ `analysis/eda.py` (976 lines) — formatters, insight callouts, actionable recommendations with computed stats, section-numbered hierarchy, `mo.lazy()` on reconciliation, cross-referenced findings.

---

## Phase 5 — Deep Dive Analysis (North Star Method) (2–3 days)
> **Sequential** — depends on Phase 4 (EDA findings feed into deep dives). Phase 7 can run alongside.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5.1 | Create **deep dive analysis** (merged into `analysis/eda.py` with Phase 4 EDA) | ✅ 2026-05-26 | 40+ cells: Phase 4 SCAN (stakeholder, coverage, pipeline, aggregates, notable) + Phase 5 North Star (Q1–Q4 deep dives with forecast, ramadan, geographic, correlation) + summary |
| 5.2 | **Q1 — Price Trends + Forecast**: annual trend plot, structural breaks (2008, 2022), decompose trend/seasonal/residual, layer 6-month forecast with CI, procurement action zone identification | ✅ | Quantified: Rice CAGR 6.7% (highest), flat near-term forecasts (all <1% Δ), wide CIs (12–29%), Cooking Oil 60.7% apparent seasonality = 2022 artifact |
| 5.3 | **Q2 — Seasonal Patterns**: align years to Islamic calendar, price index at T-3 to T+1 relative to Eid, avg premium per commodity, harvest season discount, year-end spike | ✅ | Quantified: Sugar Ramadan premium 2.7% (highest), Rice harvest discount confirmed, Ramadan effect smaller than generic seasonality after Islamic calendar correction |
| 5.4 | **Q3 — Geographic Disparity**: island group price index vs Java, narrowing/widening trend, province-level drill-down, lowest-cost provinces per commodity | ✅ | Found: Only Cooking Oil has market-level actual data for geographic analysis. Provincial gap 43.1% (Bangka Belitung vs Gorontalo). Rice/Sugar/Flour limited to national aggregate |
| 5.5 | **Q4 — Commodity Correlations**: cross-correlation at lags 0–3, strongest leading pair, rolling 3-year stability, pre/post 2022 comparison | ✅ | Quantified: Pre-2022 r=0.73–0.88. Post-2022 not measurable (Rice/Sugar/Flour actual data ends 2020). Best lag: oil↔flour at 3mo (r=0.8885) |
| 5.6 | Populate insights log with quantified findings from all 4 deep dives | ✅ 2026-05-26 | 6 new findings (#8–13) appended to `docs/insights_log.md` — all quantified with actual data |
| 5.7 | Update `docs/model_methodology.md` — add Deep Dive Validation subsection | ✅ 2026-05-26 | Added cross-reference: forecast vs actual decomposition, wide CI assessment, procurement action zone framework |
| 5.8 | **Phase 5 gap-closing**: stale doc refs (`deep_dive.py` ×3 files), summary table DD§→Q1-Q4, `mo.stop()` guards, Ramadan conn reuse, Eastern Indonesia 2015+ filter, unused `is_script_mode` removed | ✅ 2026-05-26 | 3 doc files fixed + 6 code fixes in `eda.py`. Added LEARNINGS.md §67 (merge-delete sweep pattern). |
| 5.9 | **P0 fix: Hardcoded DuckDB paths** — replaced `__db_path` (module-level `__` prefixed, filtered by marimo) with `PROJECT_DB_PATH` computed inside `setup()` cell and returned through DAG | ✅ 2026-05-26 | `analysis/eda.py` (9 occurrences), `analysis/data_validation.py` (1), `analysis/forecast_experimentation.py` (1). Marimo filters `__` names from cell namespaces. |
| 5.10 | **P1 fix: Missing pyproject deps** — `numpy>=1.26.0` + `scipy>=1.11.0` added | ✅ 2026-05-26 | Required by `analysis/eda.py` scipy imports and general numpy usage in notebooks |
| 5.11 | **P1 fix: Missing `transform/snapshots/` dir** — created directory referenced by `dbt_project.yml` but non-existent | ✅ 2026-05-26 | `dbt_project.yml` references `snapshots/` path — directory must exist for dbt commands |

**Marimo**: `marimo edit analysis/eda.py` (merged Phase 4 EDA + Phase 5 Deep Dive — 40+ cells)

---

### Phase 5g — Pre-Dashboard Gap Closing (post-stack-change, 2026-06-02)
> **Sequential** — gap analysis run 2026-06-02 against `implementation-plan.md` (Phases 0–5, 7, 8), `LEARNINGS.md`, `AGENTS.md`, and current filesystem state. 13 gaps found across 3 tiers. Tier 1 = data gaps blocking dashboard pages. Tier 2 = stale docs reflecting pre-stack-change reality. Tier 3 = pipeline cleanup. Tier 4 (Phase 6 init) deferred with Phase 6. **Execution deferred at user request (2026-06-02) — plan written, will run when user gives go-ahead.** ~~**Completed 2026-06-02** — all 13 gaps closed, dbt build passes (77 tests), export verified (6 marts + forecast).~~

#### Tier 1 — Data Gaps Blocking Dashboard Pages

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5g.1 | **G1: Add `mart_price_trends_national.sql`** — new mart for national avg × commodity × month, all 4 commodities, no `island_group` filter | ✅ | Decision: option (a) per user. Cleanest; parallels existing mart pattern. Needed for Page 1 KPI cards (4 commodities) + multi-commodity trend chart. Add to `_marts__models.yml` with `not_null` + `accepted_values` tests. Add export entry to `export_json.py`. |
| 5g.2 | **G2: Vendor Indonesia provinces GeoJSON** — ~1 MB file at `dashboard/assets/indonesia_provinces.geojson` | ✅ | Source: `github.com/denyherianto/indonesia-geojson-topojson-maps-with-38-provinces` (38 provinces, public). Needed for Page 3 choropleth map. Add to `.dockerignore` keep-list to ship with HF Spaces image. |
| 5g.3 | **G3: Add pre/post-2022 correlation columns** — `pearson_r_pre_2022` + `pearson_r_post_2022` to `mart_correlation_summary` | ✅ | Decision: option (a) per user. Splits full-period Pearson r at `2022-01-01` boundary. Needed for Page 4 scatter (§6.4.3) and rolling chart (§6.4.4). Update `_marts__models.yml` column docs + add `not_null` tests. `pearson_r_post_2022` allows NULL (Flour pairs post-2022). |
| 5g.4 | **G4: Document Cooking Oil dual-forecast behavior** — clarify which forecast is primary; secondary is `post2022_robustness` trace | ✅ | User decision: show both. Primary = full-history AutoARIMA (default Page 1 trace). Secondary = `post2022_robustness` AutoARIMA (toggled via Page 1 checkbox). Update `forecast.json` `metadata` block + §6.1.2 wireframe. |

#### Tier 2 — Stale Documentation (Stack Change)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5g.5 | **G5: AGENTS.md stack sweep** — replace "Next.js + Shadboard + Cloudflare Pages" with "Plotly Dash + dash-bootstrap-components + HF Spaces" | ✅ | 6 sections: L13 (Project Overview table), L70-73 (Export + Dashboard commands), L93 (Phase Pipeline), L338 (Shared Learnings subsection), L388 (Recharts/TanStack refs), L495 (Verify Dashboard). Drop "Shared Learnings" subsection per plan §318. |
| 5g.6 | **G6: LEARNINGS.md §75 SUPERSEDED banner** — mark section as overridden; do NOT draft §81–§85 stubs (deferred to Phase 6) | ✅ | User decision: defer §81-§85 (Dash-specific learnings earned during implementation). Add banner: `> **SUPERSEDED 2026-06-02** — HF Spaces replaces Cloudflare Pages as deployment target. §80's "Plotly EDA → Plotly dashboard" parity now realized.` |
| 5g.7 | **G7: README.md + G8: project-plan.md stack sync** — mirror AGENTS.md update in 2 sister docs | ✅ | README: replace npm commands with `uv run python dashboard/app.py` (Phase 8.10/8.11). `docs/wfp-food-price-intelligence-project-plan.md`: update Stack row, Setup Commands, Phase 6 mention. |

#### Tier 3 — Pipeline Cleanup

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5g.8 | **G9: Remove dead code** — `current_step_map: dict[str, str] = {}` in `run_pipeline.py:129` | ✅ | Defined but never read/written. Pure dead state. |
| 5g.9 | **G10: Move `transform_status="running"`** to before `dbt seed` (not between seed and run) | ✅ | Currently set at `run_pipeline.py:179`, after `dbt seed` succeeds. If seed fails, lineage shows `transform_status='pending'` not `failed`. Move to immediately after Step 1 ingest completes. |
| 5g.10 | **G11: Add `dbt source freshness` step** — invoke after `dbt seed` in pipeline | ✅ | Per LEARNINGS §49. Catches stale raw loads (>72h). Cost: ~2s. `_sources.yml` config already present. |
| 5g.11 | **G12: Sync `requirements.txt` with `pyproject.toml`** — or delete it | ✅ | Currently missing `numpy`, `scipy`, `chart-studio`. Plan §322 says "auto-synced" but isn't. Recommend delete + add AGENTS.md note that pyproject is the source of truth (uv-native project). |
| 5g.12 | **G13: Normalize date format in JSON exports** — add `dt.strftime("%Y-%m-%d")` to `export_json.py:export_table()` | ✅ | 4 marts export `"2024-06-01 00:00:00"`; forecast exports `"2024-06-01"`. Single 3-line patch in `export_table()` after `fetchdf()`. Prevents dual-parser handling in Dash. |

#### Key Decisions Made (2026-06-02)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| G1 fix path | New mart `mart_price_trends_national.sql` | Keeps analytical logic in dbt; parallels existing pattern; avoids query-time unpivoting in `data_access.py` |
| G3 fix path | New columns in `mart_correlation_summary` | Single source of truth; pre/post splits in SQL is cheaper than at query time; rolls into export/JSON naturally |
| G4 Cooking Oil forecast UX | Show both; primary as default, secondary as toggleable trace | Preserves analytical integrity; lets procurement analyst see structural-break sensitivity |
| G6 LEARNINGS §81-§85 scope | Defer — write only the SUPERSEDED banner | Dash-specific patterns best earned during implementation; avoids speculative content |
| Tier 3 cleanup | Bundle into Phase 5g (defer execution but document) | Low effort, high signal; 5 small fixes, ~25 min total |

#### Execution Order (when user gives go-ahead)

| Step | Fix | Files | Effort |
|------|-----|-------|--------|
| 1 | 5g.1 (G1) — new national mart | 1 new SQL, 1 YAML, `export_json.py` entry | 20 min |
| 2 | 5g.2 (G2) — vendor GeoJSON | 1 new file + wireframe note | 10 min |
| 3 | 5g.3 (G3) — 2 columns in correlation summary | 1 SQL + 1 YAML | 15 min |
| 4 | 5g.4 (G4) — forecast metadata + wireframe | 1 Python + 1 doc | 10 min |
| 5 | 5g.5 (G5) — AGENTS.md stack sweep | 6 sections | 20 min |
| 6 | 5g.6 (G6) — LEARNINGS §75 banner | 1 doc edit | 5 min |
| 7 | 5g.7 (G7+G8) — README + project-plan sync | 2 docs | 15 min |
| 8 | 5g.8-10 (G9-G11) — pipeline cleanup | `run_pipeline.py` | 15 min |
| 9 | 5g.11 (G12) — requirements.txt | 1 file edit or delete | 5 min |
| 10 | 5g.12 (G13) — date format normalization | `export_json.py` | 5 min |

**Total**: ~2 hours of work to close all 13 gaps. ~~Execution deferred — pipeline orchestrator, exported JSONs, and dbt marts remain in current state until user triggers.~~ **All 13 gaps closed 2026-06-02.**

---

## Phase 6 — Dashboard (Marimo-native, static JSON, 4 pages) [PAGES 1–2 COMPLETE ✅ UX AUDIT PASS ✅ v5 LAYOUT FIXED ✅, PAGES 3–4 PENDING]
> **Phase 6 REBUILD: Pages 1–2 complete (2026-06-08/09).** The Marimo-native rewrite was completed 2026-06-08, deleted for clean rebuild, and **rebuilt** with Page 1 (Price Trends & Forecast) fully implemented. A UX audit identified 18 issues; all high-priority items are resolved: dead Island Group control removed, stub tabs hidden, dual commodity filter merged, buy signal methodology disclosed, year slider defaults to last 5 years, unit labels added to KPI prices, colour-blind safe signal icons, reactivity cells split, emoji removed from sortable table columns, consolidated explainer accordion card (replaced inline ⓘ icons). See LEARNINGS.md §106-113 for new learnings. **Page 2 (Seasonal Patterns)** completed 2026-06-09: 11 new cells — seasonal computations from `price_trends_national.json` (not `seasonal_patterns.json` per LEARNINGS §99), driver toggle (Ramadan/Harvest/Year-End/All), heatmap, 3 driver charts, summary table, action window KPI cards, data limitation callout, explainer accordion. Pages 3–4 are placeholders (`mo.md("Coming soon")`). Architecture blueprint preserved in `docs/handoffs/HANDOFF-dashboard-marimo-rewrite.md`. All dbt marts, forecast JSONs, and export pipeline remain intact.
>
> **Why Marimo over Vizro/Dash:** Vizro's cross-filtering promise was compelling on paper but its Pydantic configuration model made it hard to iterate on chart layout and impossible to fix Vizro-specific rendering bugs without framework patches. Marimo's reactive DAG provides equivalent cross-filter behavior (commodity/island filters propagate to all charts on the same page) without a framework abstraction layer — every chart is plain `go.Figure` inside `mo.ui.plotly()`.

### §6.MARIMO — Marimo-native Dashboard (Pages 1–2 complete 2026-06-08/09, Pages 3–4 pending)
> ✅ **Pages 1–2 rebuilt and working.** Pages 3–4 have "Coming soon" placeholders. The handoff documents are the rebuild blueprints.

**Decision rationale:** After the Vizro spike passed (§6.SPIKE), implementing the full 4-page Vizro dashboard revealed recurring pattern friction:
1. Vizro's `vm.Graph(figure=fn(...))` first-render timing bug required sidebar toggle workarounds (§98)
2. Chart customization required `@capture("graph")` wrapper boilerplate for every `go.Figure`
3. Cross-filtering was the sole reason for Vizro, but Marimo's DAG provides the same at zero framework cost
4. Vizro is 0.x with no guarantee of API stability through project completion

**Rebuild target:** Single `dashboard/app.py` Marimo notebook with:
- Static JSON data loaded via `data_static.py` (`Path(__file__)` dual-path resolution — local dev reads `dashboard/public/data/`, WASM reads `dist/data/`)
- `mo.stat()` KPI cards with Plotly sparklines
- `mo.callout()` for info/warning callouts
- `mo.ui.table()` for interactive data tables
- `mo.ui.tabs()` for page navigation
- `mo.state()` for two-sink patterns (Page 3 island filter from 2 sources, Page 4 pair selector from 3 sources)
- `mo.ui.plotly(fig)` wrapping `go.Figure` from chart helper files in `dashboard/charts/`
- All 4 commodities available in KPI cards regardless of global filter
- PEP 723 header for `marimo run` + WASM export

**Architecture documented in handoff** (`docs/handoffs/HANDOFF-dashboard-marimo-rewrite.md`):
| Feature | What's documented |
|---------|-------------------|
| Data contract | All 8 DataFrame schemas: columns, types, sources, row counts (price_trends, forecast, seasonal_patterns, geographic_disparity, commodity_correlation, correlation_summary, action_windows, islamic_calendar) |
| Dual-path resolution | Exact `Path(__file__)` resolution logic for local dev vs WASM — `_get_data_dir()` with `load_json()`/`load_csv()` helpers |
| Cross-cell scoping model | Every exported variable name per cell — 40+ names that cross Marimo's reactive DAG boundaries |
| Page 4 mo.state() sync | Five-step mechanism: state definition → 3 independent sources (matrix click, dropdown cell + downstream listener, table on_select) → 3 consumers (scatter, stability, implication) |
| Validation failure modes | 10 checks with pass/fail criteria, what the failure looks like, and how to diagnose each one |

**Verification targets for rebuild (with failure-mode diagnosis — see handoff for full table):**
| Check | Expected | Failure mode |
|-------|----------|-------------|
| `marimo check dashboard/app.py` | ✅ Pass (PEP 723 header warning only) | SyntaxError or NameError → check cell function args match `return (x,)` names |
| `ruff check dashboard/` | ✅ Clean (E501 only, 0 F821/B018/E702) | E999 syntax error → fix Python syntax; unexpected violations likely real |
| `uv run python dashboard/app.py` | ✅ Script mode exits cleanly | ModuleNotFoundError → missing PEP 723 deps; NameError → undefined cross-cell ref |
| `marimo export html-wasm -o /tmp/test.html --mode run -f` | ✅ Succeeds (60s) | Build timeout → inline data >50MB; file perm error → check output dir |

### §6.HISTORY — Superseded Stack Plans

> The Vizro feasibility spike (§6.SPIKE), data layer port (§6.DATA), wireframe evaluation (§6.WIREFRAME), the earlier Dash scaffolding (§6.6-§6.8), and the first Marimo attempt are all preserved below for git history. The Marimo-based approach (static JSON + reactive DAG) is the target architecture for rebuild — do not implement from the Dash/Vizro sections below. The Marimo blueprint is in §6.MARIMO above.

<details>
<summary><b>⚠ SUPERSEDED 2026-06-08</b> — Click to expand Vizro-era planning and Dash scaffolding. For current architecture see §6.MARIMO above (blueprint ready, code deleted for clean rebuild).</summary>

#### Vizro Feasibility Spike, Data Port, and Wireframe Resolution

**Trigger for re-decision** and the full Vizro/Dash decision matrix are historical. The Marimo-native approach was chosen instead because:
- Vizro's `vm.Graph(figure=fn(...))` first-render timing bug required sidebar toggle workarounds
- Chart customization required `@capture("graph")` wrapper boilerplate
- Marimo's reactive DAG provides equivalent cross-filtering at zero framework cost
- Marimo is more mature (0.23.7 vs Vizro 0.x) and has stable WASM export

**What was explored:**

| Phase | Detail | Status |
|-------|--------|--------|
| §6.SPIKE | 0.5-day feasibility: `uv add vizro`, spike app at `dashboard/spike/`, px.imshow wrapper, DuckDB `data_manager` wiring | ✅ Done |
| §6.DATA | Data layer port: 6 marts + forecast registered via `data_manager["key"] = lambda:` pattern | ✅ Done |
| §6.WIREFRAME | Wireframe evaluation: component mismatch, interaction patterns, GeoJSON paths, 12-resolution-task table | ✅ Done (partial — week_relative→month_relative deviation flagged) |
| §6.PAGES | Page 1 Vizro build: 4 chart files + vm.Page + Page 1 bugfixes (first-render, YoY, clip, hover) | ✅ Done (superseded by Marimo) |

### §6.HISTORY (Dash) — Superseded Dash Plan (2026-06-02, replaced same day)

<details>
<summary><b>⚠ SUPERSEDED 2026-06-02</b> — Click to expand full Dash-based Phase 6 plan. Preserved for git history + sunk-cost accounting. Do not implement from this section; use §6.STACK through §6.DOCS above.</summary>

### Page 1 — Price Trends & Forecast ✅ DONE (2026-06-02)
> **Explainer:** "Is now a good time to lock in bulk purchase contracts?" — **KPI cards** (price + YoY%), **dropdowns + slider** filter, **trend chart** with forecast overlay + CI, **BUY/HOLD/WATCH badges**, **YoY bar chart**, **model-info card**.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.1.1 | KPI cards: current price + YoY% per commodity (4 cards) | ✅ DONE | `dbc.Card` × 4 via `components/kpi_cards.py`. Data source: `load_mart("mart_price_trends_national")` — gets latest row per commodity. `compute_yoy_delta()` adds YoY% column. Color-coded: green for price drops, red for increases. Always visible regardless of filter. |
| 6.1.2 | Main trend + forecast chart (`go.Figure` + `add_vline` + CI area) | ✅ DONE | `dcc.Graph(figure=fig)`. Solid lines for actuals from `mart_price_trends_national`. Dashed lines for forecast from `forecast.json`. `add_vrect` for forecast region. `add_vline(x="2022-01-01", line_dash="dash")` + separate `add_annotation` for cooking oil export ban. CI shaded area via `go.Scatter(fill="toself")` with inverted upper/lower traces. |
| 6.1.3 | Procurement action zone (BUY/HOLD/WATCH signals) | ✅ DONE | `dbc.Card` with `dbc.Badge` per commodity. Signal logic: compute mean of 6-month forecast, compare to current price. `BUY = forecast_avg < current * 0.98` (green badge), `HOLD = abs(forecast_change) < 2%` (gray badge), `WATCH = forecast_avg > current * 1.02` (red badge). Falls back to YoY% if forecast unavailable. |
| 6.1.4 | YoY bar chart (`go.Bar` grouped by commodity) | ✅ DONE | `dcc.Graph(id="yoy-chart")`. `compute_yoy_delta()` on `mart_price_trends_national`. Grouped bars, one color per commodity. `add_hline(y=0)` baseline. Shows inflation trajectory per commodity. |
| 6.1.5 | Model info card | ✅ DONE | `dbc.Card` showing per-commodity model selection (AutoARIMA/AutoETS) and holdout MAE from `forecast.json` `metadata.models`. Read-only display, no interactivity. |
| 6.1.6 | Model limitations footnote (always visible) | ✅ DONE | `dcc.Markdown` footer in `components/layout.py:forecast_footnote()`. Text from `forecast.json` `metadata.data_source_note`. |
| 6.1.7 | Wire page to DuckDB via `data_access.load_mart("mart_price_trends_national", ...)` | ✅ DONE | Single callback with `Input` on all 3 global filters. Returns: `kpi_cards`, `trend_chart.figure`, `signal_children`, `model_info`, `yoy_chart.figure`. Forecast loaded via `load_forecast_data()` (cached JSON read). |

**Bug fixes applied during implementation:**
- Added `sys.path.insert(0, project_root)` in `app.py` to fix `ModuleNotFoundError: No module named 'dashboard'` when run as script
- Added missing `from dash import html` to all 4 page files (was causing `NameError` at runtime)
- Fixed Plotly 6.x incompatibility: `add_vline` `annotation_position` param → separate `add_annotation()` call

### Page 2 — Seasonal Patterns ✅ DONE (2026-06-09)
> **Explainer:** "When should we increase stock for each commodity?" — **heatmap** (month × commodity), **line chart** with driver bands, Ramadan **overlay chart**, sortable **summary table**, 3 **action window cards**. Toggle: Ramadan / Harvest / Year-End.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.2.1 | Seasonal heatmap: month × commodity price index | ✅ DONE | `go.Heatmap` with all 4 commodities × 12 months. Data derived from `price_trends_national.json` (not `seasonal_patterns.json` — LEARNINGS §99). Blues colorscale, zmid=0. Y-axis: commodities, X-axis: months (Jan–Dec). Computed in `seasonal_computations` cell via `_compute_seasonal_data()`. |
| 6.2.2 | Monthly price line chart (filtered by driver toggle) | ✅ DONE | 3 chart builders (`_build_ramadan_chart`, `_build_harvest_chart`, `_build_yearend_chart`) in `page2_driver_chart` cell. Conditional on `driver_toggle` radio. Ramadan uses `month_relative` T-2 to T+1 (monthly grain, not weekly — LEARNINGS §100). Harvest highlights Mar–Apr + Aug–Sep. Year-end highlights Nov–Dec. |
| 6.2.3 | Ramadan overlay chart: price index T-3 to T+1 | ✅ DONE | Merged into driver chart — `_build_ramadan_chart()` shows 4-commodity line chart with Eid reference line at month_relative=0 and shaded T-2 to T+1 band. `add_hline(y=100)` baseline. Islamic calendar from `islamic_cal_df` loaded via `data_static.load_csv()`. |
| 6.2.4 | Seasonal summary table (`mo.ui.table()`) | ✅ DONE | Aggregated from `_compute_seasonal_data()` → `summary_df`: commodity, avg_price, peak_month, spike_pct, spike_driver, data_months. Sorted by abs spike_pct descending. |
| 6.2.5 | Page-specific driver toggle (Ramadan / Harvest / Year-End / All) | ✅ DONE | `mo.ui.radio()` with 4 options. "All" shows all 3 charts vertically with section headers. Individual modes show single chart. Action window KPI cards computed from `action_windows_df`. |
| 6.2.6 | Wire page via Marimo reactive DAG | ✅ DONE | No callback needed — Marimo DAG handles reactivity. `seasonal_computations` cell receives `price_national_df`, `forecast_df`, `islamic_cal_df`. `page2_driver_chart` reads `driver_toggle.value`. Final `page2_assembly` cell returns `mo.vstack` of all components. |
| 6.2.7 | Data limitation callout (Rice/Sugar/Flour) | ✅ DONE | `mo.callout(kind="info")` in `page2_data_notice` cell — Rice/Sugar/Flour data ends 2020-03 (WFP gap), Cooking Oil extends to 2024-12. |
| 6.2.8 | Explainer accordion (6 sections) | ✅ DONE | `mo.accordion()` in `page2_explainer` cell with 6 entries from `EXPLAINERS_P2` dict in `explainer_copy.py`. |

### Page 3 — Geographic Disparity
> **Explainer:** "Which island group offers the best sourcing price?" — 5 island **KPI cards** (clickable), **choropleth map** (province-level), **comparison line chart** (5 series + Java hline), sortable **province drill-down table**, **data limitation callout** (Cooking Oil only).

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.3.1 | KPI cards: price index per island group (5 cards) | ⬜ | `dbc.Card` × 5 from `mart_geo_disparity`. Java = 100 baseline (hardcoded). Each card shows island group name, current price index, and YoY change (`yoy_change_index`). Clickable cards set island filter via callback to `dcc.Store`. |
| 6.3.2 | Indonesia choropleth map | ⬜ | `px.choropleth` with vendored GeoJSON (`dashboard/assets/indonesia_provinces.geojson`, ~1 MB). GeoJSON already vendored (G2). `locationmode="geojson-id"` with province names matched to `admin1` in `mart_geo_disparity`. Color scale: `price_index_vs_java`. Year slider via `dcc.Slider` with `go.Frame` animation. Only Cooking Oil has province-level data (Rice/Sugar/Flour = national aggregate only). |
| 6.3.3 | Island group comparison line chart (5 series, Java baseline) | ⬜ | `go.Figure` with 5 `go.Scatter` traces (one per island group). `add_hline(y=100, line_dash="dash", annotation_text="Java baseline")`. X-axis: year. Y-axis: `price_index_vs_java`. Color per island group. Filtered by commodity dropdown. |
| 6.3.4 | Province drill-down table (`dbc.Table`) | ⬜ | Filtered by selected island group. Columns: province, price index, YoY change, months with data. Sorted by price index ascending (cheapest first). Includes "coverage" honesty column noting data gaps (Rice/Sugar/Flour limited to national agg). |
| 6.3.5 | Data limitation callout (Cooking Oil only) | ⬜ | `dbc.Alert` with `color="warning"` explaining that geographic analysis is limited to Cooking Oil because Rice/Sugar/Flour have no market-level actual prices (only national avg market_id=974). Always visible on page. |
| 6.3.6 | Wire page via single callback | ⬜ | `Input`: 3 global filters. `Output`: KPI cards, choropleth figure, comparison chart figure, drill-down table children. Data source: `load_mart("mart_geo_disparity")`. |

### Page 4 — Commodity Signals
> **Explainer:** "Which commodities to monitor as early warning indicators?" — **lag selector** (0–3 mo) controlling **correlation heatmap** + 2 **callout cards**, pair **scatter chart** (pre/post-2022), **rolling correlation chart**, **pre/post comparison table**, **procurement implication card**.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.4.1 | Leading indicator callout cards (top 2 relationships, plain language) | ⬜ | `dbc.Card` × 2 from `mart_correlation_summary` filtered to top 2 by `ABS(pearson_r)` at lag_months > 0. Category Manager audience — no r values in user-facing copy. Plain language: "When [Commodity A] rises, [Commodity B] typically follows within N months." Data: `load_mart("mart_correlation_summary", lag_months=selected_lag)` sorted by `ABS(pearson_r)` desc. |
| 6.4.2 | Correlation matrix heatmap (4×4, lag dimension) | ⬜ | `px.imshow` pivoted from `mart_commodity_correlation` at selected lag. Row = lead commodity, Column = following commodity. `color_continuous_scale="RdBu_r"` (red = positive, blue = negative). Lag selector via `dcc.RadioItems(id="lag-selector")` with options 0/1/2/3 months. Matrix recomputes on lag change via callback. |
| 6.4.3 | Commodity pair scatter chart (pre/post 2022 dot split) | ⬜ | `go.Scatter` with two traces per selected pair. Pre-2022: one color. Post-2022: another color. `add_vline(x="2022-01-01", line_dash="dash")` as structural break marker. Pair selector via `dcc.Dropdown` (6 pairs: rice-oil, rice-sugar, rice-flour, oil-sugar, oil-flour, sugar-flour). Data: `load_mart("mart_commodity_correlation")`. |
| 6.4.4 | Rolling correlation stability chart (3-year window) | ⬜ | `go.Figure` with `go.Scatter(mode='lines')` for rolling Pearson r over time. 3-year (36-month) rolling window. `add_vrect(x0="2022-01-01", x1="2022-12-31", fillcolor="red", opacity=0.1)` for structural break region. Most analytically honest visual on the page — shows correlation stability degrading post-2022. |
| 6.4.5 | Pre/post 2022 comparison table (`dbc.Table`) | ⬜ | From `mart_correlation_summary`: commodity_pair, `pearson_r_pre_2022`, `pearson_r_post_2022`, delta column (`r_pre - r_post`). Color-coded delta: red if correlation weakened, green if strengthened. Only pairs with data on both sides of 2022-01-01 boundary. |
| 6.4.6 | Procurement implication card (plain language) | ⬜ | `dbc.Card` with `dcc.Markdown` body. Analytical centerpiece: explains what correlation changes mean for bundled procurement timing. Post-2022 caveat prominently displayed. Data: computed from top relationships in `mart_correlation_summary`. |
| 6.4.7 | Page-specific lag selector (0 / 1 / 2 / 3 months) | ⬜ | `dcc.RadioItems(id="lag-selector", value=1)`. Default lag = 1 month (most operationally useful). Wired into matrix heatmap callback and leading indicator card callback. |
| 6.4.8 | Wire page via callbacks | ⬜ | 2 callbacks: (1) lag selector → matrix + leading indicator cards, (2) pair selector → scatter chart. Data source: `load_mart("mart_correlation_summary")` for summary, `load_mart("mart_commodity_correlation")` for scatter/rolling. |

### 6.6 Dashboard Init ✅ DONE (2026-06-02)
> **Parallel** — zero data dependency. Can run any time after Phase 0. No need to wait for pipeline phases.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.6.1 | Update `pyproject.toml` — add `dash>=3.0`, `dash-bootstrap-components>=2.0`, `dash-ag-grid>=31.0`, `gunicorn>=22.0`; `uv sync` | ✅ DONE | Plotly already in deps. No new lockfile conflicts expected. `dash-ag-grid` for sortable/filterable tables. `gunicorn` for HF Spaces production server. |
| 6.6.2 | Create `dashboard/__init__.py` — empty init file | ✅ DONE | Makes `dashboard` a Python package. Required for `from dashboard.app import app` in HF Spaces Dockerfile CMD. |
| 6.6.3 | Create `dashboard/data_access.py` — DuckDB read-only connection + `@functools.lru_cache(maxsize=32)` on `load_mart(mart, **filters)` | ✅ DONE | Single importable layer; pages never query DuckDB directly. Mirrors `ingest/config.py` pattern. Key functions: `load_mart(name, **filters)`, `load_forecast_data()`, `load_forecast_metadata()`, `get_latest_prices(df)`, `compute_yoy_delta(df)`. Filter dict unpacked into SQL WHERE clauses dynamically. |
| 6.6.4 | Create `dashboard/app.py` — `Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CERULEAN])` + `dbc.NavbarSimple` with `dash.page_registry` links | ✅ DONE | ~40 lines. `server = app.server` for gunicorn. `dbc.Container(fluid=True)` wrapper. Navbar auto-populates from page_registry. Add `css/` link for custom overrides if needed. |
| 6.6.5 | Create `dashboard/components/__init__.py` — empty init | ✅ DONE | Package marker |
| 6.6.6 | Create `dashboard/components/filters.py` — `dcc.Dropdown` × 2 + `dcc.RangeSlider` + `dcc.Store(id="filters-store")` | ✅ DONE | Global filter bar, shared across all 4 pages via the Store. Commodity dropdown (All/Rice/Cooking Oil/Sugar/Flour). Island Group dropdown (All/Java/Sumatera/Kalimantan/Sulawesi/Eastern Indonesia). Year Range slider (2007–2024). Wrapped in `dbc.Row` with `bg-light` background. |
| 6.6.7 | Create `dashboard/components/kpi_cards.py` — 4-card row (Rice / Cooking Oil / Sugar / Flour) | ✅ DONE | Reusable across pages 1 and 3. Each card: commodity icon, name, current price (Rp formatted), YoY% delta (green/red). `dbc.Col(md=3)` per card. Color-coded border per commodity. |
| 6.6.8 | Create `dashboard/components/layout.py` — page header, footer, "forecast limitations" footnote, methodology page placeholder | ✅ DONE | `page_header(title, subtitle)` returns `html.Div` with `H3` + `P`. `forecast_footnote()` returns `dbc.Alert` with model limitations text from `forecast.json` `metadata.data_source_note`. `methodology_page()` placeholder for `/methodology` route. |
| 6.6.9 | Create `dashboard/pages/__init__.py` — empty init | ✅ DONE | Package marker |
| 6.6.10 | Create `dashboard/pages/price_trends.py` — Page 1 (see §6.1 task table) | ✅ DONE | 1 module: `layout()` function + `update_page1` callback. Registered via `dash.register_page(__name__, path="/", name="Price Trends")`. |
| 6.6.11 | Create `dashboard/pages/seasonal_patterns.py` — Page 2 (see §6.2 task table) | ✅ DONE | 1 module: `layout()` function + `update_page2` callback. Registered via `dash.register_page(__name__, path="/seasonal", name="Seasonal Patterns")`. |
| 6.6.12 | Create `dashboard/pages/geographic_disparity.py` — Page 3 (see §6.3 task table) | ✅ DONE | 1 module: `layout()` function + `update_page3` callback. Registered via `dash.register_page(__name__, path="/geographic", name="Geographic Disparity")`. |
| 6.6.13 | Create `dashboard/pages/commodity_signals.py` — Page 4 (see §6.4 task table) | ✅ DONE | 1 module: `layout()` function + `update_page4` callback. Registered via `dash.register_page(__name__, path="/signals", name="Commodity Signals")`. |
| 6.6.14 | Smoke test: `uv run python -c "from dashboard.app import app; print('Pages:', len(dash.page_registry))"` | ✅ DONE | Expected: `Pages: 4`. Validates all page modules import without error. |

### 6.7 Global Filters + Export + Deploy
> **Sequential** — depends on §6.6 (components must exist before pages can subscribe to them).

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.7.1 | Wire global filters (Commodity, Island Group, Year Range) to `dcc.Store(id="filters-store")` | ⬜ | Per-page callbacks read from Store; no per-page filter wiring |
| 6.7.2 | (Unchanged) `export/export_json.py` — query all 4 mart models + forecast → static JSON | ✅ DONE | Writes to `dashboard/public/data/` (dir auto-created by rebuild). Retained as row-count verification artefact per §78 preservation |
| 6.7.3 | (Unchanged) `verify_export()` — validates mart row count matches JSON record count per file | ✅ DONE | Continues to log to `logs/export.log` + update `pipeline.lineage.export_status` |
| 6.7.4 | (Unchanged) Log export results to `logs/export.log` + update `pipeline.lineage.export_status` | ✅ DONE | |

### 6.8 Docker Build + HF Spaces Deploy (expanded per HF CLI skill)

> **Prerequisite**: Install HF CLI once: `curl -LsSf https://hf.co/cli/install.sh | bash -s`

#### 6.8.1 — HF CLI Authentication

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.1a | `hf auth login` — paste token from `https://huggingface.co/settings/tokens` (write access) | ⬜ | One-time. Token stored in `~/.cache/huggingface/credentials`. Use `HF_TOKEN` env var for CI. |
| 6.8.1b | `hf auth whoami` — verify `albarpambagio` | ⬜ | Confirms authenticated identity before Space creation |

#### 6.8.2 — Create Space (CLI, not UI)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.2a | `hf repos create albarpambagio/wfp-food-price --type space --space-sdk docker --public --exist-ok` | ⬜ | Creates the Space repo on Hub. `--exist-ok` prevents error if already exists. |
| 6.8.2b | `hf spaces info albarpambagio/wfp-food-price` — verify `sdk: docker`, `visibility: public` | ⬜ | Confirms Space was created correctly before uploading code |

#### 6.8.3 — Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Layer 1: deps (cached unless pyproject.toml changes)
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Layer 2: dashboard code
COPY dashboard/app.py dashboard/
COPY dashboard/pages/ dashboard/pages/
COPY dashboard/components/ dashboard/components/
COPY dashboard/data_access.py dashboard/

# Layer 3: runtime data
COPY data/wfp.duckdb data/wfp.duckdb
COPY dashboard/public/data/forecast.json dashboard/public/data/forecast.json

EXPOSE 7860
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120"]
```

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.3a | Create `dashboard/Dockerfile` per above spec | ⬜ | Port **7860** (HF Spaces standard, not 8050 from local dev). `app:server` = Flask handle exposed via `app.server`. 2 workers (free tier CPU limit). 120s timeout for cold-start DuckDB. |
| 6.8.3b | Create `dashboard/.dockerignore` — exclude `.venv/`, `__pycache__/`, `analysis/`, `transform/`, `forecast/`, `logs/`, `docs/`, `.git/`, `data/raw/` | ⬜ | Keeps Docker image lean (~200 MB vs ~1 GB). `data/raw/` excluded (CSVs not needed at runtime). |
| 6.8.3c | Create `dashboard/README_HF.md` (HF Spaces metadata header) | ⬜ | Required for HF to recognize the Space. See YAML below. |

**`dashboard/README_HF.md` content:**
```yaml
---
title: WFP Food Price Intelligence
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---
```

#### 6.8.4 — Upload + Build

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.4a | `cd "D:\PROJECT\food price dashboard" && hf upload albarpambagio/wfp-food-price --type space dashboard/ --delete --commit-message "feat: Phase 6 — Dash dashboard (4 pages + DuckDB)"` | ⬜ | Upload from **project root** so Dockerfile `COPY` paths resolve. `--delete` removes Hub files not in local dir. First push triggers Docker build (~3–5 min). |
| 6.8.4b | `hf spaces logs albarpambagio/wfp-food-price --build --follow` | ⬜ | Monitor Docker build in real-time. Watch for: COPY failures, port mismatch, import errors. |
| 6.8.4c | If build fails: fix, re-upload with same command | ⬜ | HF rebuilds incrementally (Docker layer caching). Only changed layers rebuild. |

#### 6.8.5 — Post-Deploy Verification

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.5a | `curl -s https://albarpambagio-wfp-food-price.hf.space/ \| Select-Object -First 5` | ⬜ | Verify homepage loads (returns HTML, not 502) |
| 6.8.5b | Verify all 4 page routes respond: `/`, `/seasonal`, `/geographic`, `/signals` | ⬜ | Each page should render within 30s of first request (cold start) |
| 6.8.5c | Verify KPI cards render with real data (Rp prices, YoY%) | ⬜ | Confirms DuckDB read-only connection works inside Docker |
| 6.8.5d | Verify forecast overlay loads (dashed lines + CI area) | ⬜ | Confirms `forecast.json` COPY path is correct |
| 6.8.5e | Check Space info: `hf spaces info albarpambagio/wfp-food-price` — `runtime: running` | ⬜ | Space must show running, not building or paused |

#### 6.8.6 — Iterative Updates (post-initial-deploy)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.6a | **Hot-reload** (Python-only changes, no new deps): `hf spaces hot-reload albarpambagio/wfp-food-price --local-file dashboard/app.py` | ⬜ | Skips full Docker rebuild. Changes any Python file instantly. Good for callback logic fixes. |
| 6.8.6b | **Full re-upload** (new deps, Dockerfile changes): `hf upload albarpambagio/wfp-food-price --type space dashboard/ --delete --commit-message "fix: <description>"` | ⬜ | Triggers full Docker rebuild. Use when `pyproject.toml` or `Dockerfile` changes. |
| 6.8.6c | **Restart** (stuck build, OOM): `hf spaces restart albarpambagio-wfp-food-price` | ⬜ | Full restart. Cold start ~15-30s. |
| 6.8.6d | **Dev mode** (SSH debugging): `hf spaces dev-mode albarpambagio/wfp-food-price --stop` then `hf spaces ssh albarpambagio/wfp-food-price` | ⬜ | Opens SSH tunnel into running container. Use for debugging import errors or DuckDB path issues. |

#### 6.8.7 — Sleep/Wake + Maintenance

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.7a | HF Spaces free tier: auto-sleeps after 48h inactivity. First request wakes it (~15-30s cold start). | ⬜ | No wake-up hook needed. HF auto-wakes on HTTP request. |
| 6.8.7b | **Pause manually**: `hf spaces pause albarpambagio/wfp-food-price` | ⬜ | Saves compute quota when not demonstrating the project |
| 6.8.7c | **Resume**: `hf spaces restart albarpambagio/wfp-food-price` | ⬜ | |
| 6.8.7d | **Delete Space** (if needed): `hf repos delete albarpambagio/wfp-food-price --type space --yes` | ⬜ | Irreversible. Only if rebuilding from scratch. |

#### 6.8.8 — HF CLI Command Reference (for this project)

| Step | Command | Purpose |
|------|---------|---------|
| Auth | `hf auth login` | One-time token setup |
| Auth check | `hf auth whoami` | Verify identity |
| Create Space | `hf repos create ... --type space --space-sdk docker --public --exist-ok` | Create repo on Hub |
| Upload code | `hf upload ... --type space dashboard/ --delete --commit-message "..."` | Push code + data |
| Build logs | `hf spaces logs ... --build --follow` | Watch Docker build |
| Hot reload | `hf spaces hot-reload ... --local-file <path>` | Python-only instant update |
| Restart | `hf spaces restart` | Full restart if stuck |
| Status | `hf spaces info` | Check runtime state |
| SSH debug | `hf spaces dev-mode ... && hf spaces ssh ...` | Container shell access |
| Pause | `hf spaces pause` | Manual sleep |
| Secrets | `hf spaces secrets add ... --secrets "KEY=VALUE"` | Add env secrets (future use) |
| Env vars | `hf spaces variables add ... --env "KEY=VALUE"` | Add env variables |

#### 6.8.9 — Smoke Test (local, before deploy)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.8.9a | `uv run python -c "from dashboard.app import app; print('OK', len(dash.page_registry))"` | ⬜ | Validates app object loads. Expected: `OK 4` (4 pages registered) |
| 6.8.9b | `uv run python dashboard/app.py` — visit `http://localhost:7860` | ⬜ | Full local test. All 4 pages, filters, charts, DuckDB queries. |
| 6.8.9c | Verify cold start < 3s (data loaded once via `lru_cache`, charts built in callback) | ⬜ | Performance acceptance criterion |

#### 6.8.10 — Local Dev vs Production Differences

| Aspect | Local (`uv run python dashboard/app.py`) | HF Spaces (Docker) |
|--------|------------------------------------------|---------------------|
| Port | 7860 (configured to match) | 7860 (HF default) |
| DuckDB path | `PROJECT_ROOT / "data" / "wfp.duckdb"` (relative to `dashboard/`) | Same — `COPY`'d into container at `/app/data/wfp.duckdb` |
| Forecast JSON | `PROJECT_ROOT / "dashboard" / "public" / "data" / "forecast.json"` | Same — `COPY`'d into container |
| Workers | 1 (Flask dev server) | 2 (gunicorn) |
| Cold start | Instant (already running) | 15-30s (first request after sleep) |
| Hot reload | Auto (Flask dev mode) | `hf spaces hot-reload` or full re-upload |

### New Dash Conventions Block (will be added to AGENTS.md "Key Conventions")

- `dash.register_page(__name__, path=..., name=...)` for every page file
- One file per page in `dashboard/pages/`; layout at module level
- Callbacks live in the same file as the layout they update
- Use `dcc.Store(id="filters-store")` for cross-page filter state (alternative: `dcc.Location` query string)
- Queries go through `dashboard/data_access.py:load_mart()` — never query DuckDB directly from a page
- `dcc.Graph(figure=go.Figure(...))` for charts; reuse Plotly figure code from `analysis/eda.py`
- `dbc.NavbarSimple` for top nav, `dbc.Container(fluid=True)` for full-width
- Cold-start under 3s: data loaded once via `lru_cache`, charts built in callback
- Run locally: `uv run python dashboard/app.py` (port 7860 to match HF Spaces)
- Validate: `uv run python -c "from dashboard.app import app; print(app.layout)"` smoke test

</details>

</details>

---

## Phase 7 — Forecasting Methodology Documentation (1 day)
> **Parallel** — can start once Phase 3 model decisions are made (AutoARIMA vs AutoETS, CV results). Runs alongside Phase 4–6.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 7.1 | Problem statement: grain, horizon, what/why | ✅ | `docs/model_methodology.md` §1 |
| 7.2 | Data preparation: national avg, actual prices only, monthly grain, Islamic calendar regressors | ✅ | `docs/model_methodology.md` §2 |
| 7.3 | Model candidates: AutoARIMA, AutoETS, AutoTheta — what each does | ✅ | `docs/model_methodology.md` §3 |
| 7.4 | Model selection: CV approach, holdout, MAE/RMSE, final model per commodity | ✅ | `docs/model_methodology.md` §4 |
| 7.5 | Confidence intervals: plain language explanation of 95% CI, procurement action zone | ✅ | `docs/model_methodology.md` §5 |
| 7.6 | Known limitations: 5 items per plan | ✅ | `docs/model_methodology.md` §6 — 10 items across model + data |
| 7.7 | How to re-run: step-by-step retraining instructions | ✅ | `docs/forecast_runbook.md` |

---

## Phase 8 — Insights, Recommendations & Write-up (1 day)
> **Sequential** — depends on all prior phases. Reads insights from Phase 4+5, screenshots from Phase 6, methodology from Phase 7.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 8.1 | README: business scenario (3–4 sentences) | ✅ | |
| 8.2 | README: exec-driven questions (4 bullets) | ✅ | |
| 8.3 | README: pipeline architecture (Mermaid diagram) | ✅ | Raw CSV → DuckDB → dbt → statsforecast → export_json.py → **Marimo notebook (static JSON) → HF Spaces (WASM)** — pending rebuild |
| 8.4 | README: dbt lineage graph screenshot | ⬜ | Deferred — needs `dbt docs generate` + manual screenshot |
| 8.5 | README: key findings (4–6 quantified bullets) | ✅ | 6 findings from EDA confirmed |
| 8.6 | README: dashboard preview (4 screenshots) | ⬜ | Deferred to Phase 6 rebuild — needs dashboard WASM export + browser screenshots |
| 8.7 | README: recommendations mapped to stakeholders | ✅ | Procurement Analyst + Category Manager tables |
| 8.8 | README: data limitations + validation findings | ✅ | Known Limitations + Data Quality Issues sections |
| 8.9 | README: forecasting methodology summary + link | ✅ | Links to `docs/model_methodology.md` |
| 8.10 | README: reproduction instructions | ⬜ | **NEEDS UPDATE** — replace old instructions with `uv run python dashboard/app.py` (dev) + `marimo export html-wasm` → HF Spaces static hosting (prod) |
| 8.11 | README: lessons learned | ⬜ | **NEEDS UPDATE** — replace React/Dash references with Marimo reactive DAG patterns row |
| 8.12 | Finalize `docs/insights_log.md` with all 3 insight types: contextual, directional, actionable | ✅ | 13 findings across all 3 types — no edits needed |
| 8.13 | Live URL pinned in README and GitHub repo description | ⬜ | Deferred — HF Spaces WASM deploy pending (`https://albarpambagio-wfp-food-price.hf.space`) |

---

## Validation Checklist

- [x] Phase 0: Data validation checks completed, scoping decisions documented
- [x] `pipeline.lineage` table created with run_id tracking
- [x] `update_lineage()` uses quote-wrapped column names in dynamic SET clauses
- [x] `load_raw.py` is idempotent — DROP TABLE + CREATE TABLE on each run
- [x] `reconcile()` raises RuntimeError instead of sys.exit — proper lineage update on failure
- [x] `run_pipeline.py` orchestrates ingest → dbt run → dbt test → reconciliation → lineage
- [x] `data_validation.py` reads from pipeline DB instead of reloading CSV
- [x] `docs/issues_log.md` created with 6 documented issues
- [x] `docs/LEARNINGS.md` extended with §§36-38
- [x] All paths use absolute `__file__`-based resolution — works from any working directory
- [x] Row count reconciliation at every pipeline stage
- [x] Row-level quality flags carried through to mart models
- [x] dbt staging tests pass (not_null, accepted_values, positive_values, unique)
- [x] dbt mart tests pass (not_null, accepted_values, positive_values)
- [x] dbt docs generate produces lineage graph
- [x] Phase 2.5 corrections: Ramadan flags joined, YoY delta added, correlation summary created, DATE_TRUNC centralized, lineage table fixed
- [x] dbt audit (6 dimensions): FK relationships test, packages.yml, exposures, seed YAML, filter_out invariant, unit accepted_values, dead config cleanup, expanded source column docs (5→13 food_prices, 3→7 markets)
- [x] All generic tests verified with correct `arguments:` nested syntax (dbt 1.11.11)
- [x] EDA: ≥10 findings in insights log
- [x] EDA reads from dbt marts for reconciliation (filter_out flags, correlation summary, seasonal patterns)
- [x] Sugar Ramadan uses actual Islamic calendar dates, not hardcoded Gregorian months
- [x] Forecast JSON validated against actual prices (holdout MAE per commodity)
- [x] USD price analysis confirms IDR trends are real
- [x] All 5 mart→JSON exports verified (row count match)
- [x] Source freshness column `_loaded_at` added to raw load
- [x] `forecast/run_forecast.py` — trains AutoARIMA/AutoETS per commodity
- [x] Ramadan/Eid binary flags used as exogenous regressors
- [x] 6-month forecast with 95% CI generated
- [x] Forecast output validated (no NaN, negative, or reversed CI)
- [x] `forecast_status` and `export_status` updated in pipeline lineage
- [x] `export/export_json.py` — all 4 mart models + forecast → JSON
- [x] Export verified: JSON record count == mart row count
- [x] `run_pipeline.py` updated with forecast + export steps + parameterized schemas
- [x] `docs/model_methodology.md` written (7 sections)
- [x] `analysis/forecast_experimentation.py` created (optional notebook)
- [x] Hardcoded DuckDB path replaced with `PROJECT_DB_PATH` (computed from `Path(__file__)` inside `setup()` cell) in all 3 notebooks — avoids marimo `__` name filtering
- [x] `numpy>=1.26.0` + `scipy>=1.11.0` added to `pyproject.toml` — resolves missing notebook dependency imports
- [x] `transform/snapshots/` directory created — referenced by `dbt_project.yml` but did not exist on disk
- [x] Phase 8: README.md created (273 lines, 16 sections)
- [x] Phase 8: Business scenario, exec questions, key findings documented
- [x] Phase 8: Mermaid pipeline diagram in README
- [x] Phase 8: Stakeholder audience table in README
- [x] Phase 8: Executive summary KPI table in README
- [x] Phase 8: Data traceability table (every metric → mart model → file)
- [x] Phase 8: Known limitations + data quality issues sections
- [x] Phase 8: Recommendations mapped to Procurement Analyst + Category Manager
- [x] Phase 8: Forecasting methodology summary + link to full doc
- [x] Phase 8: Reproduction instructions (7-step setup)
- [x] Phase 8: Lessons learned (8 items from LEARNINGS.md)
- [x] Phase 8: insights_log.md verified — 13 findings, all 3 insight types
- [x] Phase 3f: 11 pipeline gaps closed (ramadan cross-year, hardcoded dates, run_id, dbt log, func split, docs, pins, lineage DDL)
- [x] Full pipeline end-to-end verified: ingest → dbt (66/66) → forecast → export — 59.4s, unified run_id
- [x] **Phase 6 Marimo-native dashboard**: Page 1 complete (KPI cards, trend chart, buy signals, YoY table). Pages 2-4 placeholders.
- [x] **Phase 6 UX audit (2026-06-08)**: 18 issues identified — all high-priority resolved: dead Island Group control removed, stub tabs hidden, commodity filter merged, buy signal methodology disclosed, year slider defaults to last 5 years, unit labels on KPI prices, colour-blind safe signal icons, reactivity cells split, emoji removed from table. Remaining: hardcoded annotation (TODO'd), sparkline axis context (min/max labels added).
- [x] **Phase 6 v2 regression fix**: Broken `mo.ui.button` (counter-based, locked slider) replaced with `mo.ui.checkbox` (boolean). Unused imports cleaned. YoY reconciling note added between KPI and table sections.
- [x] **Phase 6 v3 fixes**: KPI layout hstack→vstack (no overflow), per-commodity sparkline window (Flour data ends 2020-03, global window had 0 records), `mo.stat()` HTML captions replaced with plain text + `direction` parameter.
- [x] **Phase 6 v5 fixes**: KPI cards vstack→2×2 hstack grid (4 cards, `widths="equal"`), page order corrected (KPIs → Buy Signals → Filters → Chart → Callout → YoY → Explainer), sparkline `width=160` constraint added to `kpi_sparklines.py`, full-width panels for Buy Signal Monitor and YoY table.
- [x] **Phase 6 Page 2 (Seasonal Patterns)**: 11 new cells — `seasonal_computations` (heatmap/ramadan/harvest/year-end/action-windows/summary from `price_trends_national.json`), `page2_filters` (driver radio), `page2_action_cards` (mo.stat KPIs), `page2_data_notice` (mo.callout), `page2_heatmap` (go.Heatmap), `page2_driver_chart` (3 builders conditional on toggle), `page2_summary_table` (mo.ui.table), `page2_explainer` (mo.accordion 6 sections), `page2_assembly` (mo.vstack), updated imports + data loading + final tabs cell. All 3 verification checks pass: `marimo check` ✅, `ruff format --check` ✅, script mode ✅.
- [x] **LEARNINGS.md §106-113**: 8 new sections — button counter, hstack overflow, stat HTML captions, per-commodity sparkline window, reactivity cell split, filter override consistency, numpy bool cast for Plotly showlegend, mo.ui.table sortable param unsupported.
- [x] **Phase 6 architecture documented**: `HANDOFF-dashboard-marimo-rewrite.md` — data schemas, cross-cell scoping, dual-path resolution, Page 4 sync, failure-mode validation ✅ DONE
- [x] **Phase 6 `marimo check`**: ✅ PASS — `dashboard/app.py` valid Marimo notebook (PEP 723 header warning only)
- [x] **Phase 6 `ruff check dashboard/`**: ✅ Clean — E501 only, 0 F821/B018/E702
- [x] **Phase 6 script mode**: ✅ PASS — `uv run python dashboard/app.py` exits cleanly
- [ ] **Phase 6 WASM export**: Pending — needs `marimo export html-wasm` test after Pages 2-4 complete
- [ ] **Phase 6 WASM deploy**: `dist/` folder served via HF Spaces (static HTML, no Docker) — pending Pages 2-4 + HF Spaces WASM config
- [ ] **DEFERRED**: HF Spaces live URL + dbt lineage screenshot + dashboard screenshots — pending Pages 2-4 completion
- [x] **Vizro history preserved**: §6.SPIKE/§6.DATA/§6.WIREFRAME collapsed into §6.HISTORY details block ✅ DONE
- [x] **Dash scaffolding preserved**: §6.6-§6.8 collapsed into §6.HISTORY details block ✅ DONE
- [x] **SUPERSEDED 2026-06-02**: Next.js + Shadboard + Recharts + Cloudflare Pages — replaced by Plotly Dash + dash-bootstrap-components + Hugging Face Spaces. See Phase 6 "Stack Change Decision" subsection for rationale.
- [x] **Phase 5g 2026-06-02**: G1 — `mart_price_trends_national.sql` for Page 1 multi-commodity trend ✅ DONE (preserved in dbt)
- [~] **Phase 5g 2026-06-02**: G2 — Indonesia provinces GeoJSON vendored at `dashboard/assets/` ✅ DONE **FILE DELETED 2026-06-08** — will re-vendor when Page 3 (Geographic Disparity) is built
- [x] **Phase 5g 2026-06-02**: G3 — `pearson_r_pre_2022` + `pearson_r_post_2022` columns in `mart_correlation_summary` ✅ DONE (preserved in dbt)
- [x] **Phase 5g 2026-06-02**: G4 — Cooking Oil dual-forecast (primary + `post2022_robustness` toggle) documented in `forecast.json` metadata + §6.1.2 wireframe ✅ DONE (preserved in forecast.json)
- [x] **Phase 5g 2026-06-02**: G5 — AGENTS.md stack sweep (6 sections: L13, L70-73, L93, L338, L388, L495) ✅ DONE
- [x] **Phase 5g 2026-06-02**: G6 — LEARNINGS.md §75 SUPERSEDED banner + §81-§86 Dash learnings ✅ DONE
- [x] **Phase 5g 2026-06-02**: G7 + G8 — README.md + `wfp-food-price-intelligence-project-plan.md` stack sync ✅ DONE
- [x] **Phase 5g 2026-06-02**: G9 — Remove dead `current_step_map` dict in `run_pipeline.py:129` ✅ DONE
- [x] **Phase 5g 2026-06-02**: G10 — Move `transform_status="running"` to before `dbt seed` in `run_pipeline.py:179` ✅ DONE
- [x] **Phase 5g 2026-06-02**: G11 — Add `dbt source freshness` step to pipeline (per LEARNINGS §49) ✅ DONE
- [x] **Phase 5g 2026-06-02**: G12 — Sync `requirements.txt` with `pyproject.toml` (or delete) ✅ DONE
- [x] **Phase 5g 2026-06-02**: G13 — Normalize JSON export date format to `"%Y-%m-%d"` in `export_json.py:export_table()` ✅ DONE
- [x] **Wireframe evaluation resolution 2026-06-02**: All §10.1/10.2 items resolved; evaluation §7.7 (CSS), §7.8 (interactions) added; page wireframes updated (TanStack→AG Grid, GeoJSON paths, state machines, empty states); LEARNINGS.md §92-96 added; archive heading for §1-34 ✅ DONE

---

## Key EDA Findings (Confirmed)

1. **Cooking oil structural break**: 2022 global supply shock + export ban created permanent level shift
2. **Sugar Ramadan premium**: Most consistent seasonal effect across 17 years. Islamic calendar adjustment (vs hardcoded [3,4,5]) shifts premium estimate by ~1-2pp
3. **Eastern Indonesia premium**: Persistent geographic disparity, narrowing/widening per commodity. Cooking Oil shows widest gap (~30%)
4. **Pipeline yield**: Only 2,116 of 325,239 raw rows pass quality filters (0.65%). Non-target commodities dominate filtered rows
5. **Lagged correlation**: Oil→Flour strongest at lag 3 (r=0.8885). Rice→Sugar strongest at lag 0 (r=0.8710)
6. **Forecast accuracy**: MAE ranges from 23 (Flour) to 1,714 (Cooking Oil). Post-2022 structural break degrades oil forecast reliability

---

## Commit Strategy

Solo portfolio project — commit per phase on `main`. No branches needed unless experimenting.

| Phase | Commit Message | Scope |
|-------|---------------|-------|
| Phase 0 | `feat: project setup + data validation checkpoint` | Folder structure, dbt init, config, validation |
| Phase 1 | `feat: ingest & dbt staging models` | Pipeline layer 1 |
| Phase 0/1 fix | `fix: quote-sql-idents, idempotent-ingest, pipeline-orch, validation-fix` | Engineering fixes across Phase 0/1: quote-wrap, idempotent loads, orchestrator, DB-read validation, issues_log, LEARNINGS.md §36-38 |
| Phase 2 | `feat: dbt intermediate + mart models` | Analytical core |
| Phase 2.5 | `fix: post-implementation corrections (ramadan, correlation, lineage, docs)` | Gap fixes |
| Phase 2.5a | `fix: dbt audit — FK test, packages, exposures, seed YAML, invariants, docs` | 9 audit gaps closed, 33→55 tests |
| Phase 3a | `feat: forecast engine — run_forecast.py` | AutoARIMA/AutoETS, exogenous regressors, validation |
| Phase 3b | `feat: export engine — export_json.py` | Mart queries → JSON, verify_export(), lineage |
| Phase 3c | `fix: pipeline orchestrator + _loaded_at` | `run_pipeline.py` forecast/export steps, schema parameterization, source freshness |
| Phase 4 | `feat: EDA notebook + insights log` | Analysis |
| Phase 4a | `fix: eda gap-closing (mart reconciliation, islamic ramadan, forecast val, usd, export val)` | 10 gaps closed: G1–G8 all addressed |
| Phase 5 | `feat: deep dive analysis + merge with eda notebook` | 4 North Star deep dives (forecast overlay, ramadan calendar, geographic disparity, rolling correlations), insights log update, model_methodology cross-ref |
| Phase 5a | `fix: phase 5 gap-closing — stale deep_dive.py refs, eda robustness, summary alignment` | 3 docs fixed (AGENTS.md, project-plan.md, model_methodology.md), 6 code fixes in `eda.py` (mo.stop guards, Ramadan conn, Eastern Indonesia filter, summary table, unused var, lint), LEARNINGS.md §67 |
| Phase 5f | `fix: post-phase-5 fixes — DuckDB path, deps, snapshot dir` | Hardcoded DuckDB paths -> PROJECT_DB_PATH (3 notebooks, 11 occurrences), numpy/scipy in pyproject, create snapshots/ dir, update stale checklist |
| Phase 5g | `fix: pre-dashboard gap closing — national mart, GeoJSON, pre/post correlation, dual forecast, stack docs, pipeline cleanup` | 13 gaps across 3 tiers; deferred execution per user 2026-06-02 |
| Phase 3d | `docs: forecasting methodology` | `model_methodology.md` |
| Phase 3e | `fix: phase 3 bugfix — 7 gaps from pipeline audit` | Error handler, lineage DDL, metadata, skips, connection, t_minus_3, status value |
| Phase 6 blueprint | `docs: marimo handoff — data schemas, cross-cell scoping, dual-path, Page 4 sync, failure modes` | Architecture reference: 8 DataFrame schemas, 40+ cross-cell variable exports, three-source mo.state() mechanism, validation diagnosis table |
| Phase 6 rebuild | `feat: Marimo dashboard rebuild — Page 1 complete, Pages 2-4 placeholders` | `app.py` (mo.stat KPIs, trend chart, buy signals, YoY table), `data_static.py` rewritten, 11 chart files deleted, `kpi_sparklines.py` simplified, `build.py` simplified, AGENTS.md + LEARNINGS updated, all JSON re-exported |
| Phase 7 | `docs: forecasting methodology` | `model_methodology.md` + `forecast_runbook.md` |
| Phase 8 | `docs: README, insights, recommendations` | Final packaging — README, insights_log verified |
| Phase 3f | `fix: 11 pipeline gaps — ramadan cross-year, hardcoded date, unified run_id, dbt log, func split, docs, pep723 pins, lineage dedup` | Cross-phase gap closing post-Phase-5f |
| Phase 6 plan | `docs: phase 6 stack change — Next.js+Shadboard+CF Pages → Plotly Dash+dbc+HF Spaces` | This document update; LEARNINGS.md §75 marked superseded; rationale in Phase 6 "Stack Change Decision" subsection |
| Wireframe resolution | `docs: resolve wireframe evaluation — AG Grid, GeoJSON paths, state machines, §92-96` | 6 files: 4 page wireframes, evaluation doc, LEARNINGS.md. 11 resolved items, 3 open items identified. |
| Page 1 Vizro build | `feat: Page 1 Vizro — trend forecast, KPI sparklines, YoY bar, signal badges` | 4 chart files + vm.Page + model info card + data_manager registration |
| Page 1 bugfixes | `fix: Page 1 Vizro bugs — first-render, YoY, overlap, clipping, hover, theme` | 6 fixes across charts + LEARNINGS §97-§98 |
| Page 2 handoff | `docs: Page 2 seasonal patterns implementation handoff` | Data source correction, month_relative reframing, chart functions, filter patterns |
| Phase 6 v5 | `fix: Page 1 v5 — KPI 2×2 grid, page order, sparkline width` | KPI cards hstack 2×2, layout reorder (chart before signals, callout below chart), `width=160` on sparkline, `mo.card()` attempted but reverted (unavailable in 0.23.9), full-width panels |
| Phase 6 Page 2 | `feat: Page 2 seasonal patterns — heatmap, driver charts, action windows, summary table` | 11 new cells in app.py, EXPLAINERS_P2 in explainer_copy.py, islamic_calendar.csv added to public/data/, Page 2 verification passes |

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
| 2026-05-25 | **dbt evaluation per dbt-agent-skills**: audit found 9 gaps — missing FK relationships test, no packages.yml, no exposures, no seed YAML, dead config, unused column, insufficient column docs, missing unit test, deprecated test syntax. | All 9 closed. Tests expanded from 33→55. `dbt build` passes 66/66 with 0 errors, 0 warnings. Documented in AGENTS.md § "dbt Implementation Evaluation" and LEARNINGS.md §56. |
| 2026-05-26 | **Pre-Phase 3 gap analysis**: forecast/export/pipeline/orchestrator all missing. | Built during Phase 3. ✅ Complete |
| 2026-05-26 | **Phase 3 bugfix audit**: found 7 gaps — error handler column, lineage DDL fragmentation, hardcoded dates, skipped commodity tracking, connection leak, t_minus_3 parity, status value inconsistency. | All 7 fixed in Phase 3e. See tasks 3.12–3.18. |
| 2026-05-26 | **`mart_commodity_correlation` granularity mismatch**: Cooking Oil averaged across hundreds of markets; Rice/Sugar/Flour from single national avg market (974). | Cross-correlation coefficients may be misleading. Flag in `model_methodology.md` and dashboard footnote. |
| 2026-05-26 | **Phase 4 gap analysis**: 10 gaps identified — EDA bypassed dbt marts, Ramadan used hardcoded months, no forecast validation, no export verification. | All 10 closed. EDA now reconciled against all 5 marts + JSON exports. See verification cells R1/R2. |
| 2026-05-26 | **Phase 4/5 merge**: `deep_dive.py` merged into `analysis/eda.py` (40+ cells, 1670+ lines). Plotly 6.7.0 + pandas 3.0.3 incompatibility with `add_vline` annotations on string axes; annotations removed where x-axis uses date strings. | Resolved. Notebook passes headless execution. |
| 2026-05-26 | **Phase 5 gap analysis**: 3 docs still referenced non-existent `deep_dive.py`; summary table used `DD §` section refs that don't exist; no `mo.stop()` guards on forecast/correlation JSON reads; Ramadan cell opened redundant DuckDB connection; Eastern Indonesia pre-2015 not filtered in province drilldown; unused `is_script_mode` variable. | All closed: 3 docs updated, 6 code fixes in `eda.py`. LEARNINGS.md §67 captures the merge-delete sweep pattern. |
| 2026-05-26 | **Phase 5f: Post-Phase-5 path/deps/dirs audit**: 3 notebooks used module-level __db_path (filtered by marimo from cell namespaces -> NameError). pyproject.toml missing numpy + scipy. transform/snapshots/ non-existent despite dbt_project.yml reference. | All 3 fixed: __db_path -> PROJECT_DB_PATH via setup cell DAG across 3 notebooks (11 occurrences). numpy>=1.26.0 + scipy>=1.11.0 in pyproject. transform/snapshots/ created. LEARNINGS.md sec68. |
| Phase 5f | fix: post-phase-5 fixes -- DuckDB path, deps, snapshot dir | Hardcoded DuckDB paths -> PROJECT_DB_PATH (3 notebooks), numpy/scipy in pyproject, create snapshots/ dir, update stale checklist |
| 2026-05-26 | **Phase 3f gap analysis**: 11 gaps found across all non-dashboard phases — Ramadan cross-year test gap (P1), forecast data source divergence (P1), hardcoded forecast dates (P2), fragmented run_ids (P2), empty transform.log (P2), monolithic fit_and_forecast (P3), undocumented geo filter (P3), undocumented correlation asymmetry (P3), PEP 723 == pins (P3), lineage DDL dedup (P4). | All 11 closed. Full pipeline verified (66/66 dbt tests, 59.4s pipeline time, unified run_id). |
| 2026-05-26 | **Commit c0a74a9** pushed: `fix: 11 pipeline gaps` to `origin/master`. | 12 files, 124 insertions, 85 deletions. |
| 2026-06-02 | **Phase 6 stack change — Next.js + Shadboard + Cloudflare Pages → Plotly Dash + dash-bootstrap-components + Hugging Face Spaces**. LEARNINGS.md §75's "Cloudflare Pages hard-blocks Python server frameworks" conclusion is **overridden**: HF Spaces replaces CF Pages as the deployment target, and §80's "Plotly EDA → Plotly dashboard" parity is now realized. The 5-JSON export pipeline (Phase 3.6–3.8) is preserved as a row-count verification artefact, not as the dashboard's data source — the Dash app queries DuckDB directly via `dashboard/data_access.py` with `@functools.lru_cache`. | Full plan written into Phase 6 section of this document (lines 282–end of Phase 6). Execution deferred at user request. Stack change rationale and rejected alternatives table inline in Phase 6 "Stack Change Decision" subsection. |
| 2026-06-02 | **Phase 5g pre-dashboard gap analysis — 13 gaps found across 3 tiers**. Cross-referenced `implementation-plan.md` (Phases 0–5, 7, 8), `LEARNINGS.md` (80 sections), `AGENTS.md`, and current filesystem state. Tier 1 (data, 4 gaps): `mart_price_trends` lacks national-level data for 3/4 commodities (Page 1 KPI cards); Indonesia provinces GeoJSON not vendored (Page 3 choropleth); `mart_correlation_summary` lacks pre/post-2022 split (Page 4 scatter); Cooking Oil dual-forecast UX not specified (Page 1 chart). Tier 2 (docs, 4 gaps): AGENTS.md, README.md, `wfp-food-price-intelligence-project-plan.md` still reference Next.js+Shadboard+CF Pages; LEARNINGS.md §75 not marked SUPERSEDED. Tier 3 (pipeline, 5 gaps): dead `current_step_map` dict; `transform_status="running"` set after `dbt seed` (not before); no `dbt source freshness` invocation; `requirements.txt` out of sync; inconsistent date format in JSON exports. **User decisions**: G1 + G3 use option (a) — new mart / new columns. G4 shows both forecasts (primary default + secondary toggle). G6 defers §81-§85 stubs (Dash-specific learnings earned during Phase 6). Tier 3 bundled into Phase 5g plan, execution deferred. | Full plan written as "Phase 5g — Pre-Dashboard Gap Closing" subsection of this document. Status note at top of section; all 13 items in 3 tier tables + key decisions table + execution order table. Validation Checklist +13 deferred checkboxes. Commit Strategy +1 row. Execution deferred — pipeline orchestrator, exported JSONs, and dbt marts remain in current state until user triggers. |
| 2026-06-02 | **Phase 6 plan expanded — HF CLI deployment workflow (§6.8)**. Consulted `huggingface/skills` HF CLI skill (`hf` command, replaces deprecated `huggingface-cli`). Documented: authentication (`hf auth login`), Space creation (`hf repos create --type space --space-sdk docker`), code upload (`hf upload ... --type space --delete`), build monitoring (`hf spaces logs --build --follow`), hot-reload (`hf spaces hot-reload`), SSH debugging (`hf spaces dev-mode` + `hf spaces ssh`), sleep/wake management. Expanded §6.6 (Dashboard Init) from 8 to 14 tasks with per-file implementation detail. Expanded §6.1–§6.4 (all 4 pages) with data source references and callback signatures. Added §6.8.10 (Local Dev vs Production differences table). Updated validation checklist. | Full plan written. Execution pending user go-ahead. |
| 2026-06-03/04 | **Page 1 Vizro build + 4 bugfix sessions** (historical — superseded by Marimo). Built `dashboard/app.py` (Vizro entry) + 4 chart files + `vm.Page` registered. 4 handoff-documented bugfix sessions. LEARNINGS §97-§100 added. | All Vizro work superseded by Marimo-native rewrite (2026-06-05→2026-06-08). Preserved in git history. |
| 2026-06-05→08 | **Marimo-native dashboard rewrite** — replaced both Vizro and Dash approaches with single `dashboard/app.py` Marimo notebook (static JSON, no DuckDB runtime). 4 pages, `mo.stat()`, `mo.callout()`, `mo.ui.table()`, `mo.ui.tabs()`. | ✅ Blueprint complete. Code deleted 2026-06-08 for clean rebuild. Architecture preserved in `docs/handoffs/HANDOFF-dashboard-marimo-rewrite.md`. Rebuild pending. |
| 2026-06-08 | **Dashboard code deleted for clean rebuild** — `dashboard/` directory removed entirely. All pipeline layers (dbt marts, forecast, export) remain intact. Handoff document preserved as rebuild blueprint. | Accepted — clean slate for Marimo rebuild from handoff. Will regenerate JSON exports + GeoJSON as part of rebuild. |
| 2026-06-08 | **Page 1 rebuild complete** — `dashboard/app.py` rebuilt as Marimo notebook with `mo.stat()` KPI cards (4 commodities), trend+forecast chart with CI overlay, buy signal monitor (3-tier: BUY/HOLD/WATCH), YoY annual price table, `mo.ui.tabs()` navigation. `data_static.py` rewritten with dual-path helpers. 11 Vizro-era chart files + `data_access.py` deleted. `kpi_sparklines.py` simplified to single `sparkline_chart()`. `build.py` simplified. AGENTS.md updated (Marimo conventions, lint baseline). LEARNINGS §102-105 added. `HANDOFF-page1-rebuild-plan.md` created. All JSON data files re-exported. `mart_price_trends_national.sql` WHERE clause updated. `profiles.yml` DuckDB path normalized. | Pages 2-4 are "Coming soon" placeholders. GeoJSON will be re-vendord for Page 3. WASM export test pending. |
| 2026-06-08 | **UX audit of Page 1** — 18 issues identified across 8 categories. All high-priority resolved: dead controls removed, stub tabs hidden, filters merged, buy signal methodology disclosed, year slider default, unit labels, colour-blind icons, reactivity split, emoji sort fix. 3 remaining (low-priority): hardcoded annotation (TODO'd), sparkline axis context (min/max labels added), YoY reconciling note between KPI/table sections. | 3 v2 regression fixes applied: broken button→checkbox, unused imports cleaned, single-tab wrapper preserved. v3: hstack overflow→vstack, per-commodity sparkline window, HTML captions→plain text. LEARNINGS.md §106-111 added. |
| 2026-06-09 | **Phase 6 v5 — Layout order + KPI grid + sparkline width fix**. Audit identified 6 issues: KPI cards still vertical (vstack), page order inverted (chart after buy signals), explainer invisible at bottom, no panel separation, forecast callout separated from chart, tabs wrapper removed. v5 fixes: (1) KPI cards → 2×2 hstack grid with `widths="equal"`, (2) page reorder: KPIs → Buy Signals → Filters → Chart → Callout → YoY → Explainer, (3) sparkline `width=160` in `kpi_sparklines.py` to prevent Plotly widget overflow, (4) `mo.card()` attempted for Buy Signal and YoY panels but reverted (Marimo 0.23.9 lacks `mo.card()`). Full-width layout with `##` headings provides sufficient visual separation. | LEARNINGS.md §113 added (KPI 2×2 grid + sparkline width constraint). `mo.card()` API gap documented as known Marimo limitation. |

