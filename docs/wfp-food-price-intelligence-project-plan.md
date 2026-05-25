# Indonesia Food Price Intelligence — Project Plan

## Project Brief

| Attribute | Detail |
|-----------|--------|
| **Project Title** | Indonesia Staple Food Price Intelligence: A Procurement Analytics Tool for FMCG Companies |
| **Dataset** | WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0) |
| **Source** | World Food Programme via Humanitarian Data Exchange |
| **Volume** | 325,240 price records + 224 markets |
| **Date Range** | January 2007 – May 2024 (~17 years) |
| **Stack** | Python → DuckDB → dbt → statsforecast → Static JSON → Next.js (Shadboard) → Cloudflare Pages |
| **Portfolio Goal** | Demonstrate upgraded ETL pipeline (DuckDB + dbt), time-series forecasting, and multi-dimensional procurement analytics on real Indonesian data |

### Business Scenario

> *This dashboard was built for Procurement and Supply Chain Analysts at Indonesian FMCG companies. Rising input costs for staple commodities — rice, cooking oil, sugar, and flour — represent one of the largest margin risks for food manufacturers. This tool consolidates 17 years of WFP market price data into actionable procurement intelligence: when prices are trending, when seasonal spikes are coming, where geographic arbitrage opportunities exist, and which commodities signal risk for others.*

---

## Stakeholders

| Stakeholder | Primary Question | Detail Level |
|-------------|-----------------|--------------|
| **Procurement/Supply Chain Analyst** (primary) | When should I buy, from where, and how much? | High — needs market, commodity, trend, forecast |
| **Category Manager** (secondary) | Which categories are most exposed to price risk this quarter? | Medium — needs trend summary, forecast, seasonal flag |

---

## Target Commodities

| Commodity | Raw Names in Dataset | Normalisation Required |
|-----------|---------------------|----------------------|
| Rice | Rice | None |
| Cooking Oil | Oil (vegetable), Oil (vegetable, bulk), Oil (vegetable, packaged) | Consolidate to single "Cooking Oil" commodity |
| Sugar | Sugar, Sugar (premium) | Consolidate to single "Sugar" commodity — or keep split if price divergence is meaningful |
| Flour | Wheat flour | None |

> **Note:** Consolidation decisions for cooking oil and sugar must be documented in dbt model with explicit rationale. If Sugar vs Sugar (premium) shows meaningful price divergence, keep split and surface as an insight rather than collapsing it.

---

## Exec-Driven Questions

| # | Question | Primary Stakeholder | Page |
|---|----------|---------------------|------|
| 1 | How have staple commodity prices trended over 17 years — and what does the model forecast for the next 6 months? | Procurement Analyst, Category Manager | Page 1 |
| 2 | Which seasonal events (Ramadan, harvest cycles, year-end) cause the most predictable price spikes — and how far in advance do they occur? | Procurement Analyst | Page 2 |
| 3 | How large is the price gap between island groups, and which provinces consistently offer the lowest prices for each commodity? | Procurement Analyst | Page 3 |
| 4 | Which commodities lead others in price movement — and what does that mean for bundled procurement timing? | Category Manager, Procurement Analyst | Page 4 |

---

## North Star Definitions

| Element | Definition |
|---------|------------|
| **North Star Metric** | Monthly average retail price per commodity (IDR/KG or IDR/L, normalised) |
| **Primary Dimensions** | Commodity, island group, month/year |
| **Secondary Dimensions** | Province, market, priceflag (actual vs aggregate) |
| **Forecast Metric** | Predicted price ± 95% confidence interval, 6-month horizon |
| **North Star Goal** | Give procurement teams a 1–2 month lead time signal before price spikes |

---

## READY Framework Checklist

| Pillar | How This Project Satisfies It |
|--------|-------------------------------|
| **R — Representative Data** | 17 years of real WFP market price observations across 224 Indonesian markets. Messy unit variations, commodity name inconsistencies, actual vs aggregate price flags — real-world data engineering challenges |
| **E — Exec-Driven Questions** | Four questions tied directly to procurement timing, seasonal planning, geographic sourcing, and category risk management |
| **A — Analytical Frameworks** | CLEAN for data quality, dbt for transform layer documentation, statsforecast for modelling, SCAN for EDA, North Star Method for deep dives, DASH for dashboard |
| **D — Data Best Practices** | DuckDB star schema, dbt model lineage and tests, documented commodity normalisation decisions, priceflag filtering discipline, Islamic calendar lookup table |
| **Y — Your Insights & Impact** | Quantified seasonal lead times, geographic price differentials, cross-commodity lag relationships — all mapped to actionable procurement recommendations |

---

## Phase 0 — Project Setup & Data Validation Checkpoint

**Goal:** Establish scaffolding and validate dataset coverage before any pipeline work begins. Scoping decisions are confirmed here, not assumed.

### Tasks

- [ ] Create GitHub repository with folder structure (see below)
- [ ] Write business scenario and stakeholder brief in README
- [ ] Define North Star Metric, Dimensions, and Team Goals
- [ ] Document dataset source, license, and download instructions
- [ ] Install dependencies via `uv sync`
- [ ] Create `pyproject.toml` (uv-native dependency management)
- [ ] Initialise dbt project inside `/transform`
- [ ] Initialise Next.js app using Shadboard starter-kit inside `/dashboard`

### Data Validation Checkpoint

**Marimo notebook:** `analysis/data_validation.py` — interactive exploration for all 7 validation checks with visual summaries. Run via: `marimo edit analysis/data_validation.py`

**Run before Phase 1 begins. Document findings in `docs/data_validation.md`.**

| Check | Question | Decision Trigger |
|-------|----------|-----------------|
| Commodity coverage | Are rice, cooking oil, sugar, flour present consistently across all 17 years? | If any commodity missing before 2012, adjust analysis start date |
| Provincial coverage | Which provinces have continuous data? Which are sparse? | Determines island group vs province drill-down viability |
| Priceflag distribution | What % of records are actual vs aggregate? | If aggregate dominates, analysis must use aggregate — document this |
| Unit consistency | Are unit variations stable across years for each commodity? | Confirms normalisation approach |
| Sugar split decision | Does Sugar vs Sugar (premium) show meaningful price divergence? | Keep split or consolidate |
| Cooking oil split | Do three oil variants move together or diverge? | Keep split or consolidate |
| Secondary enrichment | Is BPS CPI or USD/IDR rate needed given usdprice already available? | usdprice column likely makes external FX enrichment redundant — confirm |

> **Note:** `usdprice` column already present in dataset — external USD/IDR enrichment is likely unnecessary. Confirm during validation checkpoint.

### Folder Structure

```
indonesia-food-price-intelligence/
├── data/
│   └── raw/                    # Original CSV files — never modified
│       ├── wfp_food_prices_idn.csv
│       └── wfp_markets_idn.csv
├── ingest/
│   └── load_raw.py             # Load CSVs into DuckDB staging tables
├── transform/                  # dbt project root
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/            # 1:1 with raw tables, light cleaning only
│   │   │   ├── stg_food_prices.sql
│   │   │   └── stg_markets.sql
│   │   ├── intermediate/       # Business logic, joins, normalisation
│   │   │   ├── int_prices_normalised.sql
│   │   │   ├── int_commodity_consolidated.sql
│   │   │   └── int_islamic_calendar.sql
│   │   └── marts/              # Final analytical models, one per dashboard page
│   │       ├── mart_price_trends.sql
│   │       ├── mart_seasonal_patterns.sql
│   │       ├── mart_geographic_disparity.sql
│   │       └── mart_commodity_correlation.sql
│   └── tests/                  # dbt data tests
│       ├── assert_price_positive.sql
│       └── assert_no_mixed_flags.sql
├── forecast/
│   └── run_forecast.py         # statsforecast models, outputs forecast JSON
├── export/
│   └── export_json.py          # Query mart models → static JSON files + verify row counts
├── analysis/                   # Marimo notebooks (.py files)
│   ├── data_validation.py      # Phase 0 validation checkpoint
│   ├── eda.py                  # Phase 4 SCAN EDA
│   ├── deep_dive.py            # Phase 5 North Star deep dives
│   └── forecast_experimentation.py  # Phase 3 optional model comparison
├── dashboard/                  # Next.js + Shadboard app
│   ├── public/
│   │   └── data/               # Static JSON files
│   │       ├── price_trends.json
│   │       ├── seasonal_patterns.json
│   │       ├── geographic_disparity.json
│   │       ├── commodity_correlation.json
│   │       └── forecast.json
│   └── src/
│       └── app/
├── docs/
│   ├── data_validation.md      # Phase 0 checkpoint findings
│   ├── issues_log.md
│   ├── insights_log.md
│   └── model_methodology.md   # Forecasting rationale and limitations
├── logs/
│   ├── ingest.log            # Raw data load + row counts
│   ├── transform.log         # dbt run + reconciliation
│   ├── forecast.log          # Forecast generation + validation
│   └── pipeline_run.log      # Orchestration summary + lineage updates
├── pyproject.toml         # uv-native dependency management
├── uv.lock                # Lockfile (auto-generated by uv sync)
├── requirements.txt       # Human-readable reference only
└── README.md
```

### Key Deliverable
`docs/data_validation.md` completed before any pipeline code is written. All scoping assumptions confirmed or revised.

---

## Phase 1 — Ingest & Staging

**Goal:** Load raw CSVs into DuckDB and create clean staging models in dbt. No business logic at this layer.

### 1.1 Ingest

**Script:** `ingest/load_raw.py`

- Load `wfp_food_prices_idn.csv` into DuckDB staging table `raw.food_prices`
- Load `wfp_markets_idn.csv` into DuckDB staging table `raw.markets`
- Log row counts for both tables on load
- Preserve raw data exactly — no transformations at ingest stage
- Create `pipeline.lineage` table for run tracking (run_id, status, row counts, issues_log)
- Generate timestamp-based run_id per pipeline execution

### 1.2 dbt Staging Models

**Staging layer principle:** One model per raw table. Light cleaning only — rename columns, cast types, no business logic.

**`stg_food_prices.sql`**

| Transformation | Rationale |
|---------------|-----------|
| Cast `date` to DATE type | Ensures consistent date handling downstream |
| Uppercase `admin1`, `admin2` | Normalise province/district name casing |
| Trim whitespace from `commodity`, `market` | Remove leading/trailing spaces |
| Cast `price` and `usdprice` to DECIMAL | Precision for financial calculations |
| Rename `priceflag` → `price_flag` | Snake case consistency |
| Filter out `price <= 0` | Flag in issues log, exclude from analysis |

**`stg_markets.sql`**

| Transformation | Rationale |
|---------------|-----------|
| Rename columns to snake_case | Consistency |
| Flag national average record (market_id = 974) | Explicit boolean `is_national_avg` |
| Cast coordinates to FLOAT | Geospatial consistency |

### 1.3 dbt Tests at Staging Layer

```yaml
# stg_food_prices
- not_null: [date, commodity, market_id, price, price_flag]
- accepted_values: price_flag → [actual, aggregate]
- accepted_values: pricetype → [Retail]
- positive_values: price

# stg_markets
- unique: market_id
- not_null: [market_id, market, admin1]
```

### Key Deliverable
Two clean staging models passing all dbt tests. Row counts validated against raw CSVs.

---

## Phase 2 — Transform (dbt Intermediate + Mart Models)

**Goal:** Apply all business logic in documented, testable dbt SQL models. This is the analytical engineering core of the project.

### 2.1 Intermediate Models

**`int_commodity_consolidated.sql`**
The most important intermediate model — resolves the multi-name commodity problem.

```sql
-- Commodity consolidation mapping
CASE
  WHEN commodity IN ('Oil (vegetable)', 'Oil (vegetable, bulk)', 
                     'Oil (vegetable, packaged)') THEN 'Cooking Oil'
  WHEN commodity IN ('Sugar', 'Sugar (premium)')  THEN 'Sugar'
  WHEN commodity = 'Rice'                          THEN 'Rice'
  WHEN commodity = 'Wheat flour'                   THEN 'Flour'
  ELSE NULL  -- Exclude non-target commodities
END AS commodity_consolidated
```

> **Decision point:** If data validation shows Sugar vs Sugar (premium) diverges meaningfully, revert this to keep both and surface the gap as Page 1 insight.

**`int_prices_normalised.sql`**
Handles unit normalisation and priceflag separation.

| Transformation | Logic |
|---------------|-------|
| Unit normalisation | All solid commodities → IDR/KG. Cooking oil → IDR/L. 385G condensed milk → excluded (not target commodity) |
| Priceflag separation | Create two views: `actual_prices` (market-level) and `aggregate_prices` (national average). Never mix in same analysis |
| Island group mapping | admin1 → island group lookup table (Java, Sumatera, Kalimantan, Sulawesi, Eastern Indonesia) |
| Monthly grain | Confirm all dates are 15th of month — truncate to month for aggregation |
| Row-level quality flags | Add boolean flags: `flag_price_le_zero`, `flag_null_unit`, `flag_non_target`, `flag_aggregate` — carried to mart models for data quality transparency |

**Island group lookup table:**

| Island Group | Provinces |
|-------------|-----------|
| Java | DKI JAKARTA, JAWA BARAT, JAWA TENGAH, DI YOGYAKARTA, JAWA TIMUR, BANTEN |
| Sumatera | ACEH, SUMATERA UTARA, SUMATERA BARAT, RIAU, JAMBI, SUMATERA SELATAN, BENGKULU, LAMPUNG, KEPULAUAN RIAU, BANGKA BELITUNG |
| Kalimantan | KALIMANTAN BARAT, KALIMANTAN TENGAH, KALIMANTAN SELATAN, KALIMANTAN TIMUR, KALIMANTAN UTARA |
| Sulawesi | SULAWESI UTARA, SULAWESI TENGAH, SULAWESI SELATAN, SULAWESI TENGGARA, GORONTALO, SULAWESI BARAT |
| Eastern Indonesia | BALI, NUSA TENGGARA BARAT, NUSA TENGGARA TIMUR, MALUKU, MALUKU UTARA, PAPUA, PAPUA BARAT |

**`int_islamic_calendar.sql`**
Lookup table mapping each year's Ramadan start and Eid al-Fitr date to the dataset's monthly grain. Used by `mart_seasonal_patterns`.

| Year | Ramadan Start | Eid al-Fitr | Months Before Eid (T-1, T-2, T-3) |
|------|--------------|-------------|-----------------------------------|
| 2007 | 2007-09-13 | 2007-10-13 | 2007-09, 2007-08, 2007-07 |
| 2008 | 2007-09-01 | 2008-10-01 | ... |
| ... | ... | ... | ... |
| 2024 | 2024-03-11 | 2024-04-10 | 2024-03, 2024-02, 2024-01 |

> Note: Islamic calendar regresses ~11 days per year. This table must be manually populated or sourced from a reliable Islamic calendar API. Document source in README.

### 2.2 Mart Models

**`mart_price_trends.sql`**
Feeds Page 1. Monthly average price per commodity per island group, plus national average. Output includes both IDR and USD prices.

**`mart_seasonal_patterns.sql`**
Feeds Page 2. Joins price data with Islamic calendar lookup. Calculates:
- Average price by commodity at T-3, T-2, T-1, T0 (Eid month), T+1 months relative to Eid
- Price index relative to annual average (100 = annual average, >100 = above average)
- Harvest season flags (March–April and August–September for rice)
- Year-end flag (November–December)

**`mart_geographic_disparity.sql`**
Feeds Page 3. Average price per commodity per island group per year. Calculates:
- Price index relative to Java baseline (Java = 100)
- Province-level detail where coverage is sufficient (from data validation checkpoint)
- Year-over-year change in disparity gap

**`mart_commodity_correlation.sql`**
Feeds Page 4. Monthly national average prices for all four commodities in wide format. Calculates:
- Cross-correlation at lags 0, 1, 2, 3 months for all commodity pairs
- Identifies strongest leading indicator pair per commodity
- Rolling 3-year correlation to detect relationship stability over time

### 2.3 dbt Tests at Mart Layer

```yaml
# All mart models
- not_null: [date, commodity_consolidated, price_idr]
- accepted_values: commodity_consolidated → [Rice, Cooking Oil, Sugar, Flour]
- positive_values: price_idr

# mart_geographic_disparity
- not_null: island_group
- accepted_values: island_group → [Java, Sumatera, Kalimantan, Sulawesi, Eastern Indonesia]
```

### Key Deliverable
Four mart models passing all dbt tests. dbt docs generated (`dbt docs generate`) — include lineage graph screenshot in README.

---

## Phase 3 — Forecasting

**Goal:** Generate 6-month price forecasts with confidence intervals for each target commodity using statsforecast. Output integrated into the static JSON pipeline.

### 3.1 Model Selection Rationale

| Model | Considered | Decision |
|-------|-----------|----------|
| AutoARIMA | Automatically selects ARIMA order, handles trends | **Primary candidate** |
| AutoETS | Error/Trend/Seasonality decomposition, strong for seasonal data | **Primary candidate** |
| AutoTheta | Simple, robust, good for noisy data | Backup if AutoARIMA/ETS overfit |
| Prophet | Handles holidays well but slower, less appropriate for monthly grain | Not used |

**Selection approach:** Run AutoARIMA and AutoETS for each commodity on national average prices. Compare AIC/BIC and cross-validation MAE on holdout period (last 12 months). Select best model per commodity — document in `docs/model_methodology.md`.

**Optional marimo notebook:** `analysis/forecast_experimentation.py` for interactive model comparison — AIC/BIC, cross-validation MAE across AutoARIMA, AutoETS, AutoTheta per commodity with live charting. Run via: `marimo edit analysis/forecast_experimentation.py`

### 3.2 Islamic Calendar as Exogenous Variable

Ramadan/Eid dates can be passed as external regressors to improve seasonal fit. Implement as binary flag columns in the training data:

```python
# Binary flags added to training data before model fit
df['is_ramadan_month'] = df['date'].isin(ramadan_months).astype(int)
df['is_eid_month'] = df['date'].isin(eid_months).astype(int)
```

### 3.3 Forecast Output Structure

**Script:** `forecast/run_forecast.py`

For each commodity:
- Train on full historical series (Jan 2007 – May 2024)
- Generate 6-month forecast (Jun 2024 – Nov 2024)
- Output: `{date, commodity, forecast_price, lower_95, upper_95, model_used}`
- **Validate**: check for NaN, negative prices, CI bounds reversal (lower > upper) — log issues to `logs/forecast.log`
- Update `pipeline.lineage.forecast_status` on completion

### 3.4 Model Limitations — Document Explicitly

These go in `docs/model_methodology.md` and are summarised in the dashboard:

| Limitation | Implication |
|------------|-------------|
| Government price controls (HET for cooking oil, rice) | Model cannot anticipate policy interventions — forecast assumes no structural breaks |
| Import tariff changes | Sudden tariff adjustments create step-changes the model treats as noise |
| El Niño / La Niña cycles | Drought effects on rice and sugar not captured without weather input data |
| Islamic calendar regression | AutoARIMA handles this imperfectly without explicit Ramadan regressors |
| Forecast horizon accuracy | 1–2 month forecasts more reliable than 5–6 month. Communicate confidence intervals clearly |

### Key Deliverable
`forecast.json` containing actuals + forecast + confidence intervals for all four commodities. `docs/model_methodology.md` completed.

---

## Phase 4 — EDA (SCAN Framework)

**Goal:** Surface high-level patterns, populate insights log, identify segments worth deep-diving. Run interactively in **`analysis/eda.py`** (marimo notebook) on mart model outputs.

### S — Stakeholder Goals
- Procurement Analyst: timing signals, geographic price gaps, seasonal early warnings
- Category Manager: category-level risk exposure, trend direction, forecast summary

### C — Coverage Gaps to Document

| Gap | Implication |
|-----|-------------|
| Sparse outer island coverage pre-2015 | Eastern Indonesia comparisons restricted to 2015–2024 |
| No volume/quantity data | Cannot weight prices by procurement volume |
| No competitor or supplier pricing | Cannot benchmark against actual procurement costs |
| Retail prices only | Wholesale prices (more relevant for FMCG) not available |
| Forecast ends Nov 2024 | Data ends May 2024 — 6-month forward window only |

### A — Aggregates to Run

| Analysis | Why |
|----------|-----|
| Annual average price per commodity (IDR) | Baseline trend direction |
| Year-over-year % change per commodity | Inflation rate per commodity |
| Price volatility (std dev / mean) per commodity | Which commodity is hardest to plan for |
| Island group price index vs Java baseline | Scale of geographic disparity |
| Month-of-year average price (all years pooled) | Visual seasonality check before formal analysis |
| Cross-commodity correlation matrix (lag 0) | Quick check before lag analysis |

### N — Notable Segments
Expected candidates based on dataset characteristics:
- Cooking oil — likely shows 2022 global shock (Russia-Ukraine + Indonesia export ban)
- Rice — likely shows harvest seasonality most clearly
- Sugar — likely shows strongest Ramadan effect
- Eastern Indonesia — likely shows largest and most persistent price premium

### Key Deliverable
Insights log with minimum 6 findings, each with: metric, dimension, finding (quantified), type (contextual/directional/actionable), stakeholder.

**Marimo-driven:** enables real-time filtering, chart iteration, and inline insight capture via reactive widgets (commodity selector, date range slider, island group dropdown). Findings directly populate insights log.

---

## Phase 5 — Deep Dive Analysis (North Star Method)

**Goal:** Answer all four exec-driven questions interactively in **`analysis/deep_dive.py`** (marimo notebook) with quantified, stakeholder-ready findings.

### Question 1 — Price Trends + Forecast

**Step 1:** Plot annual average price trend per commodity (2007–2024) — identify structural breaks (2008 food crisis, 2022 cooking oil shock)

**Step 2:** Decompose trend into: long-term trend + seasonal component + residual — use statsforecast's decomposition output

**Step 3:** Layer 6-month forecast with confidence interval — identify procurement action zone (when lower bound of forecast exceeds current price by X%)

**Expected insight pattern:**
> *"Cooking oil shows the highest 17-year price inflation at X% CAGR, with a structural break in early 2022 driven by the global supply shock and Indonesia's temporary export ban. The 6-month forecast suggests prices stabilising at Rp X,XXX/L ± Rp XXX (95% CI)."*

### Question 2 — Seasonal Patterns

**Step 1:** Align all years to Islamic calendar — plot commodity prices at T-3 to T+1 relative to Eid, overlaid across years

**Step 2:** Calculate average price premium at each T-window vs annual average — identify which commodity spikes earliest

**Step 3:** Run same analysis for harvest season (rice) and year-end — compare spike magnitude across seasonal drivers

**Expected insight pattern:**
> *"Sugar prices show the most consistent Ramadan premium — averaging X% above annual baseline in the month preceding Eid across 15 of 17 observed years. Rice prices show a harvest-season discount of Y% in March–April, offering a natural procurement window. Procurement teams should increase sugar and flour stock X weeks before Ramadan start."*

### Question 3 — Geographic Disparity

**Step 1:** Calculate island group price index vs Java baseline per commodity per year

**Step 2:** Identify which island group has largest persistent premium — and whether gap is narrowing or widening

**Step 3:** Province drill-down for island groups with sufficient coverage — identify lowest-cost provinces per commodity

**Expected insight pattern:**
> *"Eastern Indonesia carries a consistent X% premium over Java for rice, narrowing from Y% in 2007 to Z% in 2024 — suggesting improving inter-island logistics. For cooking oil, the gap has widened, likely reflecting distribution concentration in Java following the 2022 policy intervention."*

### Question 4 — Commodity Correlations & Leading Indicators

**Step 1:** Calculate cross-correlation for all commodity pairs at lags 0–3 months using national average prices

**Step 2:** Identify strongest leading relationship — which commodity predicts which, at what lag

**Step 3:** Calculate rolling 3-year correlation — is the relationship stable or did it break after 2022?

**Step 4:** Translate finding into procurement implication — "monitor commodity X as early warning for commodity Y"

**Expected insight pattern:**
> *"Rice prices show the strongest leading relationship with flour prices at a 2-month lag (r = X.XX), suggesting flour price movements are partially predictable from rice market conditions. This relationship held consistently pre-2022 but weakened during the global commodity shock — procurement teams should treat this signal as directional, not deterministic."*

### Insights Log Template

```
Finding #:
Metric:
Dimension:
Finding (quantified):
Type: Contextual / Directional / Actionable
Stakeholder:
Recommendation:
Confidence: High / Medium / Low + rationale
```

### Marimo Workflow

Each of the 4 deep dives is a marimo section in `analysis/deep_dive.py` with interactive widgets:

- Date range selector, commodity dropdown, island group dropdown
- Reactive charts (trend lines, seasonal overlay, geographic index, correlation matrix)
- Inline markdown cells for narrative and findings capture
- Also runnable headlessly: `python analysis/deep_dive.py` or interactively: `marimo edit analysis/deep_dive.py`

---

## Phase 6 — Dashboard (Shadboard + Next.js, DASH Framework)

**Goal:** Four-page procurement intelligence dashboard. Live public URL on Cloudflare Pages.

**Tech:** Next.js 15 + Shadboard + Recharts + TanStack Table. All data from static JSON files generated in Phase 3 export step.

### D — Decision Each Page Enables

| Page | Decision |
|------|----------|
| 1 — Price Trends & Forecast | "Is now a good time to lock in bulk purchase contracts for key commodities?" |
| 2 — Seasonal Patterns | "When should we increase stock for each commodity based on historical seasonal patterns?" |
| 3 — Geographic Disparity | "Which island group or province offers the best sourcing price right now?" |
| 4 — Commodity Signals | "Which commodities should we monitor as early warning indicators for others?" |

### A — Audience Per Page

| Page | Primary Audience | Secondary |
|------|-----------------|-----------|
| 1 | Category Manager | Procurement Analyst |
| 2 | Procurement Analyst | Category Manager |
| 3 | Procurement Analyst | — |
| 4 | Category Manager | Procurement Analyst |

### S — Signal: Key Components Per Page

**Page 1 — Price Trends & Forecast** (reads from `price_trends.json` + `forecast.json`)
- KPI cards: Current price per commodity (IDR/KG or IDR/L) + YoY change % + trend direction arrow
- Line chart: 17-year price history per commodity (Recharts LineChart, commodity selector toggle)
- Forecast extension: Dotted line continuation with shaded 95% confidence band (Jun–Nov 2024)
- Procurement action zone: Highlighted region when forecast lower bound > current price (buy signal)
- Model label: Small annotation showing which model was selected per commodity

**Page 2 — Seasonal Patterns** (reads from `seasonal_patterns.json`)
- Seasonal calendar heatmap: Month × commodity grid, cell color = avg price premium vs annual baseline
- Ramadan overlay chart: Price index (100 = annual avg) at T-3 to T+1 relative to Eid, all years overlaid
- Seasonal driver toggle: Switch between Ramadan, Harvest Season, Year-End views
- Lead time callout: "Average X weeks before Eid — stock up by [date]" — updated dynamically

**Page 3 — Geographic Disparity** (reads from `geographic_disparity.json`)
- Indonesia map: Choropleth by island group, color intensity = price premium vs Java baseline (Recharts + GeoJSON)
- Island group comparison bar chart: Price index per commodity per island group
- Province drill-down table: For selected island group, show province-level detail where coverage sufficient
- Year slider: Animate disparity change from 2007 to 2024
- Gap trend line: Java vs Eastern Indonesia price gap over time per commodity

**Page 4 — Commodity Signals** (reads from `commodity_correlation.json`)
- Correlation matrix heatmap: 4×4 commodity grid, cell = correlation coefficient at selected lag
- Lag selector: 0, 1, 2, 3 months — updates matrix on change
- Leading indicator callout: "Commodity X leads Commodity Y by N months (r = X.XX)" — strongest relationship highlighted
- Stability chart: Rolling 3-year correlation for top leading pair — shows if relationship held post-2022
- Procurement implication card: Plain-language translation of top finding for Category Manager audience

### H — Hierarchy Rules

- KPI cards always top row
- Most actionable chart above the fold on every page
- Color: Single accent for positive signals (buy opportunity), red for risk/spike warning, neutral grey otherwise
- Every page answerable in 60 seconds at a glance
- Model limitations footnote on Page 1 and Page 2 — small but present

### Global Filters (across all pages)
- Commodity (Rice / Cooking Oil / Sugar / Flour / All)
- Island Group (All / Java / Sumatera / Kalimantan / Sulawesi / Eastern Indonesia)
- Year Range slider (2007–2024)

### Deployment

| Step | Detail |
|------|--------|
| Build | `next build` with `output: 'export'` |
| Host | Cloudflare Pages — connect GitHub repo |
| Free tier | Unlimited bandwidth, global CDN, automatic HTTPS |
| Live URL | Pinned in README and GitHub repo description |

### Key Deliverable
Live Cloudflare Pages URL. Four pages fully functional. Screenshot previews in README.

---

## Phase 7 — Forecasting Methodology Documentation

**Goal:** `docs/model_methodology.md` that any analyst or hiring manager can read and understand.

### Required Sections

```
1. Problem Statement
   — What are we forecasting, at what grain, for what horizon?

2. Data Preparation
   — How training data was constructed (national average, actual prices only,
     monthly grain, Islamic calendar regressors)

3. Model Candidates Evaluated
   — AutoARIMA, AutoETS, AutoTheta — what each does, why considered

4. Model Selection Process
   — Cross-validation approach, holdout period, metric used (MAE, RMSE)
   — Final model selected per commodity with rationale

5. Confidence Intervals
   — What 95% CI means in plain language
   — How to interpret the procurement action zone

6. Known Limitations
   — Government price controls
   — Import tariff shocks
   — El Niño / weather effects
   — Islamic calendar regression approximation
   — "This model describes patterns in historical data — it does not predict policy"

7. How to Re-run
   — Step-by-step instructions to retrain model on updated data
```

### Key Deliverable
`docs/model_methodology.md` complete before dashboard goes live. Linked from README.

---

## Phase 8 — Insights, Recommendations & Write-up

**Goal:** Package everything into a hiring-manager-ready README and populated insights log.

### README Structure

```
1. Project Title & One-line Description
2. Live Dashboard URL (Cloudflare Pages — top of README, prominent)
3. Business Scenario (3–4 sentences)
4. Exec-Driven Questions (4 bullets)
5. Pipeline Architecture (flowchart diagram)
   Raw CSV → DuckDB (staging) → dbt (transform) → statsforecast → 
   export_json.py → Next.js Shadboard → Cloudflare Pages
6. dbt Lineage Graph (screenshot from dbt docs)
7. Key Findings (4–6 bullets, quantified)
8. Dashboard Preview (4 screenshots, one per page)
9. Recommendations (mapped to Procurement Analyst and Category Manager)
10. Data Limitations & Validation Checkpoint Findings
11. Forecasting Methodology (summary + link to full doc)
12. How to Reproduce (setup instructions)
13. Lessons Learned
```

### Three Insight Types to Document

| Type | Example |
|------|---------|
| Contextual | "Retail prices only — wholesale prices more relevant for FMCG procurement but not available in this dataset" |
| Directional | "Cooking oil shows a structural price break in 2022 that the model treats as a permanent level shift" |
| Actionable | "Sugar procurement should be completed X weeks before Ramadan — historically this is the last window before the spike exceeds Y%" |

---

## dbt Model Architecture

```
raw.food_prices          raw.markets
       │                      │
       ▼                      ▼
stg_food_prices          stg_markets
       │                      │
       └──────────┬───────────┘
                  ▼
     int_commodity_consolidated
     int_prices_normalised
     int_islamic_calendar
                  │
       ┌──────────┼──────────┬──────────┐
       ▼          ▼          ▼          ▼
mart_price   mart_seasonal  mart_geo   mart_corr
_trends      _patterns      _disparity _elation
       │          │          │          │
       └──────────┴──────────┴──────────┘
                  │
           export_json.py
           run_forecast.py
                  │
         dashboard/public/data/
              *.json files
```

---

## Interview Stories This Project Enables

| Interview Question | Answer From This Project |
|-------------------|--------------------------|
| "Walk me through your data pipeline." | Raw WFP CSV → DuckDB staging → dbt transform (staging → intermediate → mart) → statsforecast → static JSON → Shadboard dashboard. Each layer has a clear responsibility. Here's the lineage graph. |
| "Have you worked with dbt before?" | Yes — built a three-layer dbt project with staging, intermediate, and mart models. Wrote schema tests for null checks, accepted values, and positive price validation. Generated lineage documentation. |
| "Tell me about a time you had to make a data cleaning decision." | The commodity normalisation problem — cooking oil appeared as three separate commodity names. I documented the consolidation decision in dbt with explicit rationale and added a dbt test to ensure no unexpected commodity names reached the mart layer. |
| "Have you done any forecasting work?" | Yes — used statsforecast AutoARIMA and AutoETS on 17 years of Indonesian commodity price data. Selected model per commodity via cross-validation on a 12-month holdout. Documented limitations explicitly — the model cannot anticipate government price controls or import policy shocks. |
| "How do you communicate uncertainty in analysis?" | Forecast confidence intervals are shown as shaded bands on the dashboard. The model methodology document explains what 95% CI means in plain language. A limitations footnote appears on every forecast-related page. |
| "Why is this relevant to our business?" | Every Indonesian FMCG company buying rice, cooking oil, sugar, or flour faces the same input cost volatility this dashboard tracks. The seasonal lead time findings directly translate to procurement planning calendars. |

---

## Known Limitations to Pre-empt in Interviews

| Limitation | How to Address It |
|------------|-------------------|
| Retail prices, not wholesale | "Retail is a proxy — directionally correct but procurement teams would want wholesale pricing for exact cost modelling. I'd request supplier pricing data in a real role." |
| Coverage gaps in outer islands pre-2015 | "Documented in data_validation.md. Eastern Indonesia analysis restricted to 2015–2024 where coverage is sufficient." |
| Forecast horizon accuracy degrades at 5–6 months | "Confidence intervals widen significantly beyond 3 months — shown explicitly on dashboard. 1–2 month forecasts are operationally reliable, 5–6 month are directional only." |
| No volume weighting | "All markets weighted equally. In a real procurement context you'd weight by your sourcing volume per region." |
| 2022 structural break | "The cooking oil shock creates a structural break that ARIMA handles imperfectly. The model was retrained on post-2022 data as a robustness check — documented in methodology." |

---

## Timeline Estimate

| Phase | Estimated Time |
|-------|---------------|
| Phase 0 — Setup + Data Validation Checkpoint | 1 day |
| Phase 1 — Ingest & Staging | 1 day |
| Phase 2 — dbt Transform (Intermediate + Mart) | 4–5 days |
| Phase 3 — Forecasting | 2 days |
| Phase 4 — EDA | 1–2 days |
| Phase 5 — Deep Dive Analysis | 2–3 days |
| Phase 6 — Dashboard + Deployment | 3–4 days |
| Phase 7 — Methodology Documentation | 1 day |
| Phase 8 — Write-up + README | 1 day |
| **Total** | **~16–20 days** |

> Note: Longer than the pharmacy project by design — this is a more complex analytical problem. Build project 1 to completion first before starting.

---

## Success Criteria

This project is done when a hiring manager can:

1. Click the live Cloudflare Pages URL and find a procurement-relevant answer on every page within 60 seconds
2. Ask "walk me through your pipeline" and receive a confident answer covering all five layers: ingest, dbt staging, dbt transform, forecasting, and JSON export
3. Ask "how did you handle the commodity naming inconsistency?" and receive a specific answer about the dbt consolidation model and its tests
4. Ask "how reliable is your forecast?" and receive a nuanced answer covering model selection, confidence intervals, and explicit limitations
5. Read the README in under 5 minutes and understand the business scenario, pipeline architecture, and top findings without needing to open the dashboard
