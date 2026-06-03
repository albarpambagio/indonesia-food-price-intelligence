# Implementation Plan — Indonesia Food Price Intelligence

## Project Meta

| Attribute | Value |
|-----------|-------|
| **Start Date** | 2026-05-22 |
| **Data First Accessed** | 2026-05-22 |
| **Data Source** | WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0) |
| **Target Completion** | ~16–20 working days |
| **Status** | Phase 0–5 ✅, Phase 5f ✅, Phase 3f ✅ (11 pipeline gaps closed), Phase 5g ✅ (13 pre-dashboard gaps closed). **Phase 6 scaffolding 2026-06-02**: 12 files created (app, data_access, 3 components, 4 pages). Smoke test passed (`Pages: 4`). §6.8 Docker deploy execution pending. |
| **Stack** | Python → DuckDB → dbt → statsforecast → Marimo → DuckDB-direct queries (Dash) + static JSON for forecast → **Plotly Dash (dash-bootstrap-components + Dash Pages plugin)** → **Hugging Face Spaces** |

### Parallelization Opportunities
| Phase | Can Start After | Runs Parallel With | Saves |
|-------|----------------|-------------------|-------|
| Phase 4 (EDA) | Phase 1 done (staging data available) | Phase 2 + Phase 3 | ~3–5 days |
| Phase 7 (Methodology Doc) | Phase 3 started (model decisions known) | Phase 4–6 | ~2–3 days |
| §6.6 Dashboard Init | **Phase 0** (scaffolding, zero data dependency) | Phase 1–5 | ~1 day on back-end |

**Sequential chain** (must wait): Phase 0 → 1 → 2 → 2.5 → 3 → 6 (pages). Phase 4 and 7 slot alongside, not behind.
> **Current**: Phase 0+1 ✅ → Phase 2 ✅ → Phase 2.5 ✅ → Phase 3 ✅ → Phase 3e ✅ (7 bugfixes) → Phase 4 ✅ → Phase 5 ✅ → Phase 5f ✅ (path, deps, dirs) → **Phase 3f ✅ (11 pipeline gaps)** → **Phase 5g ✅ (13 pre-dashboard gaps)** → **Phase 6 plan expanded 2026-06-02** (HF CLI deployment workflow documented in §6.8); execution pending.

---

## Phase 0 — Project Setup & Data Validation Checkpoint

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Create folder structure | ✅ | `data/raw/`, `ingest/`, `transform/`, `forecast/`, `export/`, `analysis/`, `logs/`, `dashboard/public/data/` |
| 0.2 | Create `pyproject.toml` + `uv sync` | ✅ | uv-native: duckdb, dbt-duckdb, statsforecast, marimo, pandas, plotly |
| 0.3 | Init dbt project in `/transform` | ✅ | `dbt init`, configure profiles.yml for DuckDB |
| 0.4 | Init Dash app skeleton in `/dashboard` (`app.py`, `pages/`, `components/`, `data_access.py`, `_data/snapshot.py`, `Dockerfile`, `README_HF.md`, `.dockerignore`) | ⬜ | **DEFERRED** to Phase 6 — plan documented 2026-06-02 (see Phase 6 Stack Change section) |
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

## Phase 6 — Dashboard (Vizro 0.1.x + DuckDB read-only + Hugging Face Spaces) (6–7 days) [PLANNING 2026-06-02]
> **🚧 Migration in progress.** Dash-based dashboard from earlier 2026-06-02 decision is being replaced with Vizro. See §6.STACK for the new decision rationale and §6.HISTORY for the full superseded Dash plan.
> **Sequential with decision gate** — Phase A (spike) is the gate. If spike ≤ 0.5 day, proceed; otherwise revert to Dash per §6.HISTORY.

### §6.STACK — Vizro Stack Decision (2026-06-02)

The Dash-based Phase 6 plan (chosen earlier the same day) is being replaced with **Vizro 0.1.50 + vizro-ai 0.3.8 + DuckDB read-only data manager + Hugging Face Spaces Docker**. The §6.HISTORY block at the end of this section preserves the full Dash plan as superseded reference material.

**Trigger for re-decision:** Cross-filtering requirement. The 4-page dashboard implicitly needs chart-click-to-filter-other-charts behavior (e.g. click an island group on the choropleth → all charts on the page filter to that island). Dash has no native cross-filter primitive; this requires a custom callback per cross-filter pair. Vizro's `set_control` action makes cross-filter declarative.

**Re-evaluated decision matrix (criterion 7, cross-filtering, weighted 8 — was zero in §76's first matrix):**

| Criterion (weight) | Dash 3.x | Vizro 0.1.50 | Delta |
|---|---:|---:|---:|
| Cross-filtering (8) | Custom callbacks per pair (~80 LOC × 6 pairs) | Declarative `set_control` action | **Vizro +8** |
| Maturity (8) | v3.x, 9 yrs, Plotly-backed | 0.1.50, 3.3 yrs, still 0.x | Dash +5 |
| Pipeline reuse (12) | `data_access.load_mart()` lru_cache works as-is | Same module adapts to `data_manager.register_data()` | Dash +1 |
| LOC for 4 pages (10) | ~10K bytes/page (4 explicit callbacks) | ~3-4K bytes/page (Pydantic declarative) | Vizro +6 |
| Filter behavior correctness (10) | Manual `dcc.Store` + `dcc.Location`; documented in §83 | Built-in `vm.Filter`+`vm.Parameter`; cross-page needs workaround | Dash +3 |
| Time-series viz (8) | `dcc.Graph(figure=go.Figure())` verbatim from EDA | `custom_charts` wrapper for `add_vline`/`vrect`/CI area | Dash +1 |
| Hiring signal (8) | Plotly Dash widely recognized | Vizro niche on resumes | Dash +4 |
| Migration sunk cost (6, NEW) | Page 1 (11.6K bytes) done; 2.5 days of work | Page 1 must be rebuilt | Dash +5 |
| Bug-recovery cost (4, NEW) | §81-86 documented; not battle-tested | 35+ Next.js sections (§1-34) don't apply; new bugs need new fixes | Dash +3 |

**Net: Dash +23 / Vizro +14. But cross-filtering (+8) is decisive — it enables the "click chart → filter all" UX that the 4 pages imply. The trade is acceptable.**

**Why Vizro specifically (vs. staying on Dash or switching to Streamlit / Panel):**

| Consideration | Outcome |
|---|---|
| Dash is already at "3-day finish" | Reverting to Dash after migrating 1 day of work to Vizro is cheap. The cross-filter +0 is worth 2-3 extra days. |
| Streamlit | `st.session_state` quirks per §76 decision; rerun-everything model breaks `@lru_cache` pattern. Not viable. |
| Panel | Bokeh/HoloViews chart engine; not Plotly-native; would require chart translation. Rejected. |
| Vizro 0.x maturity (§77 concern) | Accepted as cost. Mitigation: 0.5-day Phase A spike tests the framework on real charts before committing. If spike fails, fall back to §6.HISTORY. |

**What changes in the project (other than the dashboard code):**

1. `pyproject.toml` — add `vizro>=0.1.50` to `dependencies`; keep Dash deps until Phase C complete
2. `dashboard/app.py` — rewrite as `Vizro().build(dashboard).run()` entry; preserve `dashboard/data_access.py` with `data_manager.register_data()` wrapping
3. `dashboard/pages/*.py` — rewrite as `vm.Page(...)` configs; `go.Figure` builders move into `custom_charts` functions
4. `dashboard/components/*.py` — replaced by Vizro's `vm.Container` / `vm.Card` / `vm.Tabs`; only `filters.py` partials carry over as `vm.Filter` / `vm.Parameter` definitions
5. `AGENTS.md` — Stack row updated, Phase 6 line updated, "Dash Conventions" block replaced with "Vizro Conventions"
6. `docs/LEARNINGS.md` — mark §75, §81-86 superseded; add §87-91 (Vizro patterns)
7. `docs/implementation-plan.md` — this section
8. `docs/wfp-food-price-intelligence-project-plan.md` — mirror edits
9. `requirements.txt` — auto-synced with pyproject

**What does NOT change:** dbt models, mart SQL, forecast logic, lineage table, `run_pipeline.py` orchestration logic, all Marimo notebooks, `docs/data_validation.md`, `docs/forecast_runbook.md`, `docs/insights_log.md`, `docs/issues_log.md`, `docs/model_methodology.md`, the 5 JSON files in `dashboard/public/data/*.json` (kept as verifier per §78), `dashboard/data_access.py` core (DuckDB connection, `load_mart` function — wrapped, not rewritten).

### §6.SPIKE — Phase A: 0.5-Day Feasibility Spike (decision gate)

> **Sequential gate** — must complete and pass before any Phase C work begins. If spike takes > 0.5 day or reveals a Pydantic workaround > 50 LOC for one chart, fall back to §6.HISTORY (Dash).

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.A.1 | `uv add vizro`; verify version prints as `0.1.53` | ✅ | vizro 0.1.53 installed, within >=0.1.50 range. |
| 6.A.2 | Create `dashboard/spike/` scratch dir; build minimal 1-page Vizro app: title, one chart | ✅ | `dashboard/spike/app.py` (24 LOC). Pydantic 2 + `Vizro().build(dashboard).run()` validated. |
| 6.A.3 | Wrap `px.imshow` lag heatmap from `analysis/eda.py` A5b as `custom_charts` function | ✅ | `dashboard/spike/custom_charts.py` (18 LOC). Under 50 LOC threshold. |
| 6.A.4 | Wire to DuckDB via `data_manager["key"] = lambda: load_mart(name)` | ✅ | `data_manager["mart_correlation_summary"]` wired. DataFrame → Vizro flow validated. |
| 6.A.5 | `Vizro().build(dashboard).run(port=7860)`; load `http://localhost:7860`; verify chart renders | ✅ | Build OK, server serves 200 OK (16KB page), real DuckDB data loaded. |
| 6.A.6 | Decision: continue to Phase C OR revert to §6.HISTORY (Dash) | ✅ | **GO.** Logged in `logs/migration.log`. Key learning: `@capture("graph")` must be called, not passed as ref. |

### §6.DATA — Phase B: Data Layer Port (0.5 day)

> **Sequential** — depends on §6.SPIKE passing.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.B.1 | Wrap `load_mart()` calls in `data_manager["mart_X"] = lambda: load_mart(name)` for all 6 marts | ✅ | `dashboard/data_manager.py` (25 LOC). `data_access.py:load_mart()` unchanged. |
| 6.B.2 | Wrap `load_forecast_data()` as `data_manager["forecast"] = load_forecast_data` | ✅ | Same module. 7 keys total (6 marts + forecast). |
| 6.B.3 | Verify `export_json.py` + `verify_export()` unchanged and still log to `pipeline.lineage.export_status` | ✅ | Export pipeline PASS — all 6 marts verified, 0 row count mismatches. |
| 6.B.4 | Smoke test: verify 7 keys in data_manager | ✅ | 7 keys: 6 marts + forecast. |

### §6.PAGES — Phase C: Port 3 Pages + Rebuild Page 1 (3-4 days)

> **Sequential** — depends on §6.DATA. Page 1 must be rewritten (was Dash); pages 2-4 are net-new in either stack.

#### §6.C.1 — Page 1 (Price Trends & Forecast) — REBUILD

> **REBUILDS** Dash `dashboard/pages/price_trends.py` (11,620 bytes, 2026-06-02) in Vizro.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.C.1.1 | Wrap main trend chart as `custom_charts` function: `go.Figure()` + `add_vline` + `add_vrect` for forecast region + `go.Scatter(fill="toself")` for 95% CI area | ⬜ | Reuse verbatim from `analysis/eda.py` Q1. Wrap in `@capture("graph")` for Vizro. |
| 6.C.1.2 | Wrap YoY bar chart as `custom_charts` function | ⬜ | Reuse `compute_yoy_delta()` from `data_access.py`. |
| 6.C.1.3 | Build `vm.Page(title="Price Trends", components=[vm.Graph(figure=trend), vm.Graph(figure=yoy), vm.Card(...)])` | ⬜ | KPI cards → `vm.Card` with text. Signal logic → conditional `vm.Text` per commodity. |
| 6.C.1.4 | Add 3 page-level `vm.Filter`s: commodity, island, year_range | ⬜ | Per Vizro pattern, filters scope to data_frames of all components on page. |
| 6.C.1.5 | Wire model info card + forecast footnote via `vm.Container` | ⬜ | Forecast limitations footnote always visible — use `vm.Container` outside the page filter group. |
| 6.C.1.6 | Verify chart parity with original Dash Page 1: line shapes, colors, CI area, annotations | ⬜ | Visual regression check via side-by-side screenshot. |

#### §6.C.2 — Page 2 (Seasonal Patterns) — NEW

> **NEW** in either stack.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.C.2.1 | Wrap seasonal heatmap (`px.imshow` 12×4 matrix) as `custom_charts` | ⬜ | Reuse `mart_seasonal_patterns` pivot from EDA A3. |
| 6.C.2.2 | Wrap monthly line chart with driver-toggle bands (Ramadan/Harvest/Year-End/All) as `custom_charts` | ⬜ | `add_vrect` for highlighted months based on driver. |
| 6.C.2.3 | Wrap Ramadan overlay chart (T-3 to T+1, hline y=100) as `custom_charts` | ⬜ | Filter `mart_seasonal_patterns` by `flag_ramadan_*` columns. |
| 6.C.2.4 | Build summary table via `vm.Table` with `dash_ag_grid` backend | ⬜ | Aggregated: commodity, avg price, peak month, Ramadan premium. |
| 6.C.2.5 | Add page-level driver toggle: `vm.Parameter(targets=[...], selector=vm.RadioItems(options=["All", "Ramadan", "Harvest", "Year-End"]))` | ⬜ | Parameter (not Filter) because it controls chart configuration, not data. |
| 6.C.2.6 | Build `vm.Page(...)`; wire all components | ⬜ | |

#### §6.C.3 — Page 3 (Geographic Disparity) — NEW

> **NEW** in either stack.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.C.3.1 | Build 5 KPI cards via `vm.Container` with 5 `vm.Card`s; each card click → `set_control` action setting island filter | ⬜ | This is the cross-filter showcase. Cards become interactive via Vizro's `actions` API. |
| 6.C.3.2 | Wrap choropleth map as `custom_charts`: `px.choropleth(geojson=indonesia_provinces, ...)` with year slider via `vm.Parameter` | ⬜ | Vendored GeoJSON at `dashboard/assets/indonesia_provinces.geojson` (1 MB). Pass via `custom_charts` function. |
| 6.C.3.3 | Wrap island group comparison line chart as `custom_charts`: 5 `go.Scatter` traces + `add_hline(y=100)` | ⬜ | Java baseline annotation. |
| 6.C.3.4 | Build province drill-down table via `vm.Table` sorted by price index asc | ⬜ | Honesty column noting data gaps. |
| 6.C.3.5 | Add `vm.Container` with `vm.Text` data limitation callout (Cooking Oil only) | ⬜ | Always-visible alert. |
| 6.C.3.6 | Build `vm.Page(...)`; wire cross-filter via `set_control` on island KPI cards | ⬜ | **Cross-filter primitive — primary justification for migration.** |

#### §6.C.4 — Page 4 (Commodity Signals) — NEW

> **NEW** in either stack.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.C.4.1 | Build leading indicator callout cards (top 2 correlations, plain language) via `vm.Container` + `vm.Card` | ⬜ | Filter `mart_correlation_summary` at selected lag. |
| 6.C.4.2 | Wrap correlation matrix heatmap as `custom_charts`: `px.imshow` pivoted at selected lag | ⬜ | Lag selector via `vm.Parameter` with `vm.RadioItems` (0/1/2/3). |
| 6.C.4.3 | Wrap pair scatter chart as `custom_charts`: two `go.Scatter` traces (pre/post 2022) + `add_vline` | ⬜ | Pair selector via `vm.Dropdown` (6 pairs). |
| 6.C.4.4 | Wrap rolling correlation chart as `custom_charts`: 36-month rolling + `add_vrect` for 2022 break | ⬜ | Most analytically honest visual; preserve all annotations. |
| 6.C.4.5 | Build pre/post 2022 comparison table via `vm.Table` with color-coded delta column | ⬜ | |
| 6.C.4.6 | Build procurement implication card via `vm.Container` + `vm.Text` | ⬜ | Plain language; post-2022 caveat prominent. |
| 6.C.4.7 | Add lag selector `vm.Parameter`; wire to matrix + leading indicator callbacks | ⬜ | Default lag = 1 month. |

### §6.FILTERS — Phase D: Cross-Page Global Filter Workaround (1 day)

> **Sequential** — depends on §6.PAGES. Critical UX decision: how do Commodity / Island / Year filter across all 4 pages?

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.D.1 | **DECISION GATE**: Choose between (a) `show_in_url=True` on each `vm.Filter` → URL state, or (b) custom `vm.Action` pushing filter to global state | ⬜ | (a) is battle-tested, URLs ugly. (b) is cleaner but custom-action territory. **Default to (a) for first cut; revisit if user rejects URL state.** |
| 6.D.2 | Document chosen pattern in `docs/LEARNINGS.md` §89 | ⬜ | Cross-page filter workaround — one of two patterns. |
| 6.D.3 | Apply pattern uniformly to Commodity / Island / Year filters on all 4 pages | ⬜ | Single pattern, applied 3 filters × 4 pages = 12 placements. |
| 6.D.4 | Verify filter survives page navigation; test both directions (Page 1 → Page 2, Page 4 → Page 1) | ⬜ | Manual smoke test in browser. |

### §6.DEPLOY — Phase E: Docker + HF Spaces (0.5 day)

> **Sequential** — depends on §6.PAGES + §6.FILTERS.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.E.1 | Update `dashboard/Dockerfile` to use Vizro's `app:app` gunicorn target (vs Dash's `app:server`); port 7860, 2 workers, 120s timeout | ⬜ | Vizro exposes `app` not `server`. `Vizro().build(dashboard).run()` returns a Flask app handle. |
| 6.E.2 | Update `dashboard/README_HF.md` with new metadata if needed | ⬜ | Most fields unchanged: title, emoji, colorFrom, colorTo, sdk=docker, app_port=7860. |
| 6.E.3 | Update `dashboard/.dockerignore` to include `dashboard/spike/` (spike dir excluded from image) | ⬜ | Other exclusions unchanged from §6.HISTORY §6.8.3b. |
| 6.E.4 | `hf upload albarpambagio/wfp-food-price --type space dashboard/ --delete --commit-message "feat: Phase 6 v2 — Vizro dashboard (4 pages + DuckDB + cross-filter)"` | ⬜ | First Vizro push. ~3-5 min Docker build. |
| 6.E.5 | Verify all 4 page routes load at `https://albarpambagio-wfp-food-price.hf.space/` | ⬜ | Manual smoke test: `/`, `/seasonal`, `/geographic`, `/signals`. |
| 6.E.6 | Verify cross-filter works on Page 3 (click island KPI → choropleth updates) | ⬜ | The migration's headline feature must work in production. |

### §6.DOCS — Phase F: LEARNINGS.md + AGENTS.md Update (0.5 day)

> **Sequential** — can run in parallel with §6.DEPLOY.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.F.1 | Mark `docs/LEARNINGS.md` §75 superseded (HF Spaces adopted; Cloudflare argument voided) | ⬜ | Append `> SUPERSEDED 2026-06-02 — see §6.STACK` at top of §75. |
| 6.F.2 | Mark `docs/LEARNINGS.md` §81-86 superseded (Dash patterns) | ⬜ | Same supersession banner. |
| 6.F.3 | Add `docs/LEARNINGS.md` §87 — Vizro Pydantic Filter scoping (per-page, not cross-page) | ⬜ | |
| 6.F.4 | Add `docs/LEARNINGS.md` §88 — Vizro `custom_charts` wrapper for advanced Plotly | ⬜ | `add_vline`/`vrect`/CI area/choropleth with vendored GeoJSON patterns. |
| 6.F.5 | Add `docs/LEARNINGS.md` §89 — Cross-page filter workaround (URL state vs custom action) | ⬜ | Documents the §6.D.1 decision. |
| 6.F.6 | Add `docs/LEARNINGS.md` §90 — Vizro `data_manager.register_data()` pattern for DuckDB DataFrames | ⬜ | |
| 6.F.7 | Add `docs/LEARNINGS.md` §91 — Vizro HF Spaces Dockerfile parity (gunicorn `app:app`, port 7860) | ⬜ | |
| 6.F.8 | Update `AGENTS.md` Stack row: Plotly Dash → Vizro | ⬜ | |
| 6.F.9 | Replace `AGENTS.md` "Plotly Dash (Python)" conventions block with "Vizro" block | ⬜ | Vizro conventions: `vm.Page`, `custom_charts`, `data_manager.register_data`, cross-page filter pattern, port 7860, gunicorn `app:app`. |
| 6.F.10 | Update `AGENTS.md` Phase 6 line: "Vizro + DuckDB + HF Spaces" | ⬜ | |
| 6.F.11 | Remove Dash deps from `pyproject.toml` after Phase C is verified working | ⬜ | `dash`, `dash-bootstrap-components`, `dash-ag-grid` removed; keep `gunicorn`. |

### §6.HISTORY — Superseded Dash Plan (2026-06-02, replaced same day)

<details>
<summary><b>⚠ SUPERSEDED 2026-06-02</b> — Click to expand full Dash-based Phase 6 plan. Preserved for git history + sunk-cost accounting. Do not implement from this section; use §6.STACK through §6.DOCS above.</summary>

### Page 1 — Price Trends & Forecast ✅ DONE (2026-06-02)
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

### Page 2 — Seasonal Patterns
| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.2.1 | Seasonal heatmap: month × commodity price index | ⬜ | `px.imshow` with `mart_seasonal_patterns` pivoted to 12×4 matrix. `color_continuous_scale="RdYlGn_r"` (red = above avg, green = below avg). Y-axis: commodities, X-axis: months (Jan–Dec). Instant visual scan for seasonal patterns. |
| 6.2.2 | Monthly price line chart (filtered by driver toggle) | ⬜ | `go.Figure` with one trace per commodity. Filtered by `dcc.RadioItems` (Ramadan / Harvest / Year-End / All). When driver selected, highlights relevant months with `vrect` bands. |
| 6.2.3 | Ramadan overlay chart: price index T-3 to T+1 | ⬜ | Filter `mart_seasonal_patterns` where `flag_ramadan_*` columns are TRUE. Plot `price_index_vs_annual_avg` for each commodity. `add_hline(y=100)` as annual average baseline. One trace per commodity, bold lines. |
| 6.2.4 | Seasonal summary table (`dbc.Table`) | ⬜ | Aggregated from `mart_seasonal_patterns`: commodity, avg price, peak month, Ramadan premium (%). Computed as `(ramadan_avg - non_ramadan_avg) / non_ramadan_avg * 100`. Sortable via `dbc.Table` with `hover=True`. |
| 6.2.5 | Page-specific driver toggle (Ramadan / Harvest / Year-End / All) | ⬜ | `dcc.RadioItems(id="seasonal-driver")`. Filters `mart_seasonal_patterns` by relevant `flag_*` columns. `callback` returns filtered DataFrame to all 4 charts. |
| 6.2.6 | Wire page via single callback | ⬜ | `Input`: 3 global filters + `seasonal-driver`. `Output`: 4 chart figures + summary table children. Data source: `load_mart("mart_seasonal_patterns")`. |

### Page 3 — Geographic Disparity
| # | Task | Status | Notes |
|---|------|--------|-------|
| 6.3.1 | KPI cards: price index per island group (5 cards) | ⬜ | `dbc.Card` × 5 from `mart_geo_disparity`. Java = 100 baseline (hardcoded). Each card shows island group name, current price index, and YoY change (`yoy_change_index`). Clickable cards set island filter via callback to `dcc.Store`. |
| 6.3.2 | Indonesia choropleth map | ⬜ | `px.choropleth` with vendored GeoJSON (`dashboard/assets/indonesia_provinces.geojson`, ~1 MB). GeoJSON already vendored (G2). `locationmode="geojson-id"` with province names matched to `admin1` in `mart_geo_disparity`. Color scale: `price_index_vs_java`. Year slider via `dcc.Slider` with `go.Frame` animation. Only Cooking Oil has province-level data (Rice/Sugar/Flour = national aggregate only). |
| 6.3.3 | Island group comparison line chart (5 series, Java baseline) | ⬜ | `go.Figure` with 5 `go.Scatter` traces (one per island group). `add_hline(y=100, line_dash="dash", annotation_text="Java baseline")`. X-axis: year. Y-axis: `price_index_vs_java`. Color per island group. Filtered by commodity dropdown. |
| 6.3.4 | Province drill-down table (`dbc.Table`) | ⬜ | Filtered by selected island group. Columns: province, price index, YoY change, months with data. Sorted by price index ascending (cheapest first). Includes "coverage" honesty column noting data gaps (Rice/Sugar/Flour limited to national agg). |
| 6.3.5 | Data limitation callout (Cooking Oil only) | ⬜ | `dbc.Alert` with `color="warning"` explaining that geographic analysis is limited to Cooking Oil because Rice/Sugar/Flour have no market-level actual prices (only national avg market_id=974). Always visible on page. |
| 6.3.6 | Wire page via single callback | ⬜ | `Input`: 3 global filters. `Output`: KPI cards, choropleth figure, comparison chart figure, drill-down table children. Data source: `load_mart("mart_geo_disparity")`. |

### Page 4 — Commodity Signals
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
| 6.7.2 | (Unchanged) `export/export_json.py` — query all 4 mart models + forecast → static JSON | ✅ DONE | Writes to `dashboard/public/data/`. Retained as row-count verification artefact per §78 preservation |
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
| 8.3 | README: pipeline architecture (Mermaid diagram) | ✅ | Raw CSV → DuckDB → dbt → statsforecast → export_json.py → **Plotly Dash → HF Spaces** |
| 8.4 | README: dbt lineage graph screenshot | ⬜ | Deferred to Phase 6 — needs `dbt docs generate` + manual screenshot |
| 8.5 | README: key findings (4–6 quantified bullets) | ✅ | 6 findings from EDA confirmed |
| 8.6 | README: dashboard preview (4 screenshots) | ⬜ | Deferred to Phase 6 — Dash app not yet built |
| 8.7 | README: recommendations mapped to stakeholders | ✅ | Procurement Analyst + Category Manager tables |
| 8.8 | README: data limitations + validation findings | ✅ | Known Limitations + Data Quality Issues sections |
| 8.9 | README: forecasting methodology summary + link | ✅ | Links to `docs/model_methodology.md` |
| 8.10 | README: reproduction instructions | ⬜ | **NEEDS UPDATE** — replace `npm install`/`npm run dev` steps with `uv run python dashboard/app.py` + HF Spaces deploy command |
| 8.11 | README: lessons learned | ⬜ | **NEEDS UPDATE** — replace React hooks row with Dash callback patterns row |
| 8.12 | Finalize `docs/insights_log.md` with all 3 insight types: contextual, directional, actionable | ✅ | 13 findings across all 3 types — no edits needed |
| 8.13 | Live URL pinned in README and GitHub repo description | ⬜ | Deferred to Phase 6 — HF Spaces deploy not done (will be `https://albarpambagio-wfp-food-price.hf.space`) |

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
- [x] **Phase 6 scaffolding 2026-06-02**: Dash app skeleton — `app.py`, `pages/`, `components/`, `data_access.py` ✅ DONE
- [x] **Phase 6 scaffolding 2026-06-02**: All 4 dashboard pages (Plotly Dash + dash-bootstrap-components) ✅ DONE
- [x] **Phase 6 scaffolding 2026-06-02**: 12 files created, smoke test passed (`Pages: 4`) ✅ DONE
- [ ] **DEFERRED to Phase 6**: Dockerfile + HF Spaces metadata + push via `hf upload`
- [ ] **DEFERRED to Phase 6**: HF Spaces live URL (`https://albarpambagio-wfp-food-price.hf.space`)
- [ ] **DEFERRED to Phase 6**: dbt lineage screenshot + dashboard screenshots
- [x] **SUPERSEDED 2026-06-02**: Next.js + Shadboard + Recharts + Cloudflare Pages — replaced by Plotly Dash + dash-bootstrap-components + Hugging Face Spaces. See Phase 6 "Stack Change Decision" subsection for rationale.
- [x] **Phase 5g 2026-06-02**: G1 — `mart_price_trends_national.sql` for Page 1 multi-commodity trend ✅ DONE
- [x] **Phase 5g 2026-06-02**: G2 — Indonesia provinces GeoJSON vendored at `dashboard/assets/` ✅ DONE
- [x] **Phase 5g 2026-06-02**: G3 — `pearson_r_pre_2022` + `pearson_r_post_2022` columns in `mart_correlation_summary` ✅ DONE
- [x] **Phase 5g 2026-06-02**: G4 — Cooking Oil dual-forecast (primary + `post2022_robustness` toggle) documented in `forecast.json` metadata + §6.1.2 wireframe ✅ DONE
- [x] **Phase 5g 2026-06-02**: G5 — AGENTS.md stack sweep (6 sections: L13, L70-73, L93, L338, L388, L495) ✅ DONE
- [x] **Phase 5g 2026-06-02**: G6 — LEARNINGS.md §75 SUPERSEDED banner + §81-§86 Dash learnings ✅ DONE
- [x] **Phase 5g 2026-06-02**: G7 + G8 — README.md + `wfp-food-price-intelligence-project-plan.md` stack sync ✅ DONE
- [x] **Phase 5g 2026-06-02**: G9 — Remove dead `current_step_map` dict in `run_pipeline.py:129` ✅ DONE
- [x] **Phase 5g 2026-06-02**: G10 — Move `transform_status="running"` to before `dbt seed` in `run_pipeline.py:179` ✅ DONE
- [x] **Phase 5g 2026-06-02**: G11 — Add `dbt source freshness` step to pipeline (per LEARNINGS §49) ✅ DONE
- [x] **Phase 5g 2026-06-02**: G12 — Sync `requirements.txt` with `pyproject.toml` (or delete) ✅ DONE
- [x] **Phase 5g 2026-06-02**: G13 — Normalize JSON export date format to `"%Y-%m-%d"` in `export_json.py:export_table()` ✅ DONE

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
| Phase 6 | `feat: dashboard (Plotly Dash + dash-bootstrap-components + HF Spaces + export)` | Frontend — supersedes the previously-planned Next.js+Shadboard+CF Pages version (LEARNINGS.md §75 overridden 2026-06-02; chart-engine parity per §80 realized) |
| Phase 7 | `docs: forecasting methodology` | `model_methodology.md` + `forecast_runbook.md` |
| Phase 8 | `docs: README, insights, recommendations` | Final packaging — README, insights_log verified |
| Phase 3f | `fix: 11 pipeline gaps — ramadan cross-year, hardcoded date, unified run_id, dbt log, func split, docs, pep723 pins, lineage dedup` | Cross-phase gap closing post-Phase-5f |
| Phase 6 plan | `docs: phase 6 stack change — Next.js+Shadboard+CF Pages → Plotly Dash+dbc+HF Spaces` | This document update; LEARNINGS.md §75 marked superseded; rationale in Phase 6 "Stack Change Decision" subsection |

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
