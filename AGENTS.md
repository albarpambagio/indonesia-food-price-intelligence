# AGENTS.md

## Project Overview

Indonesia Staple Food Price Intelligence — End-to-end data pipeline + forecasting + interactive dashboard for FMCG procurement teams. Tracks 17 years of WFP market price data across 4 staple commodities, 224 markets, and 5 island groups.

| Attribute | Detail |
|-----------|--------|
| **Dataset** | WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0) |
| **Source** | World Food Programme via Humanitarian Data Exchange |
| **Volume** | 325,240 price records + 224 markets |
| **Date Range** | January 2007 – May 2024 |
| **Stack** | Python → DuckDB → dbt → statsforecast → Marimo → Static JSON → Vizro 0.1.x → Hugging Face Spaces |
| **Phase Status** | Phase 0–5 ✅, Phase 5f ✅, Phase 3f ✅ (11 pipeline gaps closed), Phase 5g ✅ (13 pre-dashboard gaps), Phase 6 §6.SPIKE ✅ §6.DATA ✅ §6.WIREFRAME ✅ — **§6.PAGES (Phase C) READY TO EXECUTE** (handoff: `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md`) |
| **Portfolio Goal** | Demonstrate upgraded ETL pipeline (DuckDB + dbt), time-series forecasting, and multi-dimensional procurement analytics |

### Business Scenario

This dashboard was built for Procurement and Supply Chain Analysts at Indonesian FMCG companies. Rising input costs for staple commodities — rice, cooking oil, sugar, and flour — represent one of the largest margin risks for food manufacturers. This tool consolidates 17 years of WFP market price data into actionable procurement intelligence: when prices are trending, when seasonal spikes are coming, where geographic arbitrage opportunities exist, and which commodities signal risk for others.

---

## Exec-Driven Questions

| # | Question | Primary Stakeholder | Page |
|---|----------|---------------------|------|
| 1 | How have staple commodity prices trended over 17 years — and what does the model forecast for the next 6 months? | Procurement Analyst, Category Manager | Page 1 |
| 2 | Which seasonal events (Ramadan, harvest cycles, year-end) cause the most predictable price spikes — and how far in advance do they occur? | Procurement Analyst | Page 2 |
| 3 | How large is the price gap between island groups, and which provinces consistently offer the lowest prices for each commodity? | Procurement Analyst | Page 3 |
| 4 | Which commodities lead others in price movement — and what does that mean for bundled procurement timing? | Category Manager, Procurement Analyst | Page 4 |

---

## Setup Commands

### Python Environment
```bash
uv sync
```

### LSP & Linting (Astral toolchain)
```bash
# Tools installed globally via uv tool (persist across sessions)
uv tool install ruff@latest    # ruff 0.15.15 — linting + formatting
uv tool install ty@latest      # ty 0.0.43 — type checking (beta, WSL only)

# Lint check
ruff check .

# Format check (dry-run)
ruff format --check .

# Auto-fix safe issues
ruff check --fix .

# Format all files
ruff format .

# Type check (run from WSL — ty cannot resolve WSL .venv from Windows)
wsl -d Debian -- bash -c "cd /home/tomioka/PROJECTS/food\ price\ dashboard && ty check ."
```

### Run Marimo Notebooks
```bash
uv run marimo edit analysis/data_validation.py          # Phase 0 — data validation
uv run marimo edit analysis/eda.py                      # Phase 4 — EDA (SCAN framework)
uv run marimo edit analysis/eda.py                      # Phase 4 EDA + Phase 5 Deep Dive (merged)
uv run marimo edit analysis/forecast_experimentation.py # Phase 3 — model selection (optional)
```

### dbt
```bash
cd transform
dbt seed             # Load seed data (islamic_calendar.csv)
dbt build            # Run + test all models in DAG order (staging → intermediate → marts)
dbt run              # Run all models (staging → intermediate → marts)
dbt test             # Run data tests (66 tests across all layers)
dbt docs generate    # Generate lineage docs
dbt docs serve       # Serve docs locally (default: http://localhost:8080)
dbt compile          # Compile SQL without running
dbt ls               # List models in project
```

### Forecasting
```bash
uv run python forecast/run_forecast.py   # DONE — Phase 3e (7 bugfixes) + Phase 3f (11 pipeline gaps)
```

### Export + Dashboard
```bash
uv run python export/export_json.py   # DONE — 5 mart JSONs via verify_export() + forecast.json
uv run python dashboard/app.py        # Dev server (HUMAN-USE ONLY — never run as agent verification, blocks forever)
# Production: same script, served via Hugging Face Spaces Docker (port 7860)
```

---

## Development Workflow

### Phase Pipeline
```
Phase 0: Setup + Data Validation  → Folder structure, marimo validation notebook, dbt init
Phase 1: Ingest & Staging         → DuckDB raw load, dbt staging models + tests        ✅ DONE
Phase 2: Transform                → dbt intermediate + mart models + tests              ✅ DONE
Phase 2.5: Corrections            → Ramadan flags, YoY delta, correlation summary, lineage fix ✅ DONE
Phase 3: Forecasting              → statsforecast AutoARIMA/AutoETS + methodology doc   ✅ DONE
Phase 3e: Bugfix                  → 7 gap fixes from pipeline audit                     ✅ DONE
Phase 3f: Pipeline Gap-Closing    → 11 gaps: Ramadan cross-year bug, hardcoded dates, unified run_id, dbt log, function split, docs, PEP 723 pins, lineage DDL dedup ✅ DONE
Phase 4: EDA                      → Marimo notebook (SCAN framework)                    ✅ DONE
Phase 4.5: Notebook Improvement   → Formatters, insight callouts, sectioning, mo.lazy    ✅ DONE
Phase 5: Deep Dive                → Marimo notebook (North Star method, merged into `analysis/eda.py`) ✅ DONE
Phase 5f: Post-Phase-5 Fixes      → Hardcoded DuckDB paths → PROJECT_DB_PATH, add numpy/scipy to pyproject, create missing snapshots/ dir, update stale checklist ✅ DONE
Phase 6: Dashboard                → 4 pages in Vizro, deployed to Hugging Face Spaces (Dash code from earlier 2026-06-02 preserved as §6.HISTORY)
Phase 7: Methodology Doc          → model_methodology.md + forecast_runbook.md      ✅ DONE
Phase 8: Write-up                 → README, insights log, recommendations            ✅ DONE
```

### Project Structure
```
indonesia-food-price-intelligence/
├── data/
│   └── raw/                    # Original CSVs — never modified
│       ├── wfp_food_prices_idn.csv
│       └── wfp_markets_idn.csv
├── ingest/
│   ├── config.py               # run_id generation, lineage helpers
│   └── load_raw.py             # Load CSVs into DuckDB staging tables
├── transform/                  # dbt project root
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── macros/
│   │   ├── generate_schema_name.sql
│   │   └── positive_values.sql
│   ├── analyses/
│   ├── tests/
│   │   └── assert_mart_rows_positive.sql
│   ├── seeds/
│   │   └── islamic_calendar.csv
│   ├── snapshots/
│   ├── docs/
│   └── models/
│       ├── sources/            # Source definitions with freshness config
│       │   └── _sources.yml
│       ├── staging/            # 1:1 with raw tables, light cleaning
│       │   ├── _staging__models.yml
│       │   ├── stg_food_prices.sql
│       │   └── stg_markets.sql
│       ├── intermediate/       # Business logic, joins, normalisation
│       │   ├── _intermediate__models.yml
│       │   ├── int_commodity_consolidated.sql
│       │   ├── int_prices_normalised.sql
│       │   └── int_islamic_calendar.sql
│       └── marts/              # Final analytical models (one per page)
│           ├── _marts__models.yml
│           ├── mart_price_trends.sql
│           ├── mart_seasonal_patterns.sql
│           ├── mart_geo_disparity.sql
│           ├── mart_commodity_correlation.sql
│           └── mart_correlation_summary.sql
├── forecast/
│   └── run_forecast.py         # statsforecast models → forecast JSON
├── export/
│   └── export_json.py          # Mart models → static JSON files
├── analysis/                   # Marimo notebooks (.py files)
│   ├── data_validation.py      # Phase 0 validation checkpoint
│   ├── eda.py                  # Phase 4 SCAN EDA + Phase 5 Deep Dive (40+ cells, 12 findings)
│   └── forecast_experimentation.py  # Phase 3 optional model comparison
├── seeds/                      # dbt seed data
│   └── islamic_calendar.csv    # Ramadan/Eid dates 2007–2024
├── dashboard/                  # Vizro app (Hugging Face Spaces) — Pydantic config + DuckDB data_manager + custom_charts
│   ├── public/
│   │   └── data/               # Static JSON files
│   └── src/
│       └── app/
├── docs/
│   ├── data_validation.md
│   ├── forecast_runbook.md
│   ├── issues_log.md
│   ├── insights_log.md
│   └── model_methodology.md
├── logs/
│   ├── ingest.log            # Raw data load + row counts
│   ├── transform.log         # dbt run + reconciliation
│   ├── forecast.log          # Forecast generation + validation
│   └── pipeline_run.log      # Orchestration summary + lineage updates
├── pyproject.toml         # uv-native dependency management
├── uv.lock                # Lockfile (auto-generated by uv sync)
├── requirements.txt       # Human-readable reference only
├── AGENTS.md
└── README.md
```

---

## Data Schema

### Raw Tables (DuckDB raw schema)
**`raw.food_prices`** (from `wfp_food_prices_idn.csv`)
| Column | Notes |
|--------|-------|
| date | Monthly grain, always 15th |
| admin1 | Province name |
| admin2 | District name |
| market | Market name |
| latitude, longitude | Market coordinates |
| commodity | Includes multiple spelling/variant forms |
| price | IDR price |
| usdprice | USD price (available, no FX enrichment needed) |
| priceflag | actual / aggregate |
| pricetype | Retail |
| unit | KG, L, 385G etc. |
| market_id | FK to raw.markets |

**`raw.markets`** (from `wfp_markets_idn.csv`)
| Column | Notes |
|--------|-------|
| market_id | PK |
| market | Market name |
| admin1 | Province |
| admin2 | District |
| latitude, longitude | |

### dbt Model Architecture
```
raw.food_prices          raw.markets          islamic_calendar.csv
  (source, fresh.)        (source, fresh.)        (dbt seed)
       │                      │                       │
       ▼                      ▼                       ▼
stg_food_prices          stg_markets           (dbt seed)
       │                      │                       │
       └──────────┬───────────┘                       │
                  ▼                                    │
     int_commodity_consolidated                        │
     int_prices_normalised                             │
     int_islamic_calendar ◄────────────────────────────┘
                  │
       ┌──────────┼──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼          ▼
mart_price   mart_seasonal  mart_geo   mart_commodity   mart_correlation
_trends      _patterns      _disparity _correlation     _summary
       │          │          │          │                 │
       └──────────┴──────────┴──────────┴─────────────────┘
                  │
           export_json.py
           run_forecast.py
                  │
         dashboard/public/data/
              *.json files
```

### Island Group Mapping
| Island Group | Provinces |
|-------------|-----------|
| Java | DKI JAKARTA, JAWA BARAT, JAWA TENGAH, DAERAH ISTIMEWA YOGYAKARTA, JAWA TIMUR, BANTEN |
| Sumatera | ACEH, SUMATERA UTARA, SUMATERA BARAT, RIAU, JAMBI, SUMATERA SELATAN, BENGKULU, LAMPUNG, KEPULAUAN RIAU, KEPULAUAN BANGKA BELITUNG |
| Kalimantan | KALIMANTAN BARAT, KALIMANTAN TENGAH, KALIMANTAN SELATAN, KALIMANTAN TIMUR, KALIMANTAN UTARA |
| Sulawesi | SULAWESI UTARA, SULAWESI TENGAH, SULAWESI SELATAN, SULAWESI TENGGARA, GORONTALO, SULAWESI BARAT |
| Eastern Indonesia | BALI, NUSA TENGGARA BARAT, NUSA TENGGARA TIMUR, MALUKU, MALUKU UTARA, PAPUA, PAPUA BARAT |

### Commodity Consolidation
```sql
CASE
  WHEN commodity IN ('Oil (vegetable)', 'Oil (vegetable, bulk)', 'Oil (vegetable, packaged)') THEN 'Cooking Oil'
  WHEN commodity IN ('Sugar', 'Sugar (premium)')  THEN 'Sugar'
  WHEN commodity = 'Rice'                          THEN 'Rice'
  WHEN commodity = 'Wheat flour'                   THEN 'Flour'
  ELSE NULL
END AS commodity_consolidated
```

---

## Data Traceability & Validation

Every pipeline run is tracked end-to-end for auditability and quality assurance.

### Pipeline Lineage Table (`pipeline.lineage`)
| Column | Type | Purpose |
|--------|------|---------|
| `run_id` | TEXT (PK) | Timestamp-based, generated per execution |
| `started_at` | TIMESTAMP | Pipeline start |
| `completed_at` | TIMESTAMP | Pipeline end |
| `ingest_status` | TEXT | `pending / running / completed / failed` |
| `transform_status` | TEXT | `pending / running / completed / failed` |
| `forecast_status` | TEXT | `pending / running / completed / failed` |
| `export_status` | TEXT | `pending / running / completed / failed` |
| `raw_food_prices_rows` | INT | Row count after raw load |
| `raw_markets_rows` | INT | Row count after raw load |
| `issues_log` | JSONB | Structured quality issue list per run |

`run_id` generated by `ingest/config.py:generate_run_id()` → `pipeline_YYYYMMDD_HHMMSS`.

### Per-Layer Row Count Reconciliation
```
CSV row count → raw table row count (must match)
raw table row count → staging row count (staging ≤ raw, filtered by date/quality)
staging row count → intermediate row count (intermediate ≤ staging, filtered by quality flags)
intermediate row count → mart row count (marts join/filter intermediate)
mart row count → JSON record count (export verification, must match)
```
All counts logged to per-phase log files and recorded in `pipeline.lineage`.

### Row-Level Quality Flags (`int_prices_normalised`)
| Flag | Description |
|------|-------------|
| `flag_price_le_zero` | price ≤ 0 |
| `flag_null_unit` | unit is NULL |
| `flag_non_target` | commodity_consolidated is NULL (excluded commodity) |
| `flag_aggregate` | priceflag = 'aggregate' |
| `flag_invalid_year` | year outside 2007–2024 (added per LEARNINGS.md §30) |

Flags are set during intermediate transformation and propagated to mart models. Downstream analysis always applies `WHERE filter_out = FALSE`. Composite `filter_out` = OR of all 5 flags — 2,116 rows pass for analytics (actual market price × target commodity × valid year).

### Forecast Validation (`forecast/run_forecast.py`)
Post-generation checks per commodity:
- **NaN check**: no NULL forecast values
- **Negative price check**: no forecast_price ≤ 0
- **CI reversal check**: lower_95 ≤ upper_95 for all rows

Failures logged to `logs/forecast.log` and `pipeline.lineage.forecast_status` set to `failed`.

### Export Verification (`export/export_json.py`)
Each exported JSON file is verified against its source mart model:
- `mart_price_trends` rows == `price_trends.json` records
- `mart_seasonal_patterns` rows == `seasonal_patterns.json` records
- `mart_geo_disparity` rows == `geographic_disparity.json` records
- `mart_commodity_correlation` rows == `commodity_correlation.json` records
- `mart_correlation_summary` rows == `correlation_summary.json` records
- `dashboard/public/data/forecast.json` copied from forecast output (819 records)

Mismatch sets `pipeline.lineage.export_status = 'failed'` and logs detailed counts.

---

## Dashboard Architecture

### Pages
| Page | Decision | Data Source |
|------|----------|-------------|
| 1 — Price Trends & Forecast | "Is now a good time to lock in bulk purchase contracts?" | `price_trends.json` + `forecast.json` |
| 2 — Seasonal Patterns | "When should we increase stock for each commodity?" | `mart_price_trends_national` (4 commodities) + `int_islamic_calendar` |
| 3 — Geographic Disparity | "Which island group offers the best sourcing price?" | `geographic_disparity.json` |
| 4 — Commodity Signals | "Which commodities to monitor as early warning indicators?" | `commodity_correlation.json` |

### Global Filters (across all pages)
- Commodity: Rice / Cooking Oil / Sugar / Flour / All
- Island Group: All / Java / Sumatera / Kalimantan / Sulawesi / Eastern Indonesia
- Year Range: 2007–2024 slider

### Page-Specific Controls
- Page 2: Seasonal driver toggle (Ramadan / Harvest / Year-End / All)
- Page 4: Lag selector (0 / 1 / 2 / 3 months)

---

## Key Conventions

- Snake_case for Python/SQL throughout (no TypeScript/JS in this stack)
- dbt: staging = light cleaning, intermediate = business logic, marts = final analytical shape
- Never mix actual and aggregate price flags in same analysis
- Java = 100 baseline for island group price index
- Islamic calendar lookup manually populated, source documented
- All marimo notebooks save as .py files (marimo's standard format)
- Forecast limitations footnote on every dashboard page with forecast data
- Period-over-period KPI deltas use same filter cohort (see LEARNINGS.md §28)
- Chart reference lines computed from displayed data, not full source (§27)

---

## Code Style

### Python/SQL
- Snake_case naming throughout
- Logging to `logs/` folder
- Error handling with try/except, log failures
- dbt models: one transformation per CTE, document rationale

### Vizro (Python)
- Pages are Pydantic `vm.Page(title=..., components=[...], controls=[...])` configs; multi-page via `vm.Dashboard(pages=[...])` and `Vizro().build(dashboard).run()`
- Cross-page filter state: every `vm.Filter` must set `show_in_url=True` to share state across pages in 0.1.50 (per §87, §89). URLs are ugly but battle-tested.
- Cross-filtering via `set_control` action: `<vm.Card>.actions = [vm.Action(function=set_island_filter)]` enables click-card-to-filter-other-charts (the primary migration justification)
- Advanced Plotly (`add_vline`, `add_vrect`, `go.Scatter(fill="toself")` for CI, `px.choropleth` with vendored GeoJSON) requires `custom_charts` registration: wrap as `@capture("graph")` function in `dashboard/charts/`, call as `vm.Graph(figure=fn(data_manager["mart_X"]))`
- DataFrames registered via `data_manager.register_data(name, lambda: load_fn())` for lazy load; `dashboard/data_access.py:load_mart()` is framework-agnostic and reused as-is
- Plotly figures: `go.Figure` with `layout.template="plotly_white"`; never `connectgaps=True` on time-series with quality-filtered gaps
- Built-in charts via `vizro.plotly.express` (line, bar, imshow, scatter); custom_charts only when advanced features needed
- Hugging Face Spaces entry: `app.py` exposing `vm.Dashboard` config; gunicorn target `app:app` (not Dash's `app:server`); port 7860; 2 workers; `--timeout 120`
- Performance: lambda-based data_manager defers DataFrame compute; `data_access.py` `lru_cache(maxsize=32)` reused
- Validate: `uv run python -c "from dashboard.app import dashboard; print(len(dashboard.pages))"` smoke test

### Marimo Notebooks
- Save as .py files (marimo's standard format)
- **PEP 723 header**: Every notebook starts with `# /// script` declaring `requires-python` + `dependencies` (marimo, duckdb, pandas, plotly, numpy, statsforecast)
- **Script mode detection**: Use `mo.app_meta().mode == "script"` to handle headless CLI vs interactive browser execution; always show widgets, change only data source in script mode
- **Cell naming**: Use descriptive function names (`def setup():`, `def data_load():`) not anonymous `__` — enables readable DAG visualization
- **One transformation per cell**: Split complex logic across cells, not one 80-line cell doing 5 things
- **No `if` cell guards**: Let the reactivity DAG handle execution order — don't wrap cells in `if training_results:` guards
- **No try/except for control flow**: Let errors surface naturally; use `mo.stop()` for graceful error states (DB failure, empty data)
- **`mo.stop()`** for graceful error states: `mo.stop(data is None, mo.md("Waiting for data..."))` — prevents raw tracebacks
- **`mo.persistent_cache`** for expensive queries: `@mo.persistent_cache` on DB query functions avoids re-execution
- **`mo.lazy()`** for deferred computation: `mo.lazy(lambda: expensive_query())` delays work until needed (e.g., tabs, scroll-into-view)
- **`mo.md()` + `return` ordering**: Final expression renders — ensure `mo.md()` is the last expression before `return`, not an intermediate statement
- **Underscore convention** (readability): Use `__` (double underscore) prefix for variables that must not appear in Marimo's reactive graph (e.g., `__c = duckdb.connect(...)`). Single `_` for loop variables (`for _i, _val in ...`). No prefix for normal locals that happen to be cell-only. This avoids the visual noise of underscore-prefixing everything while still preventing unintended cross-cell variable capture.
- **DB_PATH in notebooks**: Compute DuckDB path inside `setup()` cell via `Path(__file__)` and return as `PROJECT_DB_PATH`. Do NOT use module-level `__` prefixed variables — marimo filters `__` names from cell namespaces. Downstream cells receive it as a DAG parameter.
- **No `mo.state()` unless needed**: 99% of cases handled by reactivity reading `widget.value` across cells
- **No cross-cell mutations**: Create new objects via `items + [4]`, not `items.append(4)`
- Use `mo.md()` for markdown explanations
- Use `mo.ui` widgets for interactivity (dropdowns, sliders, tables)
- Use `mo.ui.plotly(fig)` for Plotly chart integration
- Also runnable headlessly: `uv run python analysis/eda.py`
- Validate with: `uvx marimo check <notebook.py>` before committing

---

## LSP Quality (Astral Toolchain)

**Global config:** `~/.config/opencode/opencode.json` — ruff + ty servers, ruff formatter.

### Tools
| Tool | Version | Purpose | Platform |
|------|---------|---------|----------|
| ruff | 0.15.15 | Linting + formatting (replaces flake8, isort, black) | Windows + WSL |
| ty | 0.0.43 (beta) | Type checking + IDE features (replaces mypy/pyright) | WSL only |

### Current Baseline (2026-06-04)
| Check | Count | Category | Actionable? |
|-------|-------|----------|-------------|
| ruff E501 | 98 | Line too long | No — markdown tables in `eda.py`, Plotly template strings in dashboard |
| ruff F821 | 11 | Undefined name | No — marimo cell scoping (variables exported via `return` across cells) |
| ruff E712 | 7 | `== True` comparison | Yes — should use `df[flag]` directly |
| ruff B905 | 5 | zip without `strict=` | Yes — add `strict=True` or `strict=False` |
| ruff F841 | 2 | Unused variable | Yes — remove `opacity` (kpi_sparklines.py:56), `cm` (seasonal_patterns.py:135) |
| **ty** unresolved-reference | 11 | Marimo scoping | No — cross-cell variables via `return` |
| **ty** missing-argument | 16 | Vizro components | No — ty beta sees default args as required |
| **ty** not-subscriptable | 7 | duckdb `fetchone()` | No — returns `Optional[tuple]`, always `[0]` in practice |
| **ty** unresolved-attribute | 3 | `marimo.App` | No — ty beta can't resolve marimo's dynamic exports |
| **ty** other | 10 | Various | No — framework interop (numpy/pandas, vizro) |

### Known False Positives (safe to ignore)
- **marimo cell scoping**: ty reports `unresolved-reference` for variables defined in `setup()` cell but used in downstream cells — marimo's `return` mechanism exports them across the reactive DAG
- **Vizro `missing-argument`**: ty beta doesn't see Vizro's Pydantic field defaults; all components work at runtime
- **duckdb `not-subscriptable`**: `conn.execute().fetchone()[0]` always returns a tuple; ty infers `None` from the Optional return type
- **`marimo.App`**: ty can't resolve marimo's `__all__` exports — marimo.App works at runtime

### When to Fix Manually
- E712 (`== True`): Replace with `df[flag]` for boolean column checks
- B905: Add `strict=False` to `zip()` where lengths are intentionally unequal
- F841: Remove unused variable assignments

---

## Known Limitations

| Limitation | Mitigation |
|------------|------------|
| Retail prices only, not wholesale | Directionally correct proxy; would request supplier pricing in real role |
| Coverage gaps in outer islands pre-2015 | Eastern Indonesia analysis restricted to 2015–2024 |
| Forecast accuracy degrades at 5–6 months | CI widens explicitly on dashboard; 1–2 month forecasts operationally reliable |
| No volume weighting | All markets equal weight; would weight by sourcing volume in production |
| 2022 structural break (cooking oil) | Model retrained on post-2022 data as robustness check |
| Rice/Sugar/Flour: no market-level `actual` prices in WFP data — only national avg (market_id=974) | `mart_commodity_correlation` provides all 4 at national level; `mart_price_trends_national` provides all 4 at national level for seasonal analysis (Page 2). **Page 3 (Geographic Disparity)** remains Cooking Oil only because province-level data is unavailable for Rice/Sugar/Flour. Page 2 (Seasonal Patterns) is **all 4 commodities at national level**; the island-disaggregated breakdown is Cooking Oil only — see `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` and LEARNINGS §99. |
| Forecast uses all price data (incl. `aggregate`) while dashboard plots `actual`-only | Explicitly documented in `forecast.json` metadata via `data_source_note` field |

---

## dbt Implementation Evaluation

Per dbt Labs' analytics engineering best practices, this project was audited across six dimensions. Summary below.

### DAG Architecture
```
raw schema → staging (view) → intermediate (view) → marts (table, JSON export)
```
- **Medallion layers**: Clean separation with clear responsibilities per layer
- **DRY**: Minor redundancy — `stg_food_prices` `WHERE price > 0` duplicates `int_prices_normalised` `flag_price_le_zero`
- **Dead config**: `vars.start_date` in `dbt_project.yml` defined but never referenced

### Test Coverage (33 total)
| Tier | Category | Tests | Status |
|------|----------|-------|--------|
| 1 | Structural Integrity | `unique` + `not_null` on PKs | ✅ |
| 1 | Foreign Key Integrity | `relationships` test | ⚠️ Added per audit |
| 2 | Data Quality | `accepted_values` on enums, `not_null` on critical cols | ✅ |
| 3 | Business Logic | `positive_values` on prices, `expression_is_true` invariants | ⚠️ Added per audit |
| 4 | Low Signal | Avoided unnecessary blanket `not_null` | ✅ |

**Critical fix applied**: Added `relationships` test on `stg_food_prices.market_id → stg_markets.market_id` (Tier 1 gap).

**Syntax verified**: dbt 1.11.11 requires `arguments:` key for generic tests. All 10 `accepted_values` + 1 `relationships` test confirmed using correct nested syntax.

### Documentation Quality
- Table descriptions that stated the obvious (`"Cleaned markets"`) rewritten to capture grain, edge cases, and business context
- Column descriptions that restated the name (`"Primary key"`) enriched with business rationale
- Source YAML column docs expanded from 5/15 to 13/15 columns for `food_prices`, 3/9 to 7/9 for `markets`

### Gaps Closed
| Gap | Fix |
|-----|-----|
| No `relationships` FK test on market_id | Added to `_staging__models.yml` |
| `vars.start_date` unused | Removed from `dbt_project.yml` |
| `ramadan_start` selected but unused | Removed from `int_islamic_calendar.sql` |
| `mart_commodity_correlation` 1/16 cols tested | Added `not_null` on all 4 price columns |
| No `packages.yml` | Added with `dbt_utils` v1.3.0 |
| No exposures defined | Added `_exposures.yml` mapping marts → dashboard pages |
| No seed YAML for `islamic_calendar` | Added `_seeds.yml` with column docs |
| Missing `unit` column test | Added `accepted_values` for known units |
| `filter_out` invariant not tested | Added singular test `assert_filter_out_consistency.sql` |

### Key Convention
- `mart_` prefix used consistently (not `dim_`/`fct_`) — aligns with project's analytical focus per LEARNINGS.md §53
- `_layer__models.yml` naming convention per LEARNINGS.md §51
- `generate_schema_name` macro provides multi-env isolation per LEARNINGS.md §55

---

## Testing Instructions

### Verify Linting & Formatting
```bash
ruff check .          # Must pass (E501/F821/E712/B905/F841 acceptable)
ruff format --check . # Must pass (no files would be reformatted)
```

### Verify dbt
```bash
cd transform
dbt build       # Run + test all models (staging → intermediate → marts)
dbt test        # All model tests must pass
dbt docs serve  # View lineage documentation
```

### Verify Forecast
```bash
uv run python forecast/run_forecast.py
# Check dashboard/public/data/forecast.json exists with all 4 commodities
```

### Verify Dashboard
```bash
uv run python -c "from dashboard.app import app; print(f'Pages: {len(app.layout.children)}')"
# DO NOT run: uv run python dashboard/app.py (blocks forever, human-use only)
```

---

## Success Criteria

1. Live Hugging Face Spaces URL — every page answerable in 60 seconds
2. Pipeline walkthrough covers 5 layers: ingest, dbt staging, dbt transform, forecasting, JSON export
3. Commodity naming inconsistency handled with specific dbt consolidation answer
4. Forecast reliability answered with nuance: model selection, CI, explicit limitations
5. README tells the full story in under 5 minutes
