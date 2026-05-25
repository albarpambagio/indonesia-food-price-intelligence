# AGENTS.md

## Project Overview

Indonesia Staple Food Price Intelligence — End-to-end data pipeline + forecasting + interactive dashboard for FMCG procurement teams. Tracks 17 years of WFP market price data across 4 staple commodities, 224 markets, and 5 island groups.

| Attribute | Detail |
|-----------|--------|
| **Dataset** | WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0) |
| **Source** | World Food Programme via Humanitarian Data Exchange |
| **Volume** | 325,240 price records + 224 markets |
| **Date Range** | January 2007 – May 2024 |
| **Stack** | Python → DuckDB → dbt → statsforecast → Marimo → Static JSON → Next.js (Shadboard) → Cloudflare Pages |
| **Phase 2 Status** | ✅ Complete (+ Phase 2.5 corrections: Ramadan flags, YoY delta, correlation summary) |
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

### Run Marimo Notebooks
```bash
uv run marimo edit analysis/data_validation.py          # Phase 0 — data validation
uv run marimo edit analysis/eda.py                      # Phase 4 — EDA (SCAN framework)
uv run marimo edit analysis/deep_dive.py                # Phase 5 — deep dive analysis
uv run marimo edit analysis/forecast_experimentation.py # Phase 3 — model selection (optional)
```

### dbt
```bash
cd transform
dbt seed             # Load seed data (islamic_calendar.csv)
dbt build            # Run + test all models in DAG order (staging → intermediate → marts)
dbt run              # Run all models (staging → intermediate → marts)
dbt test             # Run data tests (33 tests across all layers)
dbt docs generate    # Generate lineage docs
dbt docs serve       # Serve docs locally (default: http://localhost:8080)
dbt compile          # Compile SQL without running
dbt ls               # List models in project
```

### Forecasting
```bash
uv run python forecast/run_forecast.py   # PENDING — Phase 3
```

### Export + Dashboard
```bash
uv run python export/export_json.py   # PENDING — Mart models → static JSON
cd dashboard
npm install
npm run dev          # Development server
npm run build        # Static export for Cloudflare Pages
```

---

## Development Workflow

### Phase Pipeline
```
Phase 0: Setup + Data Validation  → Folder structure, marimo validation notebook, dbt/Next.js init
Phase 1: Ingest & Staging         → DuckDB raw load, dbt staging models + tests        ✅ DONE
Phase 2: Transform                → dbt intermediate + mart models + tests              ✅ DONE
Phase 2.5: Corrections            → Ramadan flags, YoY delta, correlation summary, lineage fix ✅ DONE
Phase 3: Forecasting              → statsforecast AutoARIMA/AutoETS + methodology doc
Phase 4: EDA                      → Marimo notebook (SCAN framework)                    ✅ DONE
Phase 5: Deep Dive                → Marimo notebook (North Star method)
Phase 6: Dashboard                → 4 pages in Next.js + Shadboard + Cloudflare Pages
Phase 7: Methodology Doc          → model_methodology.md
Phase 8: Write-up                 → README, insights log, recommendations
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
│   ├── eda.py                  # Phase 4 SCAN EDA (15 cells, 7 findings)
│   ├── deep_dive.py            # Phase 5 North Star deep dives
│   └── forecast_experimentation.py  # Phase 3 optional model comparison
├── seeds/                      # dbt seed data
│   └── islamic_calendar.csv    # Ramadan/Eid dates 2007–2024
├── dashboard/                  # Next.js + Shadboard app
│   ├── public/
│   │   └── data/               # Static JSON files
│   └── src/
│       └── app/
├── docs/
│   ├── data_validation.md
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
- `mart_corr_relation` rows == `commodity_correlation.json` records

Mismatch sets `pipeline.lineage.export_status = 'failed'` and logs detailed counts.

---

## Dashboard Architecture

### Pages
| Page | Decision | Data Source |
|------|----------|-------------|
| 1 — Price Trends & Forecast | "Is now a good time to lock in bulk purchase contracts?" | `price_trends.json` + `forecast.json` |
| 2 — Seasonal Patterns | "When should we increase stock for each commodity?" | `seasonal_patterns.json` |
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

## Shared Learnings (from Pharmacy Retail Sales project)

This project shares the same dashboard stack (Next.js + Shadboard + Recharts + TanStack Table + Cloudflare Pages) as the retail_sales project at `D:\PROJECT\data_analyst_porto\retail_sales\`. Key engineering patterns documented in LEARNINGS.md apply directly:

**Must-read sections before Phase 6 (Dashboard):**

| Section | Issue | Why It Matters Here |
|---------|-------|---------------------|
| §5 — Sidebar Disappearance | Pages outside route group don't inherit layout | 4 pages × route group — same Shadboard pattern |
| §6 — React Hooks Before Early Return | Hooks after `return` violate rules of 4 | Every page has loading state + memoized filters |
| §11 — DataProvider Pattern | Centralized JSON loading with shared cache | 5 JSON files to load across 4 pages |
| §19 — Filter Composition (No Mutation) | Sequential `if` blocks overwrite each other | 3 global filters × 4 pages = complex filter chain |
| §20 — Lazy Data Fetching | Don't load all 5 JSONs on every page | Download only what each page needs |
| §21 — Dynamic Imports | -45% bundle size via `next/dynamic` | Charts are heaviest components |
| §22 — sessionStorage Cache | Survive page reload without re-fetch | Same static JSON pattern |
| §25 — `connectNulls` Avoidance | False continuity in line charts | 17-year trend with potential gaps |
| §26 — Charts Must Respect Filters | Silent filter ignoring confuses users | Every chart must respond to all active filters |
| §28 — KPI Delta Same Cohort | Comparing different products across months | Filtered data deltas |
| §32 — Cache-Busting in Dev | Stale JSON in dev sessions | Regenerated JSON during development |
| §34 — Strip Shadboard Boilerplate | Dead code from starter kit | Same Shadboard cleanup needed |
| §35 — Cross-Tabulated Filter Data | Single-dimension fields can't compose | Multi-dimension filters need intersection fields |

**Full reference**: `D:\PROJECT\data_analyst_porto\retail_sales\docs\LEARNINGS.md` (35+ documented bugs & solutions)

---

## Key Conventions

- Snake_case for Python/SQL, camelCase for TS/JS
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

### TypeScript/React
- camelCase naming
- React Server Components by default, 'use client' only when needed
- Shadboard components from `@/components/ui/`
- Recharts for charts, TanStack Table for tables
- No `connectNulls` on line charts (see LEARNINGS.md §25)

### Marimo Notebooks
- Save as .py files (marimo's standard format)
- Use `mo.md()` for markdown explanations
- Use `mo.ui` widgets for interactivity (dropdowns, sliders)
- Use `mo.as_html(fig)` for Plotly/Altair chart integration
- Also runnable headlessly: `uv run python analysis/eda.py`

---

## Known Limitations

| Limitation | Mitigation |
|------------|------------|
| Retail prices only, not wholesale | Directionally correct proxy; would request supplier pricing in real role |
| Coverage gaps in outer islands pre-2015 | Eastern Indonesia analysis restricted to 2015–2024 |
| Forecast accuracy degrades at 5–6 months | CI widens explicitly on dashboard; 1–2 month forecasts operationally reliable |
| No volume weighting | All markets equal weight; would weight by sourcing volume in production |
| 2022 structural break (cooking oil) | Model retrained on post-2022 data as robustness check |
| Rice/Sugar/Flour: no market-level `actual` prices in WFP data — only national avg (market_id=974) | `mart_commodity_correlation` provides all 4 at national level; Pages 2/3 limited to Cooking Oil for geographic/seasonal analysis; documented on dashboard |

---

## Testing Instructions

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
cd dashboard
npm run build   # Must pass without errors
```

---

## Success Criteria

1. Live Cloudflare Pages URL — every page answerable in 60 seconds
2. Pipeline walkthrough covers 5 layers: ingest, dbt staging, dbt transform, forecasting, JSON export
3. Commodity naming inconsistency handled with specific dbt consolidation answer
4. Forecast reliability answered with nuance: model selection, CI, explicit limitations
5. README tells the full story in under 5 minutes
