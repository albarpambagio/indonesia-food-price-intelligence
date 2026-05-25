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
