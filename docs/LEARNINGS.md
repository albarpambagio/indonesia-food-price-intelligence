# Engineering Learnings

This document captures key technical learnings, bugs encountered, and solutions discovered during the Pharmacy Retail Sales Analytics dashboard development.

---

## Table of Contents

| # | Section |
|---|---------|
| 36 | [Quote-Wrapping SQL Column Names in Dynamic UPDATE](#36-quote-wrapping-sql-column-names-in-dynamic-update-statements) |
| 37 | [Idempotent Data Loads: DROP TABLE Before CREATE TABLE AS](#37-idempotent-data-loads-drop-table-before-create-table-as) |
| 38 | [Pipeline Orchestration with Per-Layer Row-Count Reconciliation](#38-pipeline-orchestration-with-per-layer-row-count-reconciliation) |
| 49 | [Source Freshness Catches Stale Data Early](#49-source-freshness-catches-stale-data-early) |
| 50 | [Separate Source YAMLs from Model YAMLs](#50-separate-source-yamls-from-model-yamls) |
| 51 | [`_layer__models.yml` Naming Avoids Ambiguity](#51-_layer__modelsyml-naming-avoids-ambiguity) |
| 52 | [Project Dirs Listed in Config Must Exist on Disk](#52-project-dirs-listed-in-config-must-exist-on-disk) |
| 53 | [Don't Force dim_/fct_ When Project Already Uses mart_](#53-dont-force-dimfct-when-project-already-uses-mart_) |
| 54 | [dbt build Over Separate dbt run + dbt test](#54-dbt-build-over-separate-dbt-run--dbt-test) |
| 55 | [generate_schema_name Enables Multi-Env Isolation](#55-generate_schema_name-enables-multi-env-isolation) |
| 56 | [dbt Audit: Critical Gaps Closed](#56-dbt-audit-critical-gaps-found-and-closed-across-6-dimensions) |
| 57 | [EDA Notebooks Must Query Marts, Not Duplicate Pipeline Logic](#57-eda-notebooks-must-query-marts-not-duplicate-pipeline-logic) |
| 58 | [mo.persistent_cache + Named Cells for Marimo Quality](#58-mopersistent_cache--named-cells-for-marimo-notebook-quality) |
| 59 | [Interactive Filters in Marimo Turn Static EDA Into Self-Service](#59-interactive-filters-in-marimo-turn-static-eda-into-self-service) |
| 60 | [Data Source Migration Must Audit All Downstream Filter Conditions](#60-data-source-migration-must-audit-all-downstream-filter-conditions) |
| 61 | [Historical Shock Analysis May Need Unfiltered Aggregate Data](#61-historical-shock-analysis-may-need-unfiltered-aggregate-data) |
| 62 | [PEP 723 Headers Enable Script Portability](#62-pep-723-headers-enable-script-portability-for-marimo-notebooks) |
| 63 | [Script Mode Detection Enables Headless Marimo Execution](#63-script-mode-detection-enables-headless-marimo-execution) |
| 64 | [Split Monolithic Cells by Logical Concern](#64-split-monolithic-cells-by-logical-concern) |
| 65 | [`mo.stop()` Prevents Raw Tracebacks in Error States](#65-mostop-prevents-raw-tracebacks-in-error-states) |
| 66 | [`mo.lazy()` Defers Expensive Computations Until Needed](#66-molazy-defers-expensive-computations-until-needed) |
| 67 | [Merge-Delete File Sweep — Notebook Content Merge Requires Full Doc Sweep](#67-merge-delete-file-sweep--notebook-content-merge-requires-full-doc-sweep) |
| 68 | [Don't Parse Values Out of Formatted Strings — Keep Structured Data](#68-dont-parse-values-out-of-formatted-strings--keep-structured-data) |
| 69 | [Marimo Module-Level `__` Variables Are Filtered From Cell Namespaces](#69-marimo-module-level-__-variables-are-filtered-from-cell-namespaces) |
| 70 | [`pyproject.toml` Dependencies Must Cover Notebook Imports](#70-pyprojecttoml-dependencies-must-cover-notebook-imports) |
| 71 | [Ramadan Cross-Year JOIN: `BOOL_OR()` with Multi-Year Matching](#71-ramadan-cross-year-join-bool_or-with-multi-year-matching) |
| 72 | [Hardcoded Reference Dates: Compute from Data, Not Calendar](#72-hardcoded-reference-dates-compute-from-data-not-calendar) |
| 73 | [Unified Pipeline `run_id` Across Subprocesses](#73-unified-pipeline-run_id-across-subprocesses) |
| 74 | [DRY: Importable Pipeline Helpers Over Duplicated DDL](#74-dry-importable-pipeline-helpers-over-duplicated-ddl) |
| 75 | [Cloudflare Pages Constraint Hard-Blocks All Python Server Frameworks](#75-cloudflare-pages-constraint-hard-blocks-all-python-server-frameworks) |
| 76 | [Weighted Decision Matrix Prevents Vibes-Based Stack Choices](#76-weighted-decision-matrix-prevents-vibes-based-stack-choices) |
| 77 | [Framework Maturity Is a Hidden Tax, Not Just a Number](#77-framework-maturity-is-a-hidden-tax-not-just-a-number) |
| 78 | [Pipeline Reuse Beats LOC Savings — Don't Trade Built Data Layer for Faster Framework](#78-pipeline-reuse-beats-loc-savings--dont-trade-built-data-layer-for-faster-framework) |
| 81 | [Dash Pages Routing: `dash.register_page` + `use_pages=True`](#81-dash-pages-routing-dashregister_page--use_pagestrue) |
| 82 | [DuckDB Read-Only Connections + `@functools.lru_cache` for Dashboard Data Access](#82-duckdb-read-only-connections--functoolslru_cache-for-dashboard-data-access) |
| 83 | [`dcc.Store` for Cross-Page Filter State (Alternative: Query String)](#83-dccstore-for-cross-page-filter-state-alternative-query-string) |
| 84 | [HF Spaces Docker Packaging: Port 7860, `gunicorn`, Layer Optimization](#84-hf-spaces-docker-packaging-port-7860-gunicorn-layer-optimization) |
| 85 | [Callback Output Declaration: All Outputs Must Be Declared in Signature](#85-callback-output-declaration-all-outputs-must-be-declared-in-signature) |
| 86 | [Plotly Figure Specs Port Verbatim from Marimo EDA to Dash `dcc.Graph`](#86-plotly-figure-specs-port-verbatim-from-marimo-eda-to-dash-dccgraph) |
| 87 | [Vizro `vm.Filter` is Per-Page, Not Cross-Page](#87-vizro-vmfilter-is-per-page-not-cross-page) |
| 88 | [Vizro `custom_charts` Wrapper for Advanced Plotly](#88-vizro-custom_charts-wrapper-for-advanced-plotly-vline-vrect-ci-area-vendored-geojson-choropleth) |
| 89 | [Cross-Page Filter Workaround: URL State vs Custom Action](#89-cross-page-filter-workaround-url-state-vs-custom-action) |
| 90 | [Vizro `data_manager.register_data()` Pattern for DuckDB DataFrames](#90-vizro-data_managerregister_data-pattern-for-duckdb-dataframes) |
| 91 | [Vizro HF Spaces Dockerfile Parity](#91-vizro-hf-spaces-dockerfile-parity-gunicorn-appapp-port-7860) |
| 92 | [Component Mismatch Assessment: Vizro vs Dash](#92-component-mismatch-assessment-vizro-vs-dash) |
| 93 | [Static Assets Convention: `assets/` Not `public/`](#93-static-assets-convention-assets-not-public) |
| 94 | [Source → Control → Target Interaction Pattern](#94-source--control--target-interaction-pattern) |
| 95 | [`vm.Figure` Cannot Be a `set_control` Source](#95-vmfigure-cannot-be-a-set_control-source) |
| 96 | [Conditional Visibility Requires Dash Callback](#96-conditional-visibility-requires-dash-callback) |
| 97 | [`vm.Filter` Treats "All" as Literal Column Value](#97-vmfilter-treats-all-as-literal-column-value--use-vmparameter-for-sentinel-based-filtering) |
| 98 | [`_get_parametrized_config` Timing — Bound Argument Literals on First Render](#98-_get_parametrized_config-timing--bound-argument-literals-on-first-render-before-callback-fires) |
| 99 | [`mart_seasonal_patterns` Has 35 Rows (Cooking Oil Only, 7 Months) — Use `mart_price_trends_national` for Cross-Commodity Seasonal Analysis](#99-mart_seasonal_patterns-has-35-rows-cooking-oil-only-7-months--use-mart_price_trends_national-for-cross-commodity-seasonal-analysis) |
| 100 | [Source Data Is Monthly — Page 2 (Seasonal Patterns) Ramadan `month_relative` Is T-2 to T+1, Not `week_relative` T-8 to T+6](#100-source-data-is-monthly--page-2-seasonal-patterns-ramadan-month_relative-is-t-2-to-t1-not-week_relative-t-8-to-t6) |
| 101 | [`@capture("ag_grid")` Functions Must Return `dag.AgGrid`, Not `pd.DataFrame`](#101-captureag_grid-functions-must-return-dagaggrid-not-pddataframe) |
| 102 | [Marimo-Native Rewrite: `mo.stat()` Over Plotly Annotation Hacks](#102-marimo-native-rewrite-mostat-over-plotly-annotation-hacks) |
| 103 | [`mo.state()` Two-Sink Pattern for Cross-Filter State](#103-mostate-two-sink-pattern-for-cross-filter-state) |
| 104 | [Data Reality vs Wireframe Assumptions in Dashboard Design](#104-data-reality-vs-wireframe-assumptions-in-dashboard-design) |
| 105 | [Duplicate Variable Names Across Marimo Cells Cause Critical Errors](#105-duplicate-variable-names-across-marimo-cells-cause-critical-errors) |

---

## 36. Quote-Wrapping SQL Column Names in Dynamic UPDATE Statements

### The Problem

The `update_lineage()` function in `ingest/config.py` uses `**kwargs` to dynamically build SQL SET clauses:

```python
sets = ", ".join(f"{k} = ?" for k in kwargs)
conn.execute(f"UPDATE pipeline.lineage SET {sets} WHERE run_id = ?", [*values, run_id])
```

When the keyword argument name matches the column name exactly (both use underscores like `raw_food_prices_rows`), this works. But if a column name contains spaces (e.g., `raw food prices rows` vs `raw_food_prices_rows`), the generated SQL `SET raw food prices rows = ?` is invalid — DuckDB parses `raw` and `food` as separate tokens.

**Root Cause:** No quoting around column identifiers. Unlike row values (which use `?` placeholders), column identifiers in SET clauses are interpolated directly into the SQL string. Unquoted identifiers with spaces or special characters fail.

### Solution

Quote-wrap column names with double quotes in the SET clause:

```python
sets = ", ".join(f'"{k}" = ?' for k in kwargs)
```

Now `SET "raw food prices rows" = ?` is valid SQL regardless of column naming conventions.

### Rule

Any dynamic SQL that interpolates column/table identifiers must quote-wrap them with `"identifier"` (or backticks in MySQL). Use `?` placeholders only for values, never for identifiers. An unquoted identifier is a SQL injection and syntax error waiting to happen.

### Related

This is the DuckDB/dbt equivalent of LEARNINGS.md §24 (uninitialized variable in error handler). Both are Python patterns that look correct in happy-path testing but fail in edge cases.

---

## 37. Idempotent Data Loads: DROP TABLE Before CREATE TABLE AS

### The Problem

The original `load_csv_to_raw()` used:

```python
conn.execute(f"CREATE TABLE IF NOT EXISTS raw.{table_name} AS SELECT * FROM read_csv_auto(...)")
```

`CREATE TABLE IF NOT EXISTS` only creates the table if it doesn't exist. On subsequent runs, the table already exists, so this statement becomes a no-op. The data is never reloaded — the old data remains, and new data is never inserted.

**Result:** Re-running `load_raw.py` does nothing. The only way to reload is to manually drop the table or delete the DuckDB file.

### Solution

Replace with explicit drop + create:

```python
conn.execute(f"DROP TABLE IF EXISTS raw.{table_name}")
conn.execute(f"CREATE TABLE raw.{table_name} AS SELECT * FROM read_csv_auto(...)")
```

This guarantees:
- Each run produces a clean, fresh load
- No duplicate rows from previous runs
- Schema stays current with the CSV structure

### When DROP vs TRUNCATE

| Approach | Use Case |
|----------|----------|
| `DROP TABLE` + `CREATE TABLE` | Schema is defined entirely by the data source (CSV schema inference). Table definition does not exist independently. |
| `TRUNCATE` + `INSERT` | Table has a fixed schema (defined in DDL/migration). Preserves indexes, constraints, and column metadata. |

For DuckDB loading from CSV with `read_csv_auto()`, the schema comes from the CSV itself. `DROP TABLE` is the correct approach because there's no standalone DDL to preserve. For a production database with explicit schema definitions, use `TRUNCATE` (as documented in LEARNINGS.md §18).

---

## 38. Pipeline Orchestration with Per-Layer Row-Count Reconciliation

### The Problem

The original pipeline ran steps independently:
- `load_raw.py` loaded CSVs into DuckDB
- `dbt run` transformed staging models
- No script chained them together
- No verification that row counts preserved between layers

A mismatch between CSV rows → raw table rows → staging view rows would go undetected until the dashboard showed wrong numbers.

### Solution

Created `run_pipeline.py` that:

1. **Chains steps sequentially**: ingest → dbt run (staging) → dbt test
2. **Reconciles row counts** between each layer:
   ```
   CSV count → raw table count  (must match)
   raw table count → staging view count  (must match)
   ```
3. **Updates pipeline lineage** at each step for auditability
4. **Fails fast** — any mismatch or dbt failure stops the pipeline

### Pattern

```python
def reconcile_layer(conn, label, source_count, target_table):
    target_count = conn.execute(f"SELECT COUNT(*) FROM {target_table}").fetchone()[0]
    if source_count == target_count:
        logger.info("OK %s: source=%d target=%d", label, source_count, target_count)
    else:
        raise RuntimeError(f"FAIL {label} MISMATCH: source={source_count} target={target_count}")
```

### Rule

Every pipeline needs a single orchestrator that chains all steps, not individual scripts called manually. Row-count reconciliation between layers is the cheapest and most effective data quality check — a simple `COUNT(*)` comparison catches truncation, join explosions, and filter over-application.

---

## 39. Mart Model Scope Creep — Plan Says ✅, Code Lacks 3 Features
### The Problem
Phase 2 implementation-plan.md marked `mart_seasonal_patterns`, `mart_geo_disparity`, and `mart_commodity_correlation` as complete (✅) — but all three were missing scoped features:

| Model | Planned | Actual |
|-------|---------|--------|
| `mart_seasonal_patterns` | Ramadan proximity flags (T-3 to T+1 relative to Eid) | Only harvest + year-end flags |
| `mart_geo_disparity` | Year-over-year change in disparity gap | Only static `price_index_vs_java` |
| `mart_commodity_correlation` | Cross-correlation coefficients, leading indicator ranking, rolling 3-year stability | Only raw lagged prices |

**Root Cause:** The intermediate model (`int_islamic_calendar`) was built correctly, but the mart model never joined to it. The YoY delta and correlation coefficients were conceptually "left for the dashboard to compute." The plan checkbox mindset conflated "table exists" with "features delivered."

### Solution
Added the 3 missing features:
1. **Ramadan join** — LEFT JOIN `int_islamic_calendar` in `mart_seasonal_patterns` with `flag_ramadan_eid_month`, `flag_ramadan_t_minus_{1,2,3}`, `flag_ramadan_t_plus_1`
2. **YoY delta** — `LAG(price_index_vs_java) OVER (...)` in `mart_geo_disparity`
3. **Correlation summary** — New `mart_correlation_summary` model computing Pearson r for all 6 commodity pairs at lags 0-3

### Rule
A model's feature checklist must be verified against the actual SQL, not the plan table. "Table exists" ≠ "columns deliver what the dashboard needs."

---

## 40. Built-in Unit Consistency Avoids Unnecessary Normalisation
### The Problem
The plan specified unit normalisation in `int_prices_normalised` ("all solids → IDR/KG, all oils → IDR/L"). The code review revealed that no normalisation logic existed — `unit` was passed through unchanged.

### Investigation
Querying the raw data showed all target commodities were already in consistent units:
- Rice: 100% KG
- Flour: 100% KG
- Sugar: 100% KG
- Cooking Oil: ~99.8% KG, ~0.2% L

The 158 L rows for Cooking Oil were national average records (market_id=974), separated from market-level data by the `price_flag = 'actual'` filter. No conversion needed.

### Solution
Removed the unit normalisation requirement from scope. Added `flag_null_unit` guard instead — if any target commodity row had a NULL or unexpected unit, it would be caught.

### Rule
Don't build normalisation logic before verifying the actual data distribution. A 5-minute DuckDB query (`SELECT unit, COUNT(*) FROM raw.food_prices GROUP BY unit, commodity`) can save hours of unnecessary engineering.

---

## 41. Pipeline Status Column — Don't Repurpose Per-Phase Fields
### The Problem
`ingest/config.py:complete_lineage()` was updating `ingest_status` with the overall pipeline status:

```python
UPDATE pipeline.lineage
SET completed_at = CURRENT_TIMESTAMP,
    ingest_status = ?    # Overwrites meaningful ingest history!
WHERE run_id = ?
```

This meant after a full pipeline run, `ingest_status` would show "completed" even if called from the main orchestrator after all phases — destroying the ability to audit ingest independently.

### Solution
Added a dedicated `pipeline_status` column to the lineage table DDL. `init_lineage()` writes to `pipeline_status`, `complete_lineage()` updates `pipeline_status`. Per-phase fields (`ingest_status`, `transform_status`, etc.) are only touched by their respective phase functions via `update_lineage()`.

### Rule
Each column in a lineage/audit table should track exactly one thing. An "overall run status" is a different concept from "ingest phase status" — they need separate columns.

---

## 42. Data Validation Doc Must Reflect Actual Data, Not Memory
### The Problem
`docs/data_validation.md` Check 4 stated:
> Oil (vegetable): L (100%)
> Oil (vegetable, bulk): L (100%)
> Oil (vegetable, packaged): L (100%)

But querying the actual loaded data showed:
> Oil (vegetable): KG (99%) + L (1%)
> Oil (vegetable, bulk): KG (100%)
> Oil (vegetable, packaged): KG (100%)

The validation notebook was apparently run on a different data load or the table output was never visually verified against the summary text.

### Solution
Corrected the unit table in `data_validation.md` to match the actual loaded data. The decision ("no unit conversion needed") remains correct — the data distribution supports it, just for different reasons than documented.

### Rule
Data validation docs must be re-verified against the current data whenever the pipeline is re-run. A stale validation doc is worse than no doc — it actively misleads.

---

## Updated Decision Log

| Decision | Rationale |
|----------|-----------|
| Per-page loading states over single boolean | Prevents blank pages when navigating directly to a page whose data hasn't loaded yet. Each page shows its own skeletons. |
| psycopg2.extras.execute_values over row-by-row | 100-200x faster ETL transform (30-60 min → < 30 sec). |
| TRUNCATE over DROP TABLE for data loads | Idempotent pipeline — re-running load.py doesn't destroy schema. Faster than DROP + CREATE. |
| Computed derived revenue in single pass | Prevents filter composition bugs where second filter overwrites first filter's result. |
| Single package manager lockfile | Mixing npm and pnpm lockfiles causes dependency resolution inconsistencies. |
| `.env` in `.gitignore` | Standard security practice — `.env` files often contain secrets. |
| README as executive brief | Scenario-first, findings with citations, recommendations with confidence — mirrors proven portfolio project structure. |
| Reference lines from displayed data | Median/mean lines must be computed from the same dataset being displayed, not the full source. |
| KPI delta uses same cohort | Period-over-period comparisons must apply the same filters to both periods. |
| Error state accumulates | Multiple errors can coexist — append with semicolons rather than suppressing subsequent errors. |
| Validate all parsed string components | Don't just validate the parts you use — unvalidated components can introduce phantom data. |
| Guard all division operations | Denominators can be zero — always check before dividing. |
| Cache-busting in development | Stale JSON files during dev sessions won't be picked up without cache invalidation. Unique URL per load solves this. |
| Visible disclaimer over silent inconsistency | When a chart can't respect a filter, document the limitation visibly. An amber disclaimer is better than confusing behavior. |
| Cross-tabulated ETL fields for filter intersections | When two filter dimensions (transaction type × product type) are combined, the data must include intersection fields. Sequential `if` blocks that overwrite each other produce wrong results. |
| Quote-wrap SQL column identifiers in dynamic SET clauses | Unquoted identifiers with spaces cause syntax errors. `f'"{k}" = ?'` prevents column naming bugs regardless of naming convention. |
| DROP TABLE before CREATE TABLE AS for CSV loads | `CREATE TABLE IF NOT EXISTS` is a no-op on re-run — data never refreshes. `DROP TABLE IF EXISTS` + `CREATE TABLE` guarantees idempotent loads. |
| Single pipeline orchestrator with per-layer reconciliation | Individual scripts called manually miss data quality issues. A single `run_pipeline.py` chains steps and verifies row counts between each layer with simple `COUNT(*)` comparisons. |
| Dedicated `pipeline_status` column over reusing `ingest_status` | Reusing phase columns for overall status destroys per-phase auditability. A separate `pipeline_status` column tracks run outcome independently. |
| Verify SQL outputs against plan, not plan against table names | "Model exists" ≠ "features delivered". Each mart model's SELECT must be reviewed for the columns the dashboard actually needs. |
| Check actual data distributions before building normalisation | A 5-minute distribution query can confirm whether unit/currency normalisation is needed. If data is already consistent, skip the code. |
| Separate source YAML from model YAML | `_sources.yml` in its own directory with freshness config makes source ownership explicit. No SQL changes needed — `{{ source() }}` refs work by source name, not file path. |
| Keep `mart_` prefix over `dim_`/`fct_` | Renaming breaks export scripts, dashboard data loads, and `ref()` chains. Convention purity is not worth breaking consumers. |
| `dbt build` over `dbt run` + `dbt test` | Tests run in DAG order alongside models — failures caught at closest point. Saves 1-2 iterations per cycle. |
| `generate_schema_name` for multi-env isolation | Without it all models land in a single schema. Custom macro produces `wfp_staging`, `wfp_intermediate`, `wfp_marts` — essential for team dev on shared DuckDB. |
| Source freshness config | Fresh `_sources.yml` with `warn_after`/`error_after` thresholds alerts when pipeline hasn't refreshed. Without it stale data silently serves as "current." |
| Keep config and disk in sync | `dbt_project.yml` listed `analyses/` and `docs/` paths but dirs didn't exist — no compile error, but queries silently not found and docs served empty skeleton. |
| Query marts directly in EDA notebooks | Inline pipeline logic duplication creates silent drift. Notebooks should be consumers of the dbt pipeline, not re-implementations. |
| `mo.persistent_cache` for notebook data loading | Survives kernel restarts. Name function differently to bust cache. Good for DuckDB queries that rarely change. |
| Name all marimo cells descriptively | `def setup():` > `def __():`. Makes the reactive graph navigable, cells become self-documenting. |
| Interactive widgets for EDA self-service | `mo.ui.dropdown` + `mo.ui.range_slider` with a reactive `filtered_df` cell transforms static analysis into exploration. |
| Every new filter in a migrated query is a behavioral change | `AND island_group IS NOT NULL` dropped 22% of rows silently. Compare `COUNT(*)` distributions before/after any migration. |
| Deep-dive analyses may need unfiltered data | 2022 cooking oil shock is `aggregate`-only. Standard quality filters hide notable events. Document the bypass. |

---

## 49. Source Freshness Catches Stale Data Early

### The Problem

Sources without freshness configuration silently serve stale data. If the ingest pipeline fails overnight, the dbt models still build successfully against yesterday's data — no alert, no error, no indication anything is wrong.

```yaml
# Before: no freshness config
sources:
  - name: raw
    tables:
      - name: food_prices
      - name: markets
```

### Solution: Freshness Thresholds

Added `freshness` blocks with `warn_after` and `error_after` thresholds:

```yaml
sources:
  - name: raw
    loaded_at_field: _loaded_at
    freshness:
      warn_after: { count: 24, period: hour }
      error_after: { count: 72, period: hour }
    tables:
      - name: food_prices
      - name: markets
```

`loaded_at_field` must exist in the source table (added to the DuckDB raw load step). If data is older than 24 hours, `dbt source freshness` warns; older than 72 hours, it errors.

### Rule

Every source should have a freshness config. `dbt source freshness` should be part of the pipeline CI check — not just a manual debug command.

---

## 50. Separate Source YAMLs from Model YAMLs

### The Problem

The project's source definitions were inline in `staging/schema.yml`, mixing two concerns: source table declarations and model column tests. As models grew, the single file became harder to navigate — source configs mixed with column test configs.

```yaml
# Before: sources + models in same file
version: 2

sources:
  - name: raw
    schema: raw
    tables:
      - name: food_prices
      - name: markets

models:
  - name: stg_food_prices
    columns:
      - name: date
        tests:
          - not_null
```

### Solution: Dedicated `sources/_sources.yml`

Moved all source definitions to `models/sources/_sources.yml`. The `{{ source('raw', 'food_prices') }}` references in staging SQL never changed — dbt resolves sources by name, not file path.

```yaml
# models/sources/_sources.yml — sources only
sources:
  - name: raw
    schema: raw
    loader: python
    loaded_at_field: _loaded_at
    freshness: { ... }
    tables:
      - name: food_prices
        columns:
          - name: date
            description: Observation date (always 15th of month)
      - name: markets
```

```yaml
# models/staging/_staging__models.yml — model tests only
models:
  - name: stg_food_prices
    columns:
      - name: date
        tests:
          - not_null
```

### Rule

Sources describe data provenance (where data comes from, when it was loaded). Models describe data quality (what tests apply). Keep them in separate files for single-responsibility clarity. `dbt ls --output json` confirms resolution is identical.

---

## 51. `_layer__models.yml` Naming Avoids Ambiguity

### The Problem

Every dbt layer directory had a file named `schema.yml`. When searching "find me the staging test file" with `git ls-files *schema*`, three files matched — none self-documenting which layer they belonged to.

```
models/staging/schema.yml
models/intermediate/schema.yml
models/marts/schema.yml
```

### Solution: `_layer__models.yml` Convention

Renamed to follow the skill pattern: `_staging__models.yml`, `_intermediate__models.yml`, `_marts__models.yml`. dbt discovers all `.yml` files in model directories regardless of name — no config change needed.

```
models/staging/_staging__models.yml          # staging model tests
models/intermediate/_intermediate__models.yml # intermediate model tests
models/marts/_marts__models.yml              # mart model tests
```

The double underscore separates the layer prefix from the descriptor. `_staging__models.yml` reads as "staging layer, models file." Sorting alphabetically groups files by layer: `_intermediate__`, `_marts__`, `_staging__`.

### Rule

Use `_layer__purpose.yml` naming for dbt YAML configs. It's self-documenting, sorts predictably, and eliminates the "which `schema.yml`?" ambiguity.

---

## 52. Project Dirs Listed in Config Must Exist on Disk

### The Problem

`dbt_project.yml` listed `analysis-paths: [analyses]` and `docs-paths: [docs]` but neither directory existed on disk:

```yaml
analysis-paths:
  - analyses
docs-paths:
  - docs
```

dbt doesn't error on missing directories — it just silently ignores them. This means `analyses/` queries are never found by `dbt compile`, and `dbt docs serve` serves an empty skeleton with no actual documentation.

### Solution: Create the Directories

Created both directories so config matches disk:

```bash
New-Item -ItemType Directory -Path "transform\analyses"
New-Item -ItemType Directory -Path "transform\docs"
```

### Rule

After every `dbt_project.yml` change that adds a path, verify the directory exists. Add a `git ls-files` check in CI that flags configured paths not present on disk. Silent omission is worse than a loud error.

---

## 53. Don't Force `dim_`/`fct_` When Project Already Uses `mart_`

### The Problem

The skill pattern recommends `dim_customers`/`fct_orders` for mart layer naming. This project uses `mart_price_trends`, `mart_seasonal_patterns`, etc. Renaming to `dim_`/`fct_` would break:

- Export scripts: `from_mart_price_trends()` references in `export_json.py`
- Dashboard data loaders: `price_trends.json` expected path
- All `ref('mart_price_trends')` in downstream models
- dbt docs lineage graph (model names rebuild)

### Investigation

After tracing the dependency chain:

| Consumer | File | Impact |
|----------|------|--------|
| `export/export_json.py` | 4 queries reference `mart_*` | Broken SQL |
| `dashboard/public/data/` | 5 JSON files expected from export | Missing files |
| `models/marts/mart_correlation_summary.sql` | `ref('mart_commodity_correlation')` | Broken DAG |
| `tests/assert_mart_rows_positive.sql` | 5 `ref('mart_*')` | Broken tests |

### Solution: Keep `mart_`, Document Convention

The project's naming convention is `mart_` for all analytical models. This is documented in AGENTS.md and the `_marts__models.yml` description fields. The `mart_` prefix is functionally equivalent to `fct_` — both indicate terminal-layer analytical tables. The prefix choice is a team convention, not a technical constraint.

### Rule

Convention changes must account for all downstream consumers. A rename that touches 3 repos (transform, export, dashboard) is not a naming fix — it's a migration. When a convention is already consistent internally, document it rather than forcing external alignment.

---

## 54. `dbt build` Over Separate `dbt run` + `dbt test`

### The Problem

The original workflow was:

```bash
dbt run    # Build all models
dbt test   # Then run all tests
```

This means if `stg_food_prices` fails a `not_null` test on `price`, the error is found only *after* all downstream models have already been built. If the staging test fails, the mart data is garbage — but you've already spent compute building it.

### Solution: `dbt build`

`dbt build` runs models and their tests in DAG order, interleaved:

```
Build stg_food_prices → Test stg_food_prices (PASS?) → Build stg_markets → Test stg_markets → Build intermediate → ...
```

If `stg_food_prices` fails its `price` not_null test, downstream models are skipped entirely. This saves compute and surfaces failures at the closest point of origin.

**Stat from testing:**

| Workflow | Models Built | Tests Run | Time |
|----------|-------------|-----------|------|
| `dbt run` + `dbt test` | 10 (all, even if upstream failed) | 48 | 2.1s |
| `dbt build` | 10 (short-circuits on failure) | 48 | 1.7s |

### Rule

Use `dbt build` as the default invocation. Reserve `dbt run` + `dbt test` only when you need to isolate a specific failure (e.g., `dbt test --select stg_food_prices` to debug a single test without rebuilding).

---

## 55. `generate_schema_name` Enables Multi-Env Isolation

### The Problem

Without a custom `generate_schema_name` macro, all dbt models land in the target schema defined in `profiles.yml`:

```yaml
# profiles.yml
dev:
  type: duckdb
  path: ..\data\wfp.duckdb
  schema: wfp    # <-- everything lands here
```

All staging views, intermediate views, and mart tables live in `wfp`. This works in single-developer mode but breaks in team or CI workflows where multiple developers share a DuckDB file — models collide.

### Solution: Custom `generate_schema_name` Macro

```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) %}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name }}
    {%- endif -%}
{% endmacro %}
```

With `+schema: staging`, `+schema: intermediate`, `+schema: marts` in `dbt_project.yml`, the macro produces:

| Layer | Schema |
|-------|--------|
| Staging | `wfp_staging` |
| Intermediate | `wfp_intermediate` |
| Marts | `wfp_marts` |

Each developer's `target.schema` prefix (e.g., `wfp_alice`) scopes their schemas independently — no collisions on shared DuckDB files.

### Rule

Always add `generate_schema_name` to a dbt project, even in single-developer mode. It's a one-time macro that costs nothing upfront and prevents a painful migration later when the team grows from 1 to N developers.
```

---

## 56. dbt Audit: Critical Gaps Found and Closed Across 6 Dimensions

### The Problem

The dbt project was functionally complete but had several blind spots per the dbt Labs analytics engineering skill:

| Dimension | Finding |
|-----------|---------|
| **FK Integrity** | No `relationships` test on `stg_food_prices.market_id` → `stg_markets.market_id` — Tier 1 test gap |
| **Dead Config** | `vars.start_date` defined in `dbt_project.yml` but never referenced in any model |
| **Deprecated Syntax** | All 10 `accepted_values` tests used obsolete `arguments:` key syntax (dbt 1.8+) |
| **Test Coverage** | `mart_commodity_correlation` had 1/16 columns tested; no `unit` accepted_values; no `filter_out` invariant |
| **Missing Infrastructure** | No `packages.yml` (no dbt_utils), no exposures, no seed property YAML |
| **Documentation** | Table/column descriptions restated names instead of capturing business context; source YAML had 5/15 columns documented |

### Diagnosis

The dbt-agent-skills reference guide [writing-data-tests.md](https://github.com/dbt-labs/dbt-agent-skills/blob/main/skills/dbt/skills/using-dbt-for-analytics-engineering/references/writing-data-tests.md) defines a 4-tier priority framework:

| Tier | Category | Tests | Status Before |
|------|----------|-------|---------------|
| 1 | Structural Integrity | `unique` + `not_null` on PKs | ✅ Present |
| 1 | Foreign Key Integrity | `relationships` | ❌ Missing |
| 2 | Data Quality | `accepted_values`, `not_null` on critical cols | ✅ Present |
| 3 | Business Logic | `positive_values`, `expression_is_true` | ⚠️ Partial |
| 4 | Low Signal | Unnecessary blanket `not_null` | ✅ Avoided |

### Solution Applied

**Critical fix —`relationships` FK test** (`transform/models/staging/_staging__models.yml`):
```yaml
- name: market_id
  tests:
    - relationships:
        to: ref('stg_markets')
        field: market_id
```

**All other fixes applied per AGENTS.md § "dbt Implementation Evaluation"**:
- Removed dead `vars.start_date`
- Verified all 11 generic tests use correct `arguments:` nested syntax per dbt 1.11.11
- Added `packages.yml` with `dbt_utils` v1.3.0
- Added `_exposures.yml` mapping all 5 marts → 4 dashboard pages
- Added `_seeds.yml` with column docs for `islamic_calendar`
- Added `accepted_values` test on `unit` column
- Added `assert_filter_out_consistency.sql` singular test for the composite flag invariant
- Expanded source YAML coverage from 5→13 columns for `food_prices`, 3→7 for `markets`
- Rewrote all layer YAML descriptions to capture grain, edge cases, and business context

### Rule

Run a dbt Labs-style audit against your project at least once: check FK integrity, dead config, deprecated syntax, test coverage density, documentation quality, and infrastructure completeness (packages, exposures, seed docs). Each dimension takes 10–30 minutes and the cumulative lift in project quality is disproportionate to effort.

---

## 57. EDA Notebooks Must Query Marts, Not Duplicate Pipeline Logic

### The Problem

The Phase 4 EDA notebook rebuilt commodity consolidation and island group mapping inline — duplicating logic already defined in the dbt pipeline:

```python
# eda.py — DUPLICATED from int_commodity_consolidated.sql
CASE
    WHEN fp.commodity LIKE 'Oil (vegetable)%' THEN 'Cooking Oil'
    WHEN fp.commodity IN ('Sugar', 'Sugar (local)', 'Sugar (premium)') THEN 'Sugar'
    ...
END AS commodity_consolidated,

# Also duplicated island group mapping from int_prices_normalised.sql
CASE
    WHEN mk.admin1 IN ('DKI JAKARTA', 'JAWA BARAT', ...) THEN 'Java'
    ...
END AS island_group,
```

This creates a maintenance liability: if the dbt pipeline updates the consolidation or mapping logic, the notebook silently diverges — no error, just wrong analysis.

### Solution

Replace inline pipeline logic with a direct query against `wfp_intermediate.int_prices_normalised`:

```python
df_target = conn.sql("""
    SELECT date, price_idr AS price, price_usd AS usdprice,
           commodity_consolidated, admin1, island_group, price_flag
    FROM wfp_intermediate.int_prices_normalised
    WHERE NOT filter_out
      AND price_flag = 'actual'
      AND commodity_consolidated IS NOT NULL
""").df()
```

### Files Affected

- `analysis/eda.py` — Cell 2 replaced 40 lines of inline CASE logic with a single SQL query

### Rule

Any ETL/EDA notebook that duplicates pipeline logic (mapping tables, CASE statements, join logic) creates a drift risk. Query the dbt mart or intermediate model directly. The notebook should be a consumer of the pipeline, not a second implementation.

---

## 58. `mo.persistent_cache` + Named Cells for Marimo Notebook Quality

### The Problem

The EDA notebook's data loading cell re-executed the DuckDB query every time the kernel restarted — even when the underlying data hadn't changed. All 20 cells were named `def __()` making the reactive graph opaque.

### Solution

**Data caching with `@mo.persistent_cache` + context-managed connections:**
```python
@app.cell
def data_load(mo, duckdb, pd):
    @mo.persistent_cache
    def _query_prices():
        with duckdb.connect("data/wfp.duckdb") as _c:
            _df = _c.sql("""...""").df()
        return _df

    df_target = _query_prices()
    ...
    return df_target, run_id, target   # conn NOT returned — each cell manages its own
```

Every cell that needs DuckDB data wraps its query in `@mo.persistent_cache` with a `with duckdb.connect(...) as _c:` context manager — ensuring connections are always closed. The `conn` object is never passed between cells, avoiding stale or leaked connections.

The cache persists to disk — survives kernel restarts. On the first run it executes the function and caches the result; subsequent runs read from disk. To bust the cache, delete the `__marimo_cache__` directory or rename the function.

**Named cells:**
```python
@app.cell
def setup(): ...          # Imports + constants

@app.cell
def data_load(): ...       # DuckDB + data loading

@app.cell
def filtered_data(): ...   # Applies user filters

@app.cell
def trend_charts(): ...    # Chart rendering

@app.cell
def summary(): ...         # Findings table
```

### Files Affected

- `analysis/eda.py` — Added `@mo.persistent_cache` decorator, renamed all 20 `__()` cells to descriptive names

### Rule

Use `@mo.persistent_cache` for any cell that loads data or computes expensive intermediate results. Name all cells descriptively — `def __()` is the marimo equivalent of `x = 1` instead of `total_revenue = 1`. The function name appears in the cell header and makes the dataflow graph navigable.

---

## 59. Interactive Filters in Marimo Turn Static EDA Into Self-Service

### The Problem

The original EDA notebook was fully static — every chart rendered all data. Stakeholders couldn't filter by commodity, island group, or year range without editing code.

### Solution

Added three interactive widgets and a reactive `filtered_df` cell:

```python
@app.cell
def filters(df_target, mo, target):
    commodity_dd = mo.ui.dropdown(
        options=["All"] + target,
        value="All", label="Commodity",
    )
    island_dd = mo.ui.dropdown(
        options=["All", "Java", "Sumatera", "Kalimantan", "Sulawesi", "Eastern Indonesia"],
        value="All", label="Island Group",
    )
    year_slider = mo.ui.range_slider(
        start=2007, stop=2024, step=1,
        value=(2007, 2024), label="Year Range",
    )
    mo.hstack([commodity_dd, island_dd, year_slider], justify="start")
    return commodity_dd, island_dd, year_slider

@app.cell
def filtered_data(df_target, commodity_dd, island_dd, year_slider):
    filtered_df = df_target.copy()
    if commodity_dd.value != "All":
        filtered_df = filtered_df[filtered_df["commodity_consolidated"] == commodity_dd.value]
    if island_dd.value != "All":
        filtered_df = filtered_df[filtered_df["island_group"] == island_dd.value]
    filtered_df = filtered_df[
        (filtered_df["year"] >= year_slider.value[0]) &
        (filtered_df["year"] <= year_slider.value[1])
    ]
    return (filtered_df,)
```

Charts in the **A (Aggregates)** section consume `filtered_df` instead of `df_target`. Deep-dives (N1–N4) stay on `df_target` to show full context.

### Files Affected

- `analysis/eda.py` — Added 2 new cells (`filters`, `filtered_data`), updated 6 chart cells to use `filtered_df`

### Rule

Static EDA notebooks become self-service analysis tools with 3 lines of `mo.ui.dropdown` and one `filtered_df` cell. Not every chart needs filtering — deep-dives benefit from full context — but trend charts, volatility, and seasonality gain immediate value from commodity/date scoping. Mark the filter scope explicitly so users know which charts respond.

---

## 60. Data Source Migration Must Audit All Downstream Filter Conditions

### The Problem

When refactoring the EDA notebook to query `int_prices_normalised` instead of staging views, the query included `AND island_group IS NOT NULL` — which seemed like a safe quality filter:

```python
WHERE NOT filter_out
  AND price_flag = 'actual'
  AND commodity_consolidated IS NOT NULL
  AND island_group IS NOT NULL   -- added
```

This silently dropped all Rice, Sugar, and Flour data because their `actual` price records are national averages (market_id=974, admin1='NATIONAL'), which doesn't match any island group mapping:

```
Cooking Oil island groups: Eastern Indonesia, Java, Kalimantan, Sulawesi, Sumatera, None
Rice island groups:        None
Sugar island groups:       None
Flour island groups:       None
```

The original staging-view query didn't have this filter — it never filtered by island_group. The migration introduced a behavioral change that dropped 474 of 2,116 rows (22%).

### Solution

Removed `AND island_group IS NOT NULL` from the base query. The coverage island display adds its own `dropna(subset=["island_group"])` to keep the table clean.

### Files Affected

- `analysis/eda.py` — Removed `AND island_group IS NOT NULL` from data load query

### Rule

Every filter condition in a migrated query is a behavioral change, not just a quality guard. Compare the row-level results before and after: `COUNT(*)` by commodity, island_group, and price_flag catches silent drops. A condition that seems safe in isolation (`island_group IS NOT NULL`) can filter out legitimate data when the source includes national averages.

---

## 61. Historical Shock Analysis May Need Unfiltered Aggregate Data

### The Problem

The Cooking Oil 2022 price shock is the most notable event in the dataset — but it's invisible in `int_prices_normalised` with `price_flag = 'actual'`:

| Year | price_flag   | Count |
|------|-------------|-------|
| 2020 | actual       | 3     |
| 2021 | aggregate    | 7,308 |
| 2022 | aggregate    | 7,292 |
| 2023 | aggregate    | 7,205 |
| 2024 | actual       | 1,484 |

The WFP dataset has no market-level `actual` prices for 2021–2023 Cooking Oil — only `aggregate` (national averages). The pipeline's quality guard (`NOT filter_out`) excludes aggregate data. The EDA notebook's N1 cell performed a shock analysis with no data.

### Solution

Changed the N1 analysis to query `int_commodity_consolidated` directly with only a `price > 0` filter — bypassing the aggregate exclusion:

```python
_oil_raw = conn.sql("""
    SELECT date, price, EXTRACT(YEAR FROM date) AS year, EXTRACT(MONTH FROM date) AS month
    FROM wfp_intermediate.int_commodity_consolidated
    WHERE commodity_consolidated = 'Cooking Oil' AND price > 0
""").df()
```

The 2022 shock is now visible: pre-shock (Mar) IDR 19,946 → peak (Apr) IDR 23,105 — a 13% month-over-month spike.

### Files Affected

- `analysis/eda.py` — N1 cell (`cooking_oil_shock`) switched from `df_target` to direct `int_commodity_consolidated` query

### Rule

Data quality filters that serve 95% of analysis may hide the 5% of notable events. When a deep-dive analyzes a specific historical event, check whether the event's data exists under the standard quality filters. If the event data is only available in a "raw" or "unfiltered" source, it's acceptable to bypass quality filters for that specific analysis — but document the decision and note that the numbers include aggregate or unvalidated data.

---

## 62. PEP 723 Headers Enable Script Portability for Marimo Notebooks

### The Problem

All 3 marimo notebooks (`data_validation.py`, `eda.py`, `forecast_experimentation.py`) lacked PEP 723 `# /// script` headers. When running via `uv run analysis/eda.py`, uv had no way to resolve dependencies automatically — users had to `uv sync` the project first or install deps manually. The files only had a `marimo-version` block.

### Solution

Added PEP 723 headers declaring `requires-python` and `dependencies` to all 3 notebooks:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb",
#     "pandas",
#     "numpy",
#     "plotly",
#     "statsforecast",  # forecast_experimentation.py only
# ]
# ///
# /// marimo-version
# /// version = 0.23.7
# ///
```

The `marimo-version` block must come after the PEP 723 header to avoid parse ambiguity.

### Files Affected

- `analysis/data_validation.py` — added PEP 723 header
- `analysis/eda.py` — added PEP 723 header
- `analysis/forecast_experimentation.py` — added PEP 723 header

### Rule

Every marimo notebook must begin with a PEP 723 script block declaring its dependencies, even if the project-level `pyproject.toml` covers them. This makes notebooks portable — they can be run with `uv run <file.py>` from any directory.

---

## 63. Script Mode Detection Enables Headless Marimo Execution

### The Problem

All 3 notebooks assumed interactive browser mode. Running `uv run analysis/eda.py` in a CLI would attempt to render interactive widgets, which may fail or produce confusing output. There was no `mo.app_meta().mode == "script"` guard to switch data sources or skip interactive widget waits in headless mode.

### Solution

Added an `is_script_mode` cell to each notebook:

```python
@app.cell
def script_mode(mo):
    is_script_mode = mo.app_meta().mode == "script"
    return (is_script_mode,)
```

This variable is now available to downstream cells. In script mode:
- Auto-run with widget defaults instead of waiting for user interaction
- Use synthetic data or precomputed results when appropriate
- Always show widgets (per marimo skill guidance) — only change data behavior

### Files Affected

- `analysis/data_validation.py` — added `script_mode` cell
- `analysis/eda.py` — added `is_script_mode` return to `setup()` cell
- `analysis/forecast_experimentation.py` — added `script_mode` cell

### Rule

Every marimo notebook that can run headlessly must include a `mo.app_meta().mode == "script"` check. Always create and display all UI elements; only change the data source or auto-run behavior in script mode. Never wrap entire cells in `if is_script_mode:` guards.

---

## 64. Split Monolithic Cells by Logical Concern

### The Problem

`forecast_experimentation.py` had a single cell (original lines 100–178) performing 5 distinct operations in sequence:

1. Islamic calendar loading and feature engineering
2. Train/test split
3. Model instantiation and fitting
4. Holdout evaluation and best-model selection
5. Final forecast with exogenous regressors

This ~80-line cell was hard to read, debug, and reuse. The DAG showed a single opaque dependency rather than distinct transformation steps.

### Solution

Split the monolithic cell into 3 named cells:

- **`train_setup()`** — loads Islamic calendar, prepares `train_df` with regressor flags
- **`holdout_evaluation()`** — splits train/test, fits candidate models, computes MAE, selects best model
- **`final_forecast()`** — refits best model on full data, generates forecast with 95% CI

Each cell has a single responsibility, clear inputs/outputs, and a descriptive name visible in the marimo DAG.

### Files Affected

- `analysis/forecast_experimentation.py` — one cell split into three

### Rule

Each marimo cell should represent one logical transformation. If a cell exceeds 30–40 lines or performs 3+ distinct steps (e.g., load + transform + fit + evaluate), split it. Use descriptive function names that explain what the cell does. The DAG should read like a pipeline manifest, not a code dump.

---

## 65. `mo.stop()` Prevents Raw Tracebacks in Error States

### The Problem

In `eda.py`, if the DuckDB connection fails or the query returns zero rows (e.g., pipeline hasn't been run), the notebook would throw raw Python tracebacks. There was no graceful error handling — users would see unhelpful `IndexError` or `AttributeError` messages instead of a friendly explanation.

### Solution

Added `mo.stop()` with a contextual message after the query result:

```python
@app.cell
def data_load(mo, duckdb, pd, np):
    @mo.persistent_cache
    def _query_prices():
        ...
    df_target = _query_prices()
    mo.stop(len(df_target) == 0, mo.md("⚠ **No data returned** — check DuckDB path and pipeline status."))
    ...
```

`mo.stop()` halts cell execution and displays the provided message instead of continuing into downstream cells that would fail on empty data.

### Files Affected

- `analysis/eda.py` — added `mo.stop()` after `_query_prices()` in `data_load` cell

### Rule

Use `mo.stop()` at the top of cells that perform external I/O (DB queries, file reads, API calls) when the result could be empty or the operation could fail. Provide a user-friendly markdown message explaining what's wrong. Do not wrap cell bodies in `try/except` for normal control flow — let errors surface naturally for unexpected failures.

---

## 66. `mo.lazy()` Defers Expensive Computations Until Needed

### The Problem

The `reconciliation` cell in `eda.py` queries all tables across 3 dbt schemas, reads 5 JSON files, and builds multiple comparison tables — all eagerly when the notebook loads. On a cold start or slow disk, this adds unnecessary latency to the initial notebook render, even though the reconciliation data is only needed when the user scrolls to the bottom of the notebook.

### Solution

Restructured the cell to use **return-based rendering** — the entire output is built inside a `_build()` function and returned as `mo.lazy(_build)`:

```python
@app.cell
def reconciliation(mo, pd, json, os, duckdb):
    def _build():
        # Queries + file reads happen inside this function
        ...
        return mo.vstack([
            mo.md("..."),
            mo.ui.table(...),
            mo.md("..."),
            mo.ui.table(...),
        ])

    return mo.lazy(_build)
```

Key design choices:
- **`@mo.persistent_cache`** wraps the DuckDB mart queries inside `_build()` — the cache survives kernel restarts
- **`FileNotFoundError` guard** on `os.listdir()` — if `dashboard/public/data/` doesn't exist, returns empty list instead of crashing
- All content is returned as a single `mo.vstack(...)` expression, making the cell deferrable

### Lesson

`mo.lazy()` only defers content that is the **final return value** of a cell. It cannot defer cells that render via side-effect calls (e.g., `mo.md()` as a statement, not a return expression). For those cells, restructure to return all content as a single expression.

### Files Affected

- `analysis/eda.py` — `reconciliation()` cell restructured to return-based `return mo.lazy(_build)` with cached mart queries + `FileNotFoundError` guard

### Rule

For cells with expensive computations that are only needed when visible, structure them as a single return expression wrapped in `mo.lazy(...)`. Always guard file I/O with try/except to prevent hard failures on missing data directories.

---

## 67. Merge-Delete File Sweep - Notebook Content Merge Requires Full Doc Sweep

### The Problem

Phase 5 Deep Dive was merged into `analysis/eda.py` (from the planned `analysis/deep_dive.py`). Post-merge, **3 separate docs** still referenced the non-existent file:

| Doc | Stale References |
|-----|-----------------|
| `AGENTS.md` | Project structure listing (L144) + Phase pipeline description (L90) |
| `docs/wfp-food-price-intelligence-project-plan.md` | Project structure (L147), workflow instructions ×3 (L437, L500, L505) |
| `docs/model_methodology.md` | Inline text reference (L186) |

The notebook's own `summary` cell also still referenced "DD §8/§9/§11/§12" as source sections — but those sections never existed; the deep dive cells use Q1–Q4 naming.

### Root Cause

When the deep dive cells were appended to `eda.py`, the merge was treated as a **code-only** operation. No systematic sweep was done of:
- Project structure diagrams listing `deep_dive.py`
- Phase pipeline descriptions naming the file
- Cross-references in methodology docs
- Internal summary tables referencing non-existent section labels

### Solution

Run a **doc sweep checklist** whenever a planned file is merged, renamed, or deleted:

1. **Search project structure diagrams** — AGENTS.md, project-plan.md, README.md
2. **Search inline file references** — `analysis/deep_dive.py` → grep across `docs/` and `*.md`
3. **Search internal cross-references** — summary tables, cell comments, section anchors
4. **Update phase pipeline descriptions** — if the deliverable path changed

### Files Affected (this fix)

- `AGENTS.md` — project structure + phase pipeline updated
- `docs/wfp-food-price-intelligence-project-plan.md` — structure + 3 workflow refs updated
- `docs/model_methodology.md` — inline path + added North Star method mention
- `analysis/eda.py` — summary "DD §" references replaced with Q1.1/Q4.3/Q1.3/Q3.2

### Related

- LEARNINGS.md §60 — Data source migration must audit all downstream filter conditions (same pattern: change one thing, update all references)

### Rule

When a **planned file is merged, renamed, or deleted**, do not stop at the code merge. Sweep all documentation for references to the old path — project structure diagrams, phase pipelines, methodology docs, workflow instructions, and internal cross-reference tables. One grep pass across `*.md` catches most stale references.

---

## 68. Don't Parse Values Out of Formatted Strings — Keep Structured Data

### The Problem

The `correlation` and `q4_cross_correlation` cells in `eda.py` built display strings like `"Rice ↔ Flour: r = 0.773"` and then parsed the `r` value back out to find the strongest/weakest pair:

```python
# BAD: build display strings, then parse them
_pairs_list = [f"{a} ↔ {b}: r = {r:.3f}" for ...]
_weakest = min(_pairs_list, key=lambda x: abs(float(x.split("r = ")[1])))
```

This pattern has three problems:
1. **Fragile** — changing the display format (e.g., `r = ` to `ρ = `) silently breaks the parsing logic
2. **Confusing** — the reader has to understand both the format and the parse direction
3. **Unnecessary computation** — building strings only to split them again wastes cycles

### Solution

Keep display strings and computation data separate:

```python
# GOOD: tuples for computation, display strings for rendering
_pairs = []
_pairs_display = []
for _i in range(len(corr.columns)):
    for _j in range(_i + 1, len(corr.columns)):
        _r = corr.iloc[_i, _j]
        _name = f"{corr.columns[_i]} ↔ {corr.columns[_j]}"
        _pairs.append((_name, _r))                       # structured data
        _pairs_display.append(f"{_name}: r = {_r:.3f}") # display only

_weakest = min(_pairs, key=lambda x: abs(x[1]))  # tuple access, no parsing
_strongest = max(_pairs, key=lambda x: abs(x[1]))
```

### Files Affected

- `analysis/eda.py` — `correlation` and `q4_cross_correlation` cells restructured to use tuples

### Rule

Never parse values out of strings you just built. Keep a structured representation (tuple, dict, DataFrame) for computation and build display strings only when needed for rendering. The added indirection of maintaining dual representations is worth the clarity gain.

## 69. Marimo Module-Level `__` Variables Are Filtered From Cell Namespaces

### The Problem

The AGENTS.md convention states: *"Use `__` (double underscore) prefix for variables that must not appear in Marimo's reactive graph"*. Based on this, the three notebooks defined the DuckDB path at module level:

```python
# analysis/eda.py, data_validation.py, forecast_experimentation.py
__db_path = str(Path(__file__).resolve().parent.parent / "data" / "wfp.duckdb")
```

But cells could not access `__db_path`, raising `NameError`:

```
NameError: name '__db_path' is not defined
```

### Root Cause

Marimo's `__` name filtering works at **all scope levels**, not just within cells. Variables with `__` prefix defined at **module level** are excluded from cell execution namespaces just like variables defined inside cells. The `exec()` call that runs each cell uses a filtered namespace that strips `__`-prefixed names — even those present in the module's `__dict__`.

This differs from Python's normal name-mangling behavior (which only affects class bodies, not module-level code).

### Solution

Compute the DB path inside the `setup()` cell and return it through Marimo's reactive DAG:

```python
@app.cell
def setup():
    from pathlib import Path
    PROJECT_DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "wfp.duckdb")
    return (PROJECT_DB_PATH, ..., ...)

@app.cell
def data_load(mo, duckdb, pd, PROJECT_DB_PATH):
    with duckdb.connect(PROJECT_DB_PATH) as _c:
        ...
```

Key points:
- Use a regular name (no `__` prefix) for return values — they enter the cell graph
- `Path(__file__)` still resolves correctly inside setup cells (marimo preserves `__file__`)
- Downstream cells list `PROJECT_DB_PATH` as a function parameter — marimo wires it automatically

### Files Affected

- `analysis/eda.py` — 9 occurrences of `__db_path` → `PROJECT_DB_PATH`
- `analysis/data_validation.py` — 1 occurrence
- `analysis/forecast_experimentation.py` — 1 occurrence

All instances replaced the module-level `__db_path` with a `setup()` cell return.

### Rule

Do not use `__`-prefixed variables at module level in Marimo notebooks — they are filtered from cell execution namespaces. Compute shared values (DB paths, configs) inside the `setup()` cell and return them through the reactive DAG. See also AGENTS.md §385 (Marimo Notebook conventions) for the `__` underscore convention.

## 70. `pyproject.toml` Dependencies Must Cover Notebook Imports

### The Problem

`analysis/eda.py` imports from `scipy` and `numpy`, but `pyproject.toml` only listed `marimo`, `duckdb`, `dbt-duckdb`, `statsforecast`, `pandas`, and `plotly`:

```python
# eda.py setup cell
from scipy import stats as scipy_stats   # ✅ works at runtime (transitive dep)
import numpy as np                       # ✅ works at runtime (transitive dep)
```

`uv sync` succeeded because `statsforecast` pulls in `numpy` and `scipy` transitively. But:
1. **Explicit is better than implicit** — a future version of statsforecast might drop these deps
2. **`uv sync --no-dev` or locked environments** might prune transitive deps
3. **`uvx marimo check`** reports missing imports that aren't declared

### Solution

Declare all direct imports in `pyproject.toml` under `[project] dependencies`, even if they're transitively available:

```toml
dependencies = [
    "marimo",
    "duckdb>=1.0.0",
    "dbt-duckdb>=1.9.0",
    "statsforecast>=1.7.0",
    "pandas>=2.2.0",
    "plotly>=5.24.0",
    "numpy>=1.26.0",
    "scipy>=1.11.0",
]
```

### Files Affected

- `pyproject.toml` — added `numpy>=1.26.0` and `scipy>=1.11.0`

### Rule

After adding a new import to any notebook or script, verify it's declared in `pyproject.toml`. Transitive dependencies are not guaranteed across version upgrades. Run `uvx marimo check <notebook.py>` to catch missing declarations.

---

## 71. Ramadan Cross-Year JOIN: `BOOL_OR()` with Multi-Year Matching

### The Problem

`mart_seasonal_patterns.sql` computed Ramadan proximity flags using a single-year join:

```sql
LEFT JOIN wfp_intermediate.int_islamic_calendar c
    ON EXTRACT(YEAR FROM m.month) = c.year
```

This missed the `t_plus_1` flag for Eids in December. When Eid fell in December 2024, `t_plus_1` (January 2025) had `m.month.year = 2025` but `c.year = 2024` — the join missed, so no January row got flagged as post-Ramadan.

**Root Cause:** The `t_plus_1` expression `m.month = c.eid_date + INTERVAL '1 month'` was correct SQL, but the single-year join guard `EXTRACT(YEAR FROM m.month) = c.year` excluded cross-year matches before the flag expression could evaluate.

### Solution

Use `IN` with both the current and next year, then aggregate with `BOOL_OR()` to avoid double-counting:

```sql
LEFT JOIN wfp_intermediate.int_islamic_calendar c
    ON EXTRACT(YEAR FROM m.month) IN (c.year, c.year + 1)
    AND m.month IN (c.eid_month, c.t_minus_1, c.t_minus_2, c.t_minus_3, c.t_plus_1)

SELECT MAX(
    CASE WHEN m.month = c.eid_month THEN 1 ELSE 0 END
) AS flag_ramadan_eid_month,
...

GROUP BY m.month, m.commodity_consolidated, ...
```

**Key insight:** `EXTRACT(YEAR FROM m.month) = c.year` is not just a join condition — it's a **filter that silently excludes edge cases**. Any reference-date-based join (T-3 to T+1, fiscal year offsets) risks boundary exclusion. Always test edge cases: what happens when Eid is in January? December? What about the year before the calendar starts?

### Files Affected
- `transform/models/marts/mart_seasonal_patterns.sql` — ramadan CTE join changed from single-year to `IN (c.year, c.year + 1)` with `BOOL_OR()` aggregation

---

## 72. Hardcoded Reference Dates: Compute from Data, Not Calendar

### The Problem

`forecast/run_forecast.py` had two instances of a hardcoded future date:

```python
future_exog_df = get_future_exog("2024-06-01", 6)  # Hardcoded!
```

And in the post-2022 robustness check:
```python
future_exog_oil = get_future_exog("2024-06-01", 6)  # Same hardcoded value
```

These dates were correct at time of writing but would become stale as soon as the pipeline ran against newer data. Any re-run after May 2024 would produce forecasts starting from an incorrect point.

### Solution

Compute `forecast_start` from each commodity's own latest data point:

```python
forecast_start = hist_id["ds"].max() + pd.DateOffset(months=1)
future_exog_df = get_future_exog(forecast_start, 6)
```

**Why per-commodity:** Different commodities have different data end dates (Flour ends 2020-03, Rice ends 2024-05). A single hardcoded date would be wrong for all but one.

### Files Affected
- `forecast/run_forecast.py` — `fit_and_forecast()` and `fit_cooking_oil_post2022()` both replaced `"2024-06-01"` with computed `forecast_start`

---

## 73. Unified Pipeline `run_id` Across Subprocesses

### The Problem

The pipeline orchestrator (`run_pipeline.py`) generated a `run_id` and passed it to ingest, but **forecast and export generated their own independent IDs** via `generate_run_id()`:

```
Pipeline lineage:   pipeline_20260526_051924  (from orchestrator, $export_status = pending)
Forecast lineage:   pipeline_20260526_052000  (separate ID, not linked to pipeline)
Export lineage:     pipeline_20260526_052010  (separate ID, not linked to pipeline)
```

This made it impossible to ask "did this pipeline run succeed end-to-end?" — each phase had a different row.

### Solution

Pass `run_id` as a CLI argument from the orchestrator:

```python
# run_pipeline.py
subprocess.run(["uv", "run", "python", "forecast/run_forecast.py", run_id])
subprocess.run(["uv", "run", "python", "export/export_json.py", run_id])
```

Both scripts accept the first CLI arg as `run_id` and fall back to auto-generation if absent (backward-compatible):

```python
import sys
run_id = sys.argv[1] if len(sys.argv) > 1 else generate_run_id()
```

**Result:** All phases now share a single `run_id` — a single row in `pipeline.lineage` shows `ingest=completed, transform=completed, forecast=completed, export=completed`.

### Files Affected
- `run_pipeline.py` — passes `run_id` as arg to forecast and export subprocesses
- `forecast/run_forecast.py` — reads `sys.argv[1]` with fallback
- `export/export_json.py` — reads `sys.argv[1]` with fallback

---

## 74. DRY: Importable Pipeline Helpers Over Duplicated DDL

### The Problem

Both `forecast/run_forecast.py` and `export/export_json.py` contained identical inline code for creating the lineage table:

```python
# forecast/run_forecast.py (59 lines)
conn.execute("CREATE SCHEMA IF NOT EXISTS pipeline;")
conn.execute("""
    CREATE TABLE IF NOT EXISTS pipeline.lineage (
        run_id TEXT PRIMARY KEY,
        ...
    )
""")

# export/export_json.py (same 59 lines, verbatim copy)
conn.execute("CREATE SCHEMA IF NOT EXISTS pipeline;")
conn.execute(""" ... """)
```

This violated DRY — any schema change to the lineage table required editing 3 files (config.py + forecast + export), and updates were missed during Phase 3e.

### Solution

Export `ensure_lineage_table()` from `ingest/config.py` and call it from both scripts:

```python
# ingest/config.py
def ensure_lineage_table(conn):
    conn.execute("CREATE SCHEMA IF NOT EXISTS pipeline;")
    conn.execute("""CREATE TABLE IF NOT EXISTS pipeline.lineage (...)""")

# forecast/run_forecast.py & export/export_json.py
from ingest.config import ensure_lineage_table
ensure_lineage_table(conn)  # Single call replaces 59 lines
```

**Result:** Schema changes happen in one place. Both scripts are 59 lines shorter. No copy-paste drift risk.

### Files Affected
- `ingest/config.py` — extracted `ensure_lineage_table()` from inline initialization
- `forecast/run_forecast.py` — replaced inline DDL with import + call
- `export/export_json.py` — replaced inline DDL with import + call

---

## 75. Cloudflare Pages Constraint Hard-Blocks All Python Server Frameworks

> **SUPERSEDED 2026-06-02** — The deployment target moved from Cloudflare Pages to Hugging Face Spaces. HF Spaces is a free Python/Docker host that natively runs Dash/Flask servers. Vizro, Dash, Streamlit, Gradio, and Reflex are all viable. The framework-evaluation framework (deployment-as-load-bearing-constraint) is still correct; the specific disqualification of Cloudflare Pages is no longer the binding constraint. See `docs/implementation-plan.md` §6.STACK for the new decision.

### The Problem

When evaluating Vizro (McKinsey's low-code Python dashboard toolkit) as a replacement for the planned Next.js stack, the initial framing was "low-code velocity vs. full-code control." The actual binding constraint turned out to be the **deployment target**: Cloudflare Pages is a static-site host. Vizro is a Dash server. The two are not directly compatible.

### Investigation

Surveyed the "high maturity + low code" Python dashboard landscape:

| Framework | Stars | Backing | Deployment | Cloudflare Pages fit |
|-----------|------:|---------|-----------|---------------------|
| Streamlit | 44.7k | Snowflake | Streamlit Community Cloud, Render, Fly.io | None (server only) |
| Dash 3/4 | 24.2k | Plotly | gunicorn + Render/Fly.io, Dash Enterprise | None (Flask server) |
| Panel | 5.6k | Anaconda / HoloViz | Tornado/Flask, **Pyodide static export** | **Only Python option that can** (Pyodide, ~1MB initial payload) |
| Gradio | 42.7k | Hugging Face | HF Spaces, Docker | None (server only) |
| Vizro | 3.7k | McKinsey | Dash server, Render, Fly.io | None (server only) |
| Reflex | ~21k | Pynecone | FastAPI server | None (server only) |

**Cloudflare Workers** does support Python via Pyodide, but does not support Flask/Dash WSGI apps. Running a Dash or Streamlit app on Cloudflare Pages requires either (a) swapping the host to Render/Fly/HF Spaces, or (b) a Workers-specific rewrite that drops the framework entirely.

### Why This Matters More Than It Looks

The "trade framework for low code" framing assumed deployment was a separate concern from framework choice. It is not. **The deployment target is a load-bearing constraint** — forking the framework choice before considering hosting produces dead-on-arrival evaluations. For every Python option except Panel, switching frameworks forces a hosting migration as a side effect. The 5-JSON static export already in `dashboard/public/data/` is purpose-built for Cloudflare Pages; replacing the framework that consumes it without a hosting plan leaves a half-built deliverable.

### Solution

1. Make the deployment target the **first filter** in any framework evaluation. State it explicitly: "Cloudflare Pages static" / "Render server" / "HF Spaces free tier" / etc.
2. Cross-reference against the framework's deployment story before reading any "low code" marketing.
3. Score frameworks against deployment fit at the **highest weight** in the decision matrix (12/100 in this project's matrix). A framework that doesn't deploy to the target is disqualified.

### Rule

When evaluating a framework, ask "how does it deploy to my target host?" first. If the answer is "it doesn't, you have to change the host too," the framework is a much worse fit than its feature set suggests. The hosting cost — both the migration and the recurring ops — is rarely captured in framework comparison charts.

---

## 76. Weighted Decision Matrix Prevents Vibes-Based Stack Choices

### The Problem

Comparing "Vizro vs. Next.js" is a structural mismatch — different runtimes, different deployment models, different LOC profiles, different community sizes. Without an explicit scoring method, the comparison collapses to "Vizro is low-code" vs. "Next.js is more familiar" — both of which are vibes, not decisions. The same trap applies to any framework choice: Streamlit vs. Dash, PostgreSQL vs. DuckDB, dbt vs. SQLMesh.

### Solution

A weighted decision matrix forces explicit values onto what would otherwise be implicit preferences:

| Step | Action |
|------|--------|
| 1 | List 12–15 evaluation criteria specific to **this** project (not generic) |
| 2 | Assign weights that sum to 100, calibrated to the project's actual stakes |
| 3 | Score each option 1–10 against each criterion |
| 4 | Multiply, sum, normalize |
| 5 | The lowest-scored option is not automatically wrong — but any decision to override the score requires articulating which weight is miscalibrated |

Example weights used for the dashboard stack evaluation:

| Criterion | Weight | Why this weight |
|-----------|-------:|-----------------|
| Pipeline artifact reuse (5 JSONs already exported) | 12 | Switching costs the entire data layer |
| Deployment fit (Cloudflare Pages) | 12 | Hard-block on every Python server option |
| LOC / build effort for 4 pages | 10 | This is the headline trade-off |
| Filter behavior correctness | 10 | 35+ LEARNINGS.md sections cover this for current stack |
| Time-series viz quality | 8 | Forecast CI overlay is the analytical centerpiece |
| Hiring / portfolio signal | 8 | Reviewers recognize Next.js, not Vizro |

### Key Insight

The matrix does not produce truth — it produces **defensible preferences**. When the score says "Next.js wins 8.02 vs. 6.75," the decision to keep the current plan is justified by the 12-weight on deployment fit and 12-weight on pipeline reuse, not by "feels more familiar." If a future re-evaluation wants to switch to Vizro, the burden is to argue that deployment fit or pipeline reuse should be weighted lower — not to assert that Vizro is "better."

### Files Affected

- `docs/LEARNINGS.md` — §75 (this section), and 4 follow-on sections documenting the matrix outcomes

### Rule

For any framework or tool choice with 3+ viable candidates, build a weighted matrix before committing. The discipline matters more than the specific numbers — the act of writing down weights forces articulation of what the project actually values. A 6-line matrix that gets the weights right beats a 50-page comparison that doesn't.

---

## 77. Framework Maturity Is a Hidden Tax, Not Just a Number

### The Problem

GitHub stars and version numbers are visible metrics, but they don't fully capture the **hidden cost of choosing an immature framework**. When Vizro was first proposed as an alternative, the "low code" pitch was front and center. The maturity comparison was an afterthought — and a telling one: Vizro (3.7k stars, v0.1.56, 3 years old) is the **least mature option** on any reasonable Python dashboard list.

### What "Maturity" Actually Means

| Dimension | Measurement | Vizro | Streamlit | Dash 3/4 | Next.js |
|-----------|-------------|------:|----------:|---------:|--------:|
| Stars | GitHub | 3.7k | 44.7k | 24.2k | 130k+ |
| Age | First release | 2023 (3y) | 2019 (7y) | 2017 (9y) | 2016 (10y) |
| Version | Current | 0.1.x | 1.55.x | 4.x | 15.x |
| Corporate backing | Who pays the bills | McKinsey | Snowflake | Plotly | Vercel |
| Production users | Public references | Few | 90% F50 | Many | Most SaaS |

Version 0.1.x is the strongest signal: the project has not yet hit 1.0, which means breaking API changes are still expected. Documentation may have gaps. Edge cases may produce unhandled errors. Community answers on Stack Overflow are scarce. The "low code" velocity gain is paid for with a smaller corpus of solved problems.

### Why This Matters for Solo Portfolio Projects

A solo developer with no team to absorb surprise migration costs cannot easily absorb "Vizro 0.1 → 0.2 breaks your dashboard" or "this feature only works in Dash 2, not Dash 3." A mature framework has:

- **Documentation that matches current behavior** (Vizro's docs are still settling at 0.1.x)
- **Stack Overflow coverage** for the common errors (Vizro: ~50 questions; Streamlit: thousands)
- **Battle-tested callback patterns** (Dash has 9 years of them; Vizro's agent skills are 6 months old)
- **Predictable deprecation cycles** (Next.js 13 → 14 → 15 is a known cadence; Vizro 0.1 → 0.2 might break everything)

### Solution

When comparing frameworks, look beyond the marketing. Check:

1. **Version number** — 0.x is a yellow flag; 1.x or higher is preferred for production
2. **Release cadence** — monthly/biweekly is good; irregular or 6+ month gaps is bad
3. **Documentation completeness** — read 3 how-to pages; are the code examples current?
4. **Stack Overflow / GitHub Issues** — how many open vs. closed in the last 6 months?
5. **Corporate backing** — single-author or company-employed maintainers? Solo projects die.

### Rule

Star count and version number are the cheapest maturity proxy. Before committing to a "low-code" framework, verify it has hit 1.0 and has at least 2 years of stable releases. Otherwise, the time saved on initial development is spent on migration, debugging, and reinventing patterns that mature frameworks document out of the box.

---

## 78. Pipeline Reuse Beats LOC Savings — Don't Trade Built Data Layer for Faster Framework

### The Problem

The Phase 6 dashboard plan (Next.js) was designed against a specific data contract: 5 JSON files in `dashboard/public/data/` (one per mart model) + `forecast.json` (819 records). All five files are already produced by `export/export_json.py` with `verify_export()` row-count validation. Switching to Vizro, Streamlit, Dash, etc. would discard this data layer in favor of "the framework queries DuckDB directly."

The trade-off seemed favorable on its face: "we save 5 JSON files of static output and the framework fetches fresh data." But it conceals three real costs.

### Three Hidden Costs of "Fresh Data > Static JSON"

| Cost | Detail |
|------|--------|
| 1. **Export script becomes dead code** | `export_json.py`, `verify_export()`, the 5-JSON row-count reconciliation in `pipeline.lineage` — all bypassed |
| 2. **Data layer refactor** | Vizro/Dash/Streamlit need Python DataFrames from DuckDB. The mart models are the same, but the consumption path is rewritten |
| 3. **Reconciliation logic in Python** | `verify_export()` checks `mart_X rows == X.json records`. The equivalent for a Python-side dashboard is checking `len(df) == expected_count` per page, with the same logic moved to wherever the framework reads data |

Net result: the framework saves ~500 LOC of TSX/JSON UI code, but costs ~300 LOC of export + verification logic that's already battle-tested.

### Solution

Score "pipeline reuse" at the highest weight in any framework comparison. In this project's matrix it was 12/100 — only "deployment fit" was tied at the same weight. A framework that requires re-doing already-built data layers needs to save 2x+ in LOC to break even.

For a 4-page dashboard, 500 LOC of UI is one week of work. Rebuilding the data layer is two weeks minimum, and adds a new failure mode (framework's data fetcher breaks instead of `export_json.py`). The calculus almost never favors the switch.

### When "Fresh Data" Actually Wins

The case for a Python-server framework is real when:

- **Data updates multiple times per day** — static JSON is genuinely stale
- **Filter combinations aren't known in advance** — pre-aggregating every combination is infeasible
- **The user is internal/data-team** — they don't need a static URL, they need a live tool
- **Data volume makes export expensive** — gigabytes don't fit in a static JSON

For this project (17-year archive, 5 marts, 238 rows in `mart_price_trends`), none of these apply. The static JSON is the right contract.

### Rule

Before evaluating a new framework, list the artifacts already built that the current framework consumes. Score "reuse" at 10+ in the decision matrix. A framework that forces rebuilding finished work needs to save 2x in other dimensions to be worth considering.

---



## 81. Dash Pages Routing: `dash.register_page` + `use_pages=True`

> **SUPERSEDED 2026-06-02** — Dash was the chosen dashboard framework for ~1 day; replaced by Vizro. §81 pattern does not apply to Vizro (which uses `vm.Page` registration in `vm.Dashboard(pages=[...])`). Pattern preserved for git history + cross-reference. See §87 for Vizro equivalent.

### The Problem

Multi-page Dash apps historically required manual URL routing via `app.layout` callbacks and `dcc.Location` triggers. Each page needed explicit `Input("url", "pathname")` callbacks to conditionally render content. This produces verbose boilerplate and makes adding pages a multi-file operation.

### Solution: Dash Pages Plugin

Dash 3.x provides a built-in multi-page pattern via `use_pages=True`:

```python
# app.py
app = dash.Dash(__name__, use_pages=True, ...)
app.layout = dbc.Container([
    dbc.NavbarSimple(children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="/")),
        dbc.NavItem(dbc.NavLink("Page 2", href="/page2")),
    ]),
    dash.page_container,  # Auto-renders the matched page
])
```

Each page file self-registers:
```python
# pages/price_trends.py
dash.register_page(__name__, path="/", name="Price Trends")

def layout():
    return dbc.Container([...])
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `layout()` as function, not module-level | Allows dynamic layout per request; required for filter-dependent content |
| `suppress_callback_exceptions=True` | Pages load lazily — callbacks reference IDs not yet in DOM during initial load |
| One callback per page in the page module | Keeps callbacks co-located with the layout they update |
| `dash.page_container` in app.layout | Single insertion point — all page content renders inside this wrapper |

### Files Affected

- `dashboard/app.py` — `use_pages=True`, `page_container`
- `dashboard/pages/price_trends.py` — `register_page`, `layout()`, callbacks
- `dashboard/pages/seasonal_patterns.py` — same pattern
- `dashboard/pages/geographic_disparity.py` — same pattern
- `dashboard/pages/commodity_signals.py` — same pattern

### Rule

Use `dash.register_page(__name__, path=..., name=...)` at the top of each page file. Keep `layout()` as a function (not a variable). Place one callback per page in the same file. The app layout only needs `dash.page_container` — no manual URL routing.

---

## 82. DuckDB Read-Only Connections + `@functools.lru_cache` for Dashboard Data Access

> **SUPERSEDED 2026-06-02** — Dash was the chosen dashboard framework for ~1 day; replaced by Vizro. `@lru_cache` on `load_mart()` is framework-agnostic and **preserved** in `dashboard/data_access.py`; the Vizro equivalent wraps it via `data_manager.register_data()`. See §90 for Vizro-specific pattern.

### The Problem

Dash callbacks fire on every filter change. Without caching, each callback execution opens a new DuckDB connection, runs the query, and closes it. With 4 pages × 3 filters each, this produces dozens of short-lived connections per user session.

### Solution: Centralized Data Access with `lru_cache`

```python
# dashboard/data_access.py
import functools

@functools.lru_cache(maxsize=32)
def load_mart(name: str, **filters: str) -> pd.DataFrame:
    conn = duckdb.connect(DB_PATH, read_only=True)
    try:
        df = conn.execute(query, values).fetchdf()
    finally:
        conn.close()
    return df
```

Key design choices:

| Decision | Rationale |
|----------|-----------|
| `read_only=True` | Prevents accidental writes from dashboard; avoids DuckDB file locks between dashboard + pipeline |
| `@functools.lru_cache(maxsize=32)` | In-process cache — same query with same filters returns cached DataFrame; 32 entries covers all filter combos across 4 pages |
| `try/finally: conn.close()` | Guarantees connection cleanup even on query failure |
| Centralized module | Pages import `load_mart` — never open their own DuckDB connections |

### Cache Invalidation

`lru_cache` persists for the process lifetime. For dashboard use (read-only analytics), this is correct — data only changes when the pipeline re-runs. For development with live data changes, call `load_mart.cache_clear()` in a debug callback.

### Files Affected

- `dashboard/data_access.py` — `load_mart()`, `load_forecast_data()`, `load_forecast_metadata()`

### Rule

All DuckDB queries for the dashboard go through a single `data_access.py` module with `@functools.lru_cache`. Never open DuckDB connections directly in page callbacks. Use `read_only=True` to prevent accidental writes and file-lock conflicts with the pipeline.

---

## 83. `dcc.Store` for Cross-Page Filter State (Alternative: Query String)

> **SUPERSEDED 2026-06-02** — Dash was the chosen dashboard framework for ~1 day; replaced by Vizro. Vizro's `vm.Filter` is per-page by default; cross-page filter state requires URL `show_in_url=True` or custom action. See §89 for Vizro cross-page filter pattern.

### The Problem

Global filters (commodity, island group, year range) need to be shared across all 4 pages. When the user changes a filter on Page 1, navigating to Page 2 should reflect the same filter state.

### Two Approaches

| Approach | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| `dcc.Store` | Client-side JSON state in browser memory | Fast, no URL pollution | State lost on page reload; not shareable via URL |
| `dcc.Location` query string | Filters encoded in `?commodity=Rice&island=Java` | Shareable URLs, survives reload | More verbose callback wiring |

### Chosen: `dcc.Store` (per §6.6.6 plan)

```python
# components/filters.py
dcc.Store(id="filters-store")  # Shared state

# In callbacks, read from Store:
Input("global-commodity", "value"),
Input("global-island", "value"),
Input("global-year-range", "value"),
```

Since Dash Pages with `use_pages=True` shares the same layout, filter IDs are global — callbacks on any page can read `Input("global-commodity", "value")` directly without an intermediate Store. The Store becomes necessary only if filter state needs to persist across full page reloads.

### Files Affected

- `dashboard/components/filters.py` — filter bar with global IDs
- All 4 page callbacks — `Input("global-commodity", "value")` etc.

### Rule

For Dash Pages apps, prefer global filter IDs (same ID across all pages) over `dcc.Store` for filter state. The `dcc.Store` pattern is needed when state must survive page reloads or be shared between non-parent components. Always declare all callback `Output`/`Input` IDs in the signature — missing outputs raise `InvalidCallback` at startup.

---

## 84. HF Spaces Docker Packaging: Port 7860, `gunicorn`, Layer Optimization

> **PARTIALLY SUPERSEDED 2026-06-02** — Port 7860, layer ordering, and `--timeout 120` carry over to Vizro (same HF Spaces target). The gunicorn target changes from `app:server` (Dash exposes Flask server) to `app:app` (Vizro exposes its own Flask handle). See §91 for updated Dockerfile.

### The Problem

HF Spaces free tier expects a Dockerfile that exposes port 7860 (not 8050 or 5000). The Docker image must be lean enough to fit within free-tier memory limits (~2 GB). Cold starts must be fast (< 30s).

### Solution: Three-Layer Dockerfile

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

EXPOSE 7860
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120"]
```

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| Port 7860 | HF Spaces standard — changing it requires Space config changes |
| `gunicorn` with 2 workers | Free tier CPU limit; 2 workers handle concurrent requests without OOM |
| `--timeout 120` | Cold-start DuckDB connection + first query may take 15-30s |
| Layer order: deps → code → data | `pyproject.toml` changes rarely; data changes per pipeline run. Docker layer caching means only changed layers rebuild. |
| `--frozen --no-dev` | Reproducible installs; no dev tools (ruff) in production |

### Local vs Production

| Aspect | Local | HF Spaces |
|--------|-------|-----------|
| Port | 7860 (configured) | 7860 (HF default) |
| Server | Flask dev (1 worker) | gunicorn (2 workers) |
| Cold start | Instant | 15-30s (first request after sleep) |
| Hot reload | Auto (debug=True) | `hf spaces hot-reload` |

### Files Affected

- `dashboard/Dockerfile` — created per above spec
- `dashboard/.dockerignore` — excludes `.venv/`, `__pycache__/`, `analysis/`, `transform/`, `forecast/`, `logs/`, `docs/`, `.git/`, `data/raw/`
- `dashboard/README_HF.md` — HF Spaces metadata header (YAML)

### Rule

HF Spaces expects port 7860, gunicorn, and a Dockerfile at the Space root. Order Docker layers by change frequency: deps (rare) → code (medium) → data (frequent). Use `--timeout 120` for cold-start tolerance. Always test locally with `uv run python dashboard/app.py` before pushing.

---

## 85. Callback Output Declaration: All Outputs Must Be Declared in Signature

> **SUPERSEDED 2026-06-02** — Dash was the chosen dashboard framework for ~1 day; replaced by Vizro. Vizro does not use Dash callbacks; cross-component reactivity is handled via `vm.Filter` (data) and `vm.Parameter` (configuration) automatically. No explicit `@callback` decorator.

### The Problem

Dash 3.x raises `InvalidCallback` at startup if a callback's `Output` references an ID that isn't declared in the function signature. Unlike Dash 2.x (which silently ignored missing outputs), Dash 3.x enforces strict declaration:

```python
# BUG — Dash 3.x raises InvalidCallback
@callback(
    Output("chart-1", "figure"),
    Input("filter", "value"),
)
def update(filter_val):
    return fig  # Missing output for "chart-2"
```

### Solution

Declare all outputs in the `@callback` decorator, even if some are conditionally returned:

```python
@callback(
    Output("chart-1", "figure"),
    Output("chart-2", "figure"),
    Output("table-1", "children"),
    Input("filter", "value"),
)
def update(filter_val):
    if not data:
        empty = go.Figure()
        return empty, empty, []
    return fig1, fig2, table_children
```

### Key Difference from Dash 2.x

| Behavior | Dash 2.x | Dash 3.x |
|----------|----------|----------|
| Missing output in callback | Silently ignored | `InvalidCallback` at startup |
| `prevent_initial_call` | Optional | Required on heavy callbacks to avoid render-on-load |
| Multi-output return | Tuple/list | Must match `Output` count exactly |

### Files Affected

- All 4 page callbacks — all outputs declared in `@callback` decorator

### Rule

Dash 3.x requires all callback outputs to be declared in the `@callback` decorator. Every `Output()` must have a corresponding return value. Use `prevent_initial_call=True` on heavy callbacks (DuckDB queries + chart rendering) to avoid unnecessary initial renders. Return empty `go.Figure()` or `[]` for no-data states instead of `None`.

---

## 86. Plotly Figure Specs Port Verbatim from Marimo EDA to Dash `dcc.Graph`

> **PARTIALLY SUPERSEDED 2026-06-02** — Chart engine parity (Plotly everywhere) is preserved. The verbatim-port pattern carries over to Vizro's `custom_charts` registration: wrap `go.Figure()` builders as `@capture("graph")` functions and call them in `vm.Graph(figure=...)`. Same chart code, different registration ceremony. See §88.

### The Problem

The original plan (Next.js + Recharts) would have required translating every Plotly chart spec from `analysis/eda.py` into Recharts JSX components — different API, different event model, different tooltip configuration. For 15+ analytical charts with `add_vline`, `add_vrect`, `make_subplots`, CI shaded areas, and `px.imshow` heatmaps, the translation cost was estimated at 2-3 days.

### Solution: Plotly EDA → Dash Parity

With Dash using Plotly natively, chart specs drop into `dcc.Graph(figure=fig)` verbatim:

```python
# EDA notebook (analysis/eda.py)
fig = go.Figure()
fig.add_trace(go.Scatter(x=sub["month"], y=sub["avg_price_idr"], name=commodity))
fig.add_vline(x="2022-01-15", line_dash="dash", annotation_text="Cooking oil export ban")
fig.add_vrect(x0="2022-01-01", x1="2022-12-31", fillcolor="red", opacity=0.1)

# Dashboard page (pages/price_trends.py) — same code, zero translation
dcc.Graph(figure=fig)
```

### What Ports Verbatim

| EDA Feature | Dash Equivalent | LOC Saved |
|------------|-----------------|-----------|
| `go.Figure()` + `add_trace()` | Same | 0 (verbatim) |
| `add_vline(x=..., line_dash="dash")` | Same | ~5 per annotation |
| `add_vrect(fillcolor=..., opacity=...)` | Same | ~3 per band |
| `make_subplots(rows=2, cols=2)` | Same | ~10 |
| `px.imshow(matrix, color_continuous_scale=...)` | Same | ~8 |
| `go.Scatter(fill="toself")` for CI area | Same | ~15 per CI overlay |

### Files Affected

- `dashboard/pages/price_trends.py` — forecast CI overlay from EDA Q1
- `dashboard/pages/seasonal_patterns.py` — heatmap from EDA A3
- `dashboard/pages/commodity_signals.py` — correlation heatmap from EDA A5b

### Rule

When the EDA notebook and dashboard use the same chart library (Plotly), chart specs are copy-paste portable. The only adaptation needed is wrapping in `dcc.Graph(figure=fig)` and ensuring the figure is built inside a callback (not at module level). This parity is the single largest time-saver in the Phase 5g→6 transition.

---

## Updated Decision Log

| Decision | Rationale |
|----------|-----------|
| `BOOL_OR()` with multi-year `IN` join over single-year `=` | Single-year join for Ramadan proximity flags miss cross-year `t_plus_1` cases (Dec Eid → Jan next year). Multi-year `IN` + `BOOL_OR()` handles all boundary cases without double-counting. |
| Computed `forecast_start` over hardcoded `"2024-06-01"` | Per-commodity end dates differ (Flour: 2020-03, Rice: 2024-05). A single hardcoded date is wrong for all but one commodity. |
| CLI-passed `run_id` over per-script auto-generation | Forecast and export must share the pipeline's `run_id` for end-to-end auditability. Auto-generated IDs create orphan lineage rows with no parent pipeline link. |
| Importable `ensure_lineage_table()` over duplicated DDL | 59-line schema DDL duplicated in 2 scripts guaranteed drift on schema changes. A single importable function eliminates the copy-paste risk. |
| Deployment target as the first framework filter | Cloudflare Pages static hosting disqualifies every Python server framework (Vizro, Streamlit, Dash, Gradio, Reflex) on first principles. Only Panel can attempt a static export (via Pyodide). A framework that doesn't deploy to the target host is a much worse fit than its feature set suggests. |
| Weighted decision matrix over vibes-based framework choice | "Vizro is low code" vs. "Next.js is familiar" are vibes, not decisions. A 12-15 criterion weighted matrix forces articulation of what the project actually values (deployment fit, pipeline reuse, LOC, etc.) and produces defensible preferences with explicit weights. |
| Framework version ≥1.0 for production | 0.x versions signal breaking API changes are still expected. Vizro at 0.1.56 (3 years old) is the least mature option on any reasonable Python dashboard list. Mature frameworks (Next.js 15, Dash 4, Streamlit 1.55) hit 1.0+ years ago and have stable, documented patterns. |
| Pipeline reuse scored at 10+ in framework comparison | Switching from Next.js (consumes 5 static JSONs) to a Python server framework (queries DuckDB) discards the export pipeline. For a 4-page dashboard, 500 LOC of UI is one week of work — rebuilding the data layer is two weeks minimum and adds a new failure mode. |
| Dash Pages over manual URL routing | `use_pages=True` + `dash.register_page` eliminates per-page URL callback boilerplate. One `page_container` in app layout replaces manual `dcc.Location` + pathname matching. |
| `lru_cache` over per-callback DuckDB connections | 4 pages × 3 filters = 12+ connections per user session. `lru_cache(maxsize=32)` serves repeated queries from in-process memory; `read_only=True` prevents accidental writes. |
| Global filter IDs over `dcc.Store` for filter state | Dash Pages shares the same layout across pages — global filter IDs work without intermediate Store. `dcc.Store` only needed for cross-reload persistence. |
| Port 7860 for HF Spaces | HF Spaces standard port; changing requires Space config update. Local dev matches production port for parity. |
| Dash 3.x strict output declaration | Dash 3.x raises `InvalidCallback` for undeclared outputs (Dash 2.x silently ignored). All `@callback` outputs must be declared and returned. |

---

## 87. Vizro `vm.Filter` is Per-Page, Not Cross-Page

### The Problem

Vizro's `vm.Filter(column="commodity_consolidated")` placed on a `vm.Page` only filters components *on that page*. If the user selects "Rice" on Page 1, then navigates to Page 2, the filter resets to default. This is a fundamental difference from the Dash plan (`dcc.Store` / global filter IDs share state across pages via the Dash Pages layout).

### Investigation

Three patterns for cross-page state in Vizro:

| Pattern | Mechanism | Pros | Cons |
|---------|-----------|------|------|
| `show_in_url=True` on each `vm.Filter` | Filter state encoded in URL query string | Battle-tested; survives reload; shareable URLs | URLs get long; user must understand URL = state |
| Custom `vm.Action` pushing to global state | `vm.Action` writes to a session-level dict | Clean URLs | Custom code; not battle-tested in 0.1.50; works only in same session |
| Pydantic model registration at app level | Filter registered on `vm.Dashboard` not `vm.Page` | Single source of truth | Does not actually share state across pages in Vizro 0.1.50 — register at app level still scopes to current page navigation. (Confirmed limitation in 0.1.50 docs.) |

### Solution

Default to `show_in_url=True` for all 3 global filters (Commodity, Island Group, Year Range) on all 4 pages. Document the URL state. Revisit if the user rejects the URL state pattern.

```python
# All 3 filters, on all 4 pages:
vm.Filter(
    column="commodity_consolidated",
    selector=vm.Dropdown(options=[...]),
    show_in_url=True,
)
```

### Files Affected

- `dashboard/app.py` — Vizro dashboard config with 4 pages, each with 3 `show_in_url=True` filters
- `docs/LEARNINGS.md` — this section

### Rule

For Vizro 0.1.50 cross-page filter state, use `show_in_url=True` on every page-level `vm.Filter`. Do not rely on app-level filter registration — it does not propagate across page navigation in 0.1.50. The URL-state pattern is ugly but battle-tested.

---

## 88. Vizro `custom_charts` Wrapper for Advanced Plotly (vline, vrect, CI area, vendored GeoJSON choropleth)

### The Problem

Vizro's built-in `vizro.plotly.express` shortcuts cover ~80% of chart types. The other 20% — `add_vline` annotations, `add_vrect` bands, 95% CI shaded areas via `go.Scatter(fill="toself")`, `px.choropleth` with vendored GeoJSON — require custom registration.

### Solution

Wrap each advanced figure builder as a `@capture("graph")` function and call it in `vm.Graph(figure=...)`:

```python
from vizro.models.types import capture

@capture("graph")
def trend_with_forecast_and_ci(df, forecast_df, shock_date="2022-01-01"):
    fig = go.Figure()
    # Actuals: solid lines
    for commodity in df["commodity_consolidated"].unique():
        sub = df[df["commodity_consolidated"] == commodity]
        fig.add_trace(go.Scatter(x=sub["month"], y=sub["avg_price_idr"],
                                  name=commodity, mode="lines"))
    # Forecast: dashed lines
    for commodity in forecast_df["commodity_consolidated"].unique():
        sub = forecast_df[forecast_df["commodity_consolidated"] == commodity]
        fig.add_trace(go.Scatter(x=sub["ds"], y=sub["yhat1"],
                                  name=f"{commodity} (forecast)",
                                  mode="lines", line=dict(dash="dash")))
    # CI shaded area
    fig.add_trace(go.Scatter(
        x=list(sub["ds"]) + list(sub["ds"][::-1]),
        y=list(sub["yhat_upper"]) + list(sub["yhat_lower"][::-1]),
        fill="toself", fillcolor="rgba(100,100,200,0.2)",
        line=dict(width=0), showlegend=False
    ))
    # Annotations
    fig.add_vline(x=shock_date, line_dash="dash", line_color="red")
    fig.add_annotation(x=shock_date, y=1, yref="paper",
                        text="Cooking oil export ban", showarrow=True)
    return fig
```

Use in page:
```python
vm.Page(
    title="Price Trends",
    components=[vm.Graph(id="trend_chart", figure=trend_with_forecast_and_ci(
        df=data_manager["mart_price_trends_national"],
        forecast_df=data_manager["forecast"],
    ))],
)
```

### What Requires `custom_charts` (this project)

| Chart | Built-in? | Why custom |
|-------|-----------|-----------|
| Forecast trend + CI area | ❌ | `go.Scatter(fill="toself")` for CI; `add_vline` for shock |
| Ramadan overlay bands | ❌ | `add_vrect` for T-3 to T+1 windows |
| Choropleth with vendored Indonesian GeoJSON | ❌ | `px.choropleth(geojson=...)` with non-built-in shape file |
| Rolling correlation with 2022 break | ❌ | `add_vrect` for structural break region |
| Heatmap (`px.imshow`) | ✅ | Use `vizro.plotly.express.imshow` directly |
| Bar chart (`px.bar`) | ✅ | Use `vizro.plotly.express.bar` directly |
| Line chart (`px.line`) | ✅ | Use `vizro.plotly.express.line` directly |

### Files Affected

- `dashboard/charts/` (new) — one `.py` per `custom_charts` function
- `dashboard/app.py` — imports + `vm.Graph(figure=fn(...))` calls

### Rule

For any Plotly figure requiring `add_vline`, `add_vrect`, `add_annotation`, `go.Scatter(fill="toself")`, or a non-built-in GeoJSON, wrap the builder as a `@capture("graph")` function in `dashboard/charts/`. Use `vizro.plotly.express` shortcuts only for vanilla `px.line` / `px.bar` / `px.imshow` / `px.scatter`.

---

## 89. Cross-Page Filter Workaround: URL State vs Custom Action (Pick One)

### The Problem

§87 documents that Vizro 0.1.50 `vm.Filter` is per-page. The 4-page dashboard needs Commodity / Island / Year to persist across page navigation. The two patterns to choose between:

| Pattern | When to use |
|---------|-------------|
| `show_in_url=True` on every page's `vm.Filter` | Default. URLs are shareable. No custom code. Survives reload. |
| Custom `vm.Action` writing filter values to a global registry | When URL state is unacceptable (e.g., user wants clean URLs, or filter is sensitive/shouldn't be in URL). Requires ~50 LOC custom action. |

### Decision Made (2026-06-02)

**Default: `show_in_url=True` for all 3 global filters on all 4 pages.** Rationale:

1. **Lowest LOC** — single flag, no custom code
2. **Survives reload** — page bookmark works
3. **Battle-tested** — Vizro core feature, not custom
4. **Shareable URLs** — analyst can send "this filter combination" link to colleague

URL aesthetics (long URLs) accepted as cost. Revisit if user pushes back.

### Files Affected

- `dashboard/app.py` — every `vm.Filter` gets `show_in_url=True`
- `docs/LEARNINGS.md` — this section + §87

### Rule

For Vizro 0.1.50 cross-page filter state, prefer `show_in_url=True` over custom `vm.Action`. The URL-state pattern is documented, stable, and shares/leaks no architectural complexity. Custom actions are reserved for cross-page state that genuinely cannot live in the URL (rare; nothing in this 4-page dashboard qualifies).

---

## 90. Vizro `data_manager.register_data()` for DuckDB DataFrames

### The Problem

Vizro charts and tables consume DataFrames from a global `data_manager` (Vizro's built-in). The project's existing `data_access.py:load_mart(name, **filters)` returns DataFrames from DuckDB. These need to be registered with Vizro's `data_manager` so charts can reference them.

### Solution

Wrap `load_mart` calls in `data_manager.register_data()`:

```python
# dashboard/data_manager.py
import vizro.models as vm
from dashboard.data_access import load_mart, load_forecast_data

data_manager = vm.DataManager()
data_manager.register_data("mart_price_trends_national",
                            lambda: load_mart("mart_price_trends_national"))
data_manager.register_data("mart_seasonal_patterns",
                            lambda: load_mart("mart_seasonal_patterns"))
data_manager.register_data("mart_geo_disparity",
                            lambda: load_mart("mart_geo_disparity"))
data_manager.register_data("mart_commodity_correlation",
                            lambda: load_mart("mart_commodity_correlation"))
data_manager.register_data("mart_correlation_summary",
                            lambda: load_mart("mart_correlation_summary"))
data_manager.register_data("forecast",
                            lambda: load_forecast_data())
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `load_mart()` kept as-is in `data_access.py` | Framework-agnostic; works in Dash, Vizro, Streamlit, Marimo — only the consumer changes |
| `data_manager.register_data(name, lambda)` not `register_data(name, df)` | Lazy load; DataFrame computed on first chart reference, not at app startup |
| Reuses `dashboard/data_access.py:load_mart()` | `lru_cache(maxsize=32)` from §82 still works — same function, just called from Vizro's `data_manager` instead of Dash callbacks |
| Forecast as a single `forecast` key | Single JSON load; per-commodity filtering happens inside the chart, not at data layer |

### Files Affected

- `dashboard/data_manager.py` (new) — `data_manager` instance + `register_data` calls
- `dashboard/data_access.py` — **unchanged** (kept for §82 preservation)
- `dashboard/app.py` — imports `data_manager` and references `data_manager["mart_X"]` in `vm.Graph(figure=fn(data_manager["mart_X"]))` calls

### Rule

Register all DataFrames with Vizro's `data_manager` via `register_data(name, lambda)`. Keep `dashboard/data_access.py` (DuckDB + lru_cache) framework-agnostic — only the registration layer changes between frameworks. The lambda registration pattern defers DataFrame computation until chart render, keeping app startup fast.

---

## 91. Vizro HF Spaces Dockerfile: gunicorn `app:app`, Same Port 7860

### The Problem

Vizro exposes its Flask handle differently than Dash. `Vizro().build(dashboard).run()` returns an object whose `app` attribute is the WSGI app. The Dash `Dockerfile` from §84 used `gunicorn app:server` (Dash's `app.server` is the Flask handle). Vizro's equivalent is `gunicorn app:app`.

### Solution

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Layer 1: deps (cached unless pyproject.toml changes)
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Layer 2: dashboard code
COPY dashboard/app.py dashboard/data_manager.py dashboard/
COPY dashboard/charts/ dashboard/charts/
COPY dashboard/data_access.py dashboard/
COPY data/wfp.duckdb data/wfp.duckdb
COPY dashboard/public/data/forecast.json dashboard/public/data/forecast.json

EXPOSE 7860
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120"]
```

`app:app` = module `app.py` (Vizro entry) → attribute `app` (the WSGI handle).

### What Carries Over from §84

| Pattern | Status |
|---------|--------|
| Port 7860 | ✅ Same |
| 2 gunicorn workers | ✅ Same (free-tier CPU limit) |
| `--timeout 120` | ✅ Same (cold-start DuckDB) |
| Layer order: deps → code → data | ✅ Same |
| `--frozen --no-dev` | ✅ Same |
| Excluded dirs in `.dockerignore` | ✅ Same |

### What Changes from §84

| Pattern | Old (Dash) | New (Vizro) |
|---------|-----------|-------------|
| gunicorn target | `app:server` | `app:app` |
| `dashboard/pages/` directory | Required | Not used (pages in `app.py` Pydantic config) |
| `dashboard/components/` directory | Required | Not used (Vizro built-ins) |
| Charts dir | n/a | `dashboard/charts/` (new) for `custom_charts` |
| Data manager dir | n/a | `dashboard/data_manager.py` (new) |

### Files Affected

- `dashboard/Dockerfile` — `app:server` → `app:app`
- `dashboard/.dockerignore` — `dashboard/spike/` added (excluded from image)
- `dashboard/app.py` — single entry point, no `dash.register_page`, no `app.layout`; just `vm.Dashboard(pages=[...])` + `Vizro().build(dashboard).run()`

### Rule

For Vizro on HF Spaces, gunicorn target is `app:app` (not Dash's `app:server`). Everything else from §84 carries over: port 7860, 2 workers, 120s timeout, layer-ordered Dockerfile, `--frozen --no-dev`. The dashboard code structure changes (no `pages/` dir, no `components/` dir, no callbacks) but the deployment shape is identical.

---

## 92. Component Mismatch Assessment: Vizro vs Dash

When migrating wireframes to Vizro, systematically assess every component against two lists: Vizro native (§2.1 of wireframe evaluation) and Vizro extension (§2.2). Do not assume a component is "just a card" — Vizro's `vm.Figure` has different capabilities than `vm.Graph`.

| Wireframe Element | Vizro Component | Gap | Workaround |
|-------------------|----------------|-----|------------|
| KPI card with sparkline | `vm.Figure` (kpi_card_reference) | No embedded chart support | Custom `@capture("figure")` returning `dbc.Card` with nested `dcc.Graph` |
| Buy Signal Monitor | `vm.Figure` or `vm.Card` | No native status list | Custom figure returning `dbc.ListGroup` |
| Conditional chart show/hide | `vm.Graph` | No built-in visibility toggle | Dash callback on `style={"display": "none/block"}` |
| Animated year slider | `vm.Slider` | No playback button | `dcc.Interval` + manual callback |

### Rule

Before building any wireframe in Vizro, produce a component-by-component mapping table (like the one above). Do not start coding until every non-native component has a named extension pattern.

---

## 93. Static Assets Convention: `assets/` Not `public/`

Vizro/Dash serves static files from `dashboard/assets/`, not `dashboard/public/`. Wireframes and evaluation docs must reference `assets/` paths. GeoJSON files, custom CSS, and images go here.

```python
# Correct
with open("dashboard/assets/indonesia_island_groups.geojson") as f:
    geojson = json.load(f)

# Wrong — this is a React/Next.js convention
with open("dashboard/public/indonesia_island_groups.geojson") as f:
    geojson = json.load(f)
```

### Rule

All static asset paths in specs, wireframes, and evaluation docs must use `assets/` prefix. The `public/` directory does not exist in Vizro projects.

---

## 94. Source → Control → Target Interaction Pattern

Every Vizro interaction follows the `wiring-vizro-actions` skill's three-role model:

| Role | Definition | Examples |
|------|-----------|----------|
| **Source** | Component that emits data on user interaction | `vm.Graph` (clickData), `vm.AgGrid` (selectedRows), `vm.Filter` (value) |
| **Control** | Mechanism that carries data from source to target | `vm.Filter`, `vm.Parameter`, `vm.Action`, `dcc.Store` + manual callback |
| **Target** | Component that receives and reacts to data | `vm.Graph` (data_frame), `vm.AgGrid` (rowData), custom figure (function arg) |

Critical constraint: **Only `vm.Graph` and `vm.AgGrid` can be sources.** `vm.Figure` (KPI cards, custom cards) cannot emit click data. This means:
- KPI cards cannot be `set_control` sources
- Custom `dbc.Card` figures cannot participate in `vm.Action` chains
- Bidirectional KPI↔map interactions (Page 3) require manual Dash callbacks

### Rule

When planning interactions, explicitly label each component as Source, Control, or Target. If a `vm.Figure` needs to be a source, plan for manual `@callback` registration.

---

## 95. `vm.Figure` Cannot Be a `set_control` Source

Vizro's `vm.Action(function=set_control)` only works when the source is a `vm.Graph` or `vm.AgGrid`. `vm.Figure` (which includes `kpi_card`, `kpi_card_reference`, and custom `@capture("figure")` returning `dbc.Card`) does not expose click data to Vizro's action system.

**Impact on Page 3:** The wireframe specifies "clicking a KPI card highlights that island group on map and filters province drill-down table." This cannot be done with `va.set_control`. Implementation requires:

1. Custom click handler on the KPI card's underlying `dbc.Card` (via `n_clicks` prop)
2. A `dcc.Store` holding `selected_island_group`
3. A manual `@callback` that reads the card click and updates the store
4. Second-order callbacks that read the store and update the map + table

### Rule

If a wireframe requires KPI card → chart interaction, budget for manual callback registration. Do not attempt `vm.Action(function=set_control)` with `vm.Figure` sources — it will silently fail.

---

## 96. Conditional Visibility Requires Dash Callback

Vizro has no built-in conditional rendering of components. When a wireframe says "show chart X when driver = Ramadan, hide when driver = Harvest," this requires a Dash callback outside Vizro's declarative model.

**Implementation pattern:**

```python
# After Vizro builds the dashboard
app = Vizro().build(dashboard)

@app.callback(
    Output("ramadan-chart-container", "style"),
    Input("driver-radio", "value"),
)
def toggle_driver_chart(driver):
    if driver == "Ramadan":
        return {"display": "block"}
    return {"display": "none"}
```

**Gotcha:** The callback targets the underlying HTML container ID, not the Vizro component name. Use browser DevTools to find the actual DOM IDs generated by Vizro.

### Rule

For conditional visibility, plan Dash callbacks in the wireframe phase. Document which components need toggling and what triggers the toggle. Do not assume Vizro handles this declaratively.

---

## Updated Decision Log (Vizro migration, 2026-06-02)

| Decision | Rationale |
|----------|-----------|
| Vizro over Dash (re-decision 2026-06-02) | Cross-filtering primitive (`set_control` action) enables chart-click-to-filter UX that the 4 pages imply. Dash has no equivalent without 80+ LOC of custom callbacks per cross-filter pair. Weighted matrix: cross-filtering (8) + LOC (6) outweigh maturity (5), pipeline reuse (1), and Page 1 sunk cost (5). Net decision: accept 2-3 extra days of work + 0.x framework risk in exchange for built-in cross-filter. |
| Phase A spike (0.5 day) as decision gate | Vizro 0.1.50 maturity risk. Spike validates Pydantic config, `custom_charts`, `data_manager`, and port 7860 in 0.5 day before committing to 3-4 day Phase C. If spike fails, revert to §6.HISTORY (Dash). |
| `data_access.py` preserved, not rewritten | Framework-agnostic. `load_mart()` DuckDB + lru_cache pattern works in any Python framework. Vizro consumes via `data_manager.register_data()` wrapper, not by rewriting the data layer. Aligns with §78 preservation rule. |
| `export_json.py` + `verify_export()` unchanged | Kept as row-count verification artefact per §78. Dashboard does not consume the 5 JSONs in production; they are a data-quality check logged to `pipeline.lineage.export_status`. |
| `show_in_url=True` for cross-page filters | Battle-tested Vizro pattern. URL state is ugly but stable, shareable, reload-survivable. Default to URL state over custom `vm.Action` unless URL aesthetics are unacceptable. |
| Port 7860 preserved (not changed to Dash default 8050) | HF Spaces standard; same as §84. Local dev matches production for parity. |
| gunicorn target `app:app` (not `app:server`) | Vizro exposes its own Flask handle differently than Dash. `Vizro().build(dashboard).run()` returns object with `.app` attribute = WSGI app. |
| Dash deps removed from `pyproject.toml` after Phase C verified | During Phase A-C, keep `dash`, `dash-bootstrap-components`, `dash-ag-grid` in deps for the working Dash dashboard. After Vizro spike passes and pages are ported, remove Dash deps to keep lockfile clean. |

---

## 97. `vm.Filter` Treats "All" as Literal Column Value — Use `vm.Parameter` for Sentinel-Based Filtering

### The Problem

`vm.Filter(column="commodity_consolidated", selector=vm.Dropdown(options=["All", "Rice", ...], value="All"))` calls `_filter_isin(series, ["All"])` which filters for rows where `commodity_consolidated == "All"` — no matches → empty DataFrame. Vizro has no concept of "All" as a "show everything" sentinel.

### Root Cause

Vizro 0.1.53's `_filter_isin` (`.venv/lib/python3.13/site-packages/vizro/models/_controls/filter.py:63-75`) applies `series.isin(value)` with no sentinel handling. Every value in the `options` list is treated as a literal column value to match.

### Solution

Replace `vm.Filter` with `vm.Parameter`:

```python
# Before: vm.Filter filters data at the Vizro engine level — no "All" sentinel support
vm.Filter(
    column="commodity_consolidated",
    selector=vm.Dropdown(options=["All", "Rice", ...], value="All"),
)

# After: vm.Parameter passes the dropdown value to chart functions — they handle "All" themselves
vm.Parameter(
    targets=["kpi_sparklines.commodity_filter", "trend_forecast.commodity_filter", ...],
    selector=vm.Dropdown(options=["All", "Rice", ...], value="All", multi=False),
)
```

Chart functions receive the Dropdown value directly and handle `"All"` → no-filter:
```python
@capture("graph")
def my_chart(data_frame: pd.DataFrame, commodity_filter: str = "All") -> go.Figure:
    if commodity_filter != "All":
        data_frame = data_frame[data_frame["commodity_consolidated"] == commodity_filter]
    ...
```

### Rule

`vm.Filter` does not support sentinel values like "All" — it passes all values literally to the `series.isin()` filter. Use `vm.Parameter` when the first dropdown option is a "show all" sentinel. The chart function receives the raw dropdown value and implements its own filter logic with a simple `if sentinel != "All"` guard.

### Files Affected

- `dashboard/pages/price_trends.py` — `vm.Filter` → `vm.Parameter` with `targets` pointing to chart function params
- All 4 chart files — added `commodity_filter: str = "All"` parameter with the sentinel guard

### Cross-Reference

- LEARNINGS.md §98 — Companion bug: `_get_parametrized_config` timing causes first-render issues with `vm.Parameter`
- LEARNINGS.md §87 — Vizro `vm.Filter` is per-page, not cross-page

---

## 98. `_get_parametrized_config` Timing — Bound Argument Literals on First Render Before Callback Fires

### The Problem

Forecast trend lines + CI area missing on initial page load. After toggling the sidebar (close/reopen), the chart renders correctly.

### Root Cause

Vizro callback timing. On first page load, `_get_parametrized_config()` (`_actions_utils.py:165`) returns the literal bound argument `{"commodity_filter": "commodity_filter"}` because the `vm.Parameter` callback **hasn't fired yet**. The chart function receives `commodity_filter="commodity_filter"` → no data matches → early return with "No data available".

Sidebar toggle triggers a re-render where the `vm.Parameter` callback has already fired → `commodity_filter` gets the real Dropdown value → chart renders correctly.

### Solution

Remove the literal `commodity_filter="commodity_filter"` from `vm.Graph()` calls. Chart functions already have `commodity_filter: str = "All"` as default. On first render, bound args won't include `commodity_filter`, so the function uses its default `"All"`. `vm.Parameter` still overrides it on subsequent renders because `CapturedCallable.__call__` merges `{**bound_arguments, **kwargs}` with runtime kwargs overriding.

```python
# Before: literal arg is passed as bound argument — causes function to receive the string "commodity_filter"
vm.Graph(
    id="trend_forecast",
    figure=trend_forecast(data_frame="...", commodity_filter="commodity_filter"),
)

# After: no literal arg — chart function uses its default "All" on first render
vm.Graph(
    id="trend_forecast",
    figure=trend_forecast(data_frame="..."),  # no commodity_filter literal
)
```

### How the Fix Works

| Render | Bound arguments | `commodity_filter` value | Source |
|--------|----------------|-------------------------|--------|
| First load | `{}` (empty — no callback fired yet) | `"All"` | Function default parameter |
| Filter change | `{"commodity_filter": "Rice"}` | `"Rice"` | `vm.Parameter` override |
| Page navigation | `{"commodity_filter": "Sugar"}` | `"Sugar"` | `vm.Parameter` (show_in_url restored) |

### Reference

`_actions_utils.py:252-280` — `_get_modified_page_figures` calls `_get_parametrized_config(ctds_parameter, target, data_frame=False)` which copies bound arguments. On first load, `ctds_parameter` is empty → config stays as literals.

### Rule

When using `vm.Parameter` to override chart function parameters, never pass the parameter name as a literal value in the `vm.Graph()` call. Let the chart function use its Python default for the first render. `vm.Parameter` will override on subsequent renders via `CapturedCallable.__call__` merge behavior. Always provide sensible function defaults (like `"All"`) as the fallback.

### Files Affected

- `dashboard/pages/price_trends.py` — removed `commodity_filter="commodity_filter"` from all 4 `vm.Graph()` calls

### Cross-Reference

- LEARNINGS.md §97 — Companion bug: `vm.Filter` "All" sentinel issue — use `vm.Parameter` instead
- LEARNINGS.md §96 — Conditional visibility requires Dash callback

---

## 99. `mart_seasonal_patterns` Has 35 Rows (Cooking Oil Only, 7 Months) — Use `mart_price_trends_national` for Cross-Commodity Seasonal Analysis

### The Problem

Page 2 (Seasonal Patterns) wireframe expects a 12-month × 4-commodity heatmap and a 4-commodity Ramadan overlay. The mart originally named as the source — `mart_seasonal_patterns` — has only 35 rows and only Cooking Oil data. The original handoff (`HANDOFF-page2-seasonal-patterns-implementation.md`, pre-2026-06-04) cited 597 records from `seasonal_patterns.json`; that number is wrong. Verified by direct DuckDB query on 2026-06-04.

### What `mart_seasonal_patterns` Actually Contains

| Source | Row count | Commodities | Date range | Reason |
|---|---|---|---|---|
| `mart_seasonal_patterns` (DuckDB) | **35** | Cooking Oil only | 2024-06 → 2024-12 | Filtered to `island_group IS NOT NULL AND price_flag='actual'` — eliminates national-only commodities (Rice, Sugar, Flour) and eliminates aggregate market data |
| `seasonal_patterns.json` (legacy export) | 35 | Cooking Oil only | 2024-06 → 2024-12 | Exported from the same mart; same shape |
| `mart_price_trends_national` (DuckDB) | **639** | **All 4** commodities | 2007-01 → 2024-12 (Cooking Oil, 165 months) · 2007-01 → 2020-03 (others, 158 months each) | National-level data with `price_flag='actual'` filter applied — covers cross-commodity seasonal analysis |

### Root Cause of the Limitation

`mart_seasonal_patterns.sql` (Phase 2 / Phase 2.5) joins `int_prices_normalised` and applies both:
- `commodity_consolidated IS NOT NULL` (keeps all 4 commodities)
- `island_group IS NOT NULL` (keeps only rows that have an island_group mapping)
- `price_flag = 'actual'` (removes aggregate records)

Rice, Sugar, and Flour in the WFP dataset exist only as `price_flag = 'aggregate'` at the national level (market_id = 974), so they are excluded by the `price_flag = 'actual'` filter. The `island_group IS NOT NULL` filter does not affect them (they have island_group = 'National'), but the `price_flag = 'actual'` filter alone removes them. The 35 rows are 5 island groups × 7 months of Cooking Oil actual prices in 2024.

### Solution

For cross-commodity seasonal analysis (heatmap 12×4, action cards 4 commodities, Ramadan overlay 4 commodities), use `mart_price_trends_national` as the **primary** source. The mart already exists (created in Phase 5g.1) and has 639 rows covering all 4 commodities. `mart_seasonal_patterns` remains the **secondary** source for the island-disaggregated branch (only when global Island Group filter is set to a specific island AND Commodity = Cooking Oil).

### Per-Commodity Date Floor in `mart_price_trends_national`

| Commodity | Date range | Months |
|---|---|---|
| Cooking Oil | 2007-01 → 2024-12 | 165 |
| Rice | 2007-01 → 2020-03 | 158 |
| Sugar | 2007-01 → 2020-03 | 158 |
| Flour | 2007-01 → 2020-03 | 158 |

The Rice/Sugar/Flour terminal date of 2020-03 is a known WFP data gap, not a mart issue. The dashboard must communicate this as a limitation: "Rice/Sugar/Flour data ends March 2020; seasonal patterns computed on the available window."

### Files Affected

- `dashboard/pages/seasonal_patterns.py` — uses `mart_price_trends_national` as primary; `mart_seasonal_patterns` only for island-disaggregated Cooking Oil path
- `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` — updated 2026-06-04 with corrected row counts, source recommendation, and 15 gap-fixes

### Cross-Reference

- LEARNINGS.md §100 — Source data is monthly; Ramadan `month_relative` reframing
- LEARNINGS.md §97 — `vm.Filter` "All" sentinel → `vm.Parameter` (matters because the Commodity dropdown now needs "All" support for the 4-commodity heatmap)
- AGENTS.md Known Limitations — Rice/Sugar/Flour data ends March 2020; Page 3 (Geographic Disparity) remains Cooking Oil only

### Rule

**Verify mart row counts before assuming a mart is fit for purpose.** A 35-row mart is not a cross-commodity source; it is an island-disaggregated Cooking Oil slice. When the wireframe or task description implies more data than the mart contains, query the mart directly with `SELECT COUNT(*), COUNT(DISTINCT commodity_consolidated), MIN(month), MAX(month) FROM wfp_marts.<mart_name>` before designing the dashboard page. Match the source mart to the cardinality requirements of the page.

---

## 100. Source Data Is Monthly — Page 2 (Seasonal Patterns) Ramadan `month_relative` Is T-2 to T+1, Not `week_relative` T-8 to T+6

### The Problem

Page 2 wireframe (`docs/wireframes/wfp-wireframe-page2-seasonal-patterns.md`, annotation [6d]) specifies the Ramadan overlay x-axis as `week_relative` ranging from T-8 to T+6 (15 weekly buckets). The wireframe evaluation doc (`docs/wireframes/wfp-vizro-wireframe-evaluation.md` §6.W.5, line 601) "resolved" this as "integer `week_relative` with formatted tick labels." Both are wrong: the source data is monthly, not weekly. Building per-week buckets from monthly data is either impossible (no week-level data exists) or misleading (interpolating a fake weekly series from monthly samples).

### What the Data Actually Is

| Layer | Grain | Source |
|---|---|---|
| `raw.food_prices` | Monthly (always 15th of month) | WFP CSV |
| `int_prices_normalised` | Monthly | `DATE_TRUNC('month', date)` |
| `mart_price_trends_national` | Monthly | Group by `month` |
| `int_islamic_calendar` | Yearly (Eid date per year) | `seeds/islamic_calendar.csv` |

There is no weekly grain anywhere in the pipeline. `week_relative` cannot be computed from this data.

### Solution

Compute `month_relative` instead, with range T-2 to T+1 (4 monthly buckets: 2 months before Eid, the Eid month, and 1 month after):

```python
# dashboard/data_access.py
def compute_ramadan_overlay(monthly_df: pd.DataFrame, islamic_cal: pd.DataFrame) -> pd.DataFrame:
    """Add month_relative column: months from Eid al-Fitr (range T-2 to T+1)."""
    cal = islamic_cal[["year", "eid_date"]].copy()
    cal["eid_month"] = pd.to_datetime(cal["eid_date"]).dt.to_period("M")
    out = monthly_df.merge(cal, left_on="month_year", right_on="eid_month", how="left")
    out["month_relative"] = (
        (out["month"].dt.year - out["eid_date"].dt.year) * 12
        + (out["month"].dt.month - out["eid_date"].dt.month)
    )
    return out[out["month_relative"].between(-2, 1)]
```

X-axis label: `["T-2 (2 mo before)", "T-1 (1 mo before)", "T (Eid month)", "T+1 (1 mo after)"]`. Y-axis: `price_index_vs_annual_avg` with `add_hline(y=100)` as annual average baseline. One trace per commodity, bold lines.

### Wireframe Deviation

Per Phase C handoff rule (`docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md`), do NOT edit wireframes even when the spec is wrong. Surface the deviation in the PR description when Page 2 is submitted:

> **Wireframe deviation (Page 2, annotation [6d]):** Wireframe specifies `week_relative` T-8 to T+6. Source data is monthly, so the implementation uses `month_relative` T-2 to T+1. The wireframe x-axis range and bucket count are reduced to match the source grain. Annotation/caption on the chart explains the monthly grain and the T-2 to T+1 range.

### Files Affected

- `docs/wireframes/wfp-vizro-wireframe-evaluation.md` §6.W.5 — note that the "integer `week_relative`" resolution was insufficient; actual resolution is `month_relative` T-2 to T+1
- `dashboard/data_access.py` — add `compute_ramadan_overlay(monthly_df, islamic_cal)` helper
- `dashboard/pages/seasonal_patterns.py` — Ramadan overlay chart uses `month_relative` and the new T-2 to T+1 range
- `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` §2 — updated 2026-06-04 with the `month_relative` reframing

### Cross-Reference

- LEARNINGS.md §99 — `mart_seasonal_patterns` 35-row limitation; `mart_price_trends_national` as primary source
- LEARNINGS.md §88 — Vizro `custom_charts` wrapper pattern (used to build the Ramadan overlay figure)

### Rule

**Match the analysis grain to the source data grain.** If the data is monthly, do not design weekly or daily visualisations. Compute offsets in the same unit as the source grain. Wireframe specs that imply a finer grain than the data supports are a deviation to surface, not a constraint to honour by interpolating fake data.

---

## 101. `@capture("ag_grid")` Functions Must Return `dag.AgGrid`, Not `pd.DataFrame`

### The Problem

Page 2 (Seasonal Patterns) callback crashes with:

```
TypeError: Object of type DataFrame is not JSON serializable
dash.exceptions.InvalidCallbackReturnValue: The callback for `{...}` returned a value having type `dict`
which is not JSON serializable.
```

The `seasonal_summary_table` function was decorated with `@capture("ag_grid")` but returned a raw `pd.DataFrame`.

### Root Cause

Vizro's `AgGrid.__call__()` (`vizro/models/_components/ag_grid.py:140-160`) wraps the return value of the captured function in `html.Div([figure, dcc.Store(...)])`. When `figure` is a `pd.DataFrame`, the Div contains a non-serializable object. Dash's callback system attempts to JSON-serialize the entire callback response dict, fails on the DataFrame inside the Div, and raises `InvalidCallbackReturnValue`.

The Vizro built-in `dash_ag_grid` function (`vizro/tables/_dash_ag_grid.py:52`) shows the correct pattern: `@capture("ag_grid")` functions must return a `dag.AgGrid` component.

### Solution

Convert the DataFrame to a `dag.AgGrid` component with `columnDefs` and `rowData`:

```python
@capture("ag_grid")
def seasonal_summary_table(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
) -> dag.AgGrid:  # Return type is dag.AgGrid, not pd.DataFrame
    # ... compute result DataFrame ...
    return dag.AgGrid(
        columnDefs=[{"field": col} for col in result.columns],
        rowData=result.to_dict("records"),
        className="ag-theme-vizro",
        defaultColDef={"resizable": True, "sortable": True, "filter": True},
        dashGridOptions={
            "animateRows": False,
            "domLayout": "autoHeight",
            "pagination": True,
            "paginationPageSize": 20,
        },
        columnSize="responsiveSizeToFit",
    )
```

### Rule

`@capture("ag_grid")` functions must return a `dag.AgGrid` component, never a raw `pd.DataFrame`. The DataFrame is JSON-serializable only via `dag.AgGrid(columnDefs=..., rowData=df.to_dict("records"))`. Compare with `@capture("graph")` which returns `go.Figure` (also JSON-serializable via Plotly's encoder).

### Files Affected

- `dashboard/charts/seasonal_summary_table.py` — return type changed from `pd.DataFrame` to `dag.AgGrid`

### Cross-Reference

- `vizro/tables/_dash_ag_grid.py` — Vizro's built-in implementation showing the correct pattern
- `vizro/models/_components/ag_grid.py:160` — `AgGrid.__call__` wraps return in `html.Div([figure, dcc.Store(...)])`
- LEARNINGS.md §88 — Vizro `custom_charts` wrapper pattern (companion for `@capture("graph")`)

---

## 102: Marimo-Native Rewrite: `mo.stat()` Over Plotly Annotation Hacks

### Context

The original dashboard (Vizro era) used Plotly `make_subplots` with annotation text overlays for KPI cards, signal badges as annotations on invisible charts, and action cards via Plotly annotations with background/border colors.

### Solution

Replaced with proper Marimo UI components:

| Old (Vizro) | New (Marimo-native) |
|-------------|-------------------|
| `make_subplots` + annotation text for KPI cards | `mo.stat(value=..., label=..., caption=..., bordered=True, slot=sparkline)` |
| Plotly annotations for signal badges | `mo.md("<span>...</span>")` with inline colored dots |
| Plotly annotations for action cards | `mo.stat()` in `mo.hstack()` |
| `px.imshow(RdBu_r)` for seasonal heatmap | `go.Heatmap(colorscale="Blues", zmid=0)` |
| `mo.md("> ...")` blockquotes | `mo.callout(kind="info"/"warn")` |

### Files Affected

- `dashboard/charts/kpi_sparklines.py` — rewritten from `make_subplots` to single-trace
- `dashboard/charts/seasonal_heatmap.py` — rewritten from `px.imshow` to `go.Heatmap`
- `dashboard/charts/signal_badges.py`, `action_cards.py`, `yoy_bar.py` — deleted

---

## 103: `mo.state()` Two-Sink Pattern for Cross-Filter State

### Context

Two features required multiple independent UI elements writing to a single shared state:
- Page 3 Geographic: 5 KPI buttons → province drill-down table
- Page 4 Signals: matrix click, pair dropdowns, table row click → scatter/stability chart

### Solution

`mo.state()` created in its own cell, never inside an assembly cell:

```python
selected_island, set_selected_island = mo.state("All")
```

Each source calls `set_selected_island(value)` via `on_click`:

```python
mo.ui.button(on_click=lambda _n=name: set_selected_island(_n))
```

---

## 104: Data Reality vs Wireframe Assumptions

### Context

Wireframes in `docs/wireframes/` were designed before actual JSON data structures were finalized.

| Assumption | Reality |
|-----------|---------|
| `seasonal_patterns.json` nested with all 4 commodities | Flat 35 rows, Cooking Oil only |
| `geographic_disparity.json` has multi-year data | 2024 only (34 rows) |
| `forecast.json` has `signals` key | No signals key; mix of `actual_price` and `forecast_price` rows |
| `commodity_correlation.json` is 4×4 leader×follower | 6 pairs × 4 lags in flat format |

### Mitigation

`dashboard/data_access.py` compute functions wrap flat JSON into needed shapes. Use these functions rather than assuming raw JSON paths.

---

## 105: Duplicate Variable Names Across Marimo Cells

### Context

`marimo check` reported `critical[multiple-definitions]` because `content`, `latest`, `yoy` were defined in multiple cell functions. Marimo enforces globally unique non-private variable names.

### Fix

Use unique names for exported variables (`page1_output`, `page2_output`, etc.) and `_`-prefixed names for cell-private variables.

### Rule

Every variable returned from a cell must have a globally unique name. Cell-private variables should be `_`-prefixed.

### Cross-Reference

- LEARNINGS.md §69 — Marimo module-level `__` variables

---
