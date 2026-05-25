# Issues Log — Indonesia Food Price Intelligence

Tracks data quality issues discovered during pipeline runs, with resolution status.

| # | Run ID | Layer | Issue | Status |
|---|--------|-------|-------|--------|
| 1 | `pipeline_20260525_031313` | ingest (update_lineage) | `update_lineage()` generated invalid SQL: column keys with spaces (`raw food prices rows`) instead of underscores (`raw_food_prices_rows`). DDL had been changed to underscores but kwargs used old space-separated column names. | **Fixed** — Added double-quote wrapping around column names in `config.py:update_lineage()` to be immune to naming inconsistencies. |
| 2 | `pipeline_20260525_031302` | ingest | First run crashed silently — likely DuckDB path resolution or CSV not yet staged. | **Mitigated** — Pipeline now logs all steps; `run_pipeline.py` orchestrator provides clear error output. |
| 3 | — | staging | dbt tests pass (12/12) but no row-count reconciliation between raw and staging tables existed. | **Fixed** — Added `reconcile_layer()` in `run_pipeline.py` that verifies raw → staging row counts match. |
| 4 | — | ingest | `load_raw.py` was non-idempotent — re-running appended duplicate rows via `CREATE TABLE IF NOT EXISTS` + `INSERT INTO`. | **Fixed** — Changed to `DROP TABLE IF EXISTS` + `CREATE TABLE` for clean reloads. |
| 5 | — | validation | `data_validation.py` reloads CSVs directly into DuckDB instead of reading from the pipeline-loaded `raw.*` tables. Bypasses ingest pipeline, can't catch ingest-level issues. | **Fixed** — Notebook now connects to `data/wfp.duckdb` and reads from existing `raw.*` tables. |
| 6 | — | pipeline | No orchestration script existed to chain ingest → dbt run → dbt test with lineage tracking. | **Fixed** — Created `run_pipeline.py` with full orchestration, logging, and row-count reconciliation. |
| 7 | — | config | `complete_lineage()` in `ingest/config.py` overwrote `ingest_status` with overall pipeline status — destroying the ability to audit ingest independently. Lineage table had no dedicated `status` column. | **Fixed** — Added `pipeline_status` column to DDL. `init_lineage()` and `complete_lineage()` now use `pipeline_status`. Per-phase fields (`ingest_status`, `transform_status`) are only updated by their respective phase functions. |
| 8 | — | intermediate | No dbt tests defined for intermediate models (`int_commodity_consolidated`, `int_prices_normalised`, `int_islamic_calendar`). Only staging and marts had schema.yml. | **Fixed** — Created `transform/models/intermediate/schema.yml` with `not_null`, `accepted_values`, `unique` tests for all 3 intermediate models. |
