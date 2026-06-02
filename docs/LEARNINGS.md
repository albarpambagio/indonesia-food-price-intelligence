# Engineering Learnings

This document captures key technical learnings, bugs encountered, and solutions discovered during the Pharmacy Retail Sales Analytics dashboard development.

---

## Table of Contents

| # | Section |
|---|---------|
| 1 | [Dashboard Architecture & Routing](#1-dashboard-architecture--routing) |
| 2 | [Data Fetching & Caching](#2-data-fetching--caching) |
| 3 | [Component Loading States](#3-component-loading-states) |
| 4 | [Build & Development Issues](#4-build--development-issues) |
| 5 | [Sidebar Disappearance Bug](#5-sidebar-disappearance-bug) |
| 6 | [React Hooks Rules Violation](#6-react-hooks-rules-violation) |
| 7 | [Array.filter() Does Not Mutate In Place](#7-arrayfilter-does-not-mutate-in-place) |
| 8 | [Global Filter Pattern Across Pages](#8-global-filter-pattern-across-pages) |
| 9 | [KPI Cards Should Reflect Filtered Data](#9-kpi-cards-should-reflect-filtered-data) |
| 10 | [Quick Reference](#10-quick-reference) |
| 11 | [React Context for Centralized Data Loading](#11-react-context-for-centralized-data-loading) |
| 12 | [Debounced Slider Pattern](#12-debounced-slider-pattern) |
| 13 | [Scatter Chart Data Sampling](#13-scatter-chart-data-sampling-for-large-sku-sets) |
| 14 | [Threshold-Driven Visual Styling](#14-threshold-driven-visual-styling-not-data-filtering) |
| 15 | [Pagination with Smart Ellipsis](#15-pagination-with-smart-ellipsis) |
| 16 | [QA Audit: setState Inside useMemo](#16-qa-audit-setstate-inside-usememo-causes-re-render-loops) |
| 17 | [ETL Pipeline: Row-by-Row INSERT vs Batch Insert](#17-etl-pipeline-row-by-row-insert-vs-batch-insert) |
| 18 | [ETL Pipeline: DROP TABLE vs TRUNCATE](#18-etl-pipeline-drop-table-vs-truncate-for-idempotent-loads) |
| 19 | [Filter Composition: Avoid Mutating Source Data](#19-filter-composition-avoid-mutating-source-data) |
| 20 | [Lazy Data Fetching: Hybrid Approach](#20-lazy-data-fetching-hybrid-approach-with-react-context) |
| 21 | [Dynamic Imports with next/dynamic](#21-dynamic-imports-with-nextdynamic) |
| 22 | [sessionStorage Cache Persistence](#22-sessionstorage-cache-persistence) |
| 23 | [CSV Export: Proper Field Quoting](#23-csv-export-proper-field-quoting) |
| 24 | [Exception Handling: Uninitialized Variable](#24-exception-handling-uninitialized-variable-in-error-handler) |
| 25 | [`connectNulls=true` Creates False Continuity](#25-connectnullstrue-creates-false-continuity-in-line-charts) |
| 26 | [Charts Must Respect Active Filter Scope](#26-charts-must-respect-active-filter-scope) |
| 27 | [Median Lines Must Match Displayed Data](#27-median-lines-must-match-displayed-data) |
| 28 | [KPI Delta Must Compare Same Cohort Over Time](#28-kpi-delta-must-compare-same-cohort-over-time) |
| 29 | [Silent Error Swallowing in DataProvider](#29-silent-error-swallowing-in-dataprovider) |
| 30 | [Missing Year Validation in NO_RESEP Parser](#30-missing-year-validation-in-no_resep-parser) |
| 31 | [Division by Zero in KPI Delta Calculation](#31-division-by-zero-in-kpi-delta-calculation) |
| 32 | [Cache-Busting Query Param for Development](#32-cache-busting-query-param-for-development) |
| 33 | [Visible Disclaimer for Charts That Can't Be Filtered](#33-visible-disclaimer-for-charts-that-cant-be-filtered) |
| 34 | [Strip Template Boilerplate Before Deploy](#34-strip-template-boilerplate-before-deploy) |
| 35 | [Cross-Tabulated Data for Multi-Dimension Filters](#35-filter-composition-cross-tabulated-data-required-for-multi-dimension-filters) |
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
| 79 | [LEARNINGS.md Patterns Are Stack-Specific — Switching Means Losing the Knowledge Base](#79-learningsmd-patterns-are-stack-specific--switching-means-losing-the-knowledge-base) |
| 80 | [Chart Engine Parity Between EDA and Dashboard Saves Migration Cost](#80-chart-engine-parity-between-eda-and-dashboard-saves-migration-cost) |
| 81 | [Dash Pages Routing: `dash.register_page` + `use_pages=True`](#81-dash-pages-routing-dashregister_page--use_pagestrue) |
| 82 | [DuckDB Read-Only Connections + `@functools.lru_cache` for Dashboard Data Access](#82-duckdb-read-only-connections--functoolslru_cache-for-dashboard-data-access) |
| 83 | [`dcc.Store` for Cross-Page Filter State (Alternative: Query String)](#83-dccstore-for-cross-page-filter-state-alternative-query-string) |
| 84 | [HF Spaces Docker Packaging: Port 7860, `gunicorn`, Layer Optimization](#84-hf-spaces-docker-packaging-port-7860-gunicorn-layer-optimization) |
| 85 | [Callback Output Declaration: All Outputs Must Be Declared in Signature](#85-callback-output-declaration-all-outputs-must-be-declared-in-signature) |
| 86 | [Plotly Figure Specs Port Verbatim from Marimo EDA to Dash `dcc.Graph`](#86-plotly-figure-specs-port-verbatim-from-marimo-eda-to-dash-dccgraph) |

---

## 1. Dashboard Architecture & Routing

### How Next.js Route Groups Work

Next.js App Router uses folder structure to determine layouts and page hierarchy. Route groups, denoted by parentheses like `(dashboard-layout)`, allow grouping routes without affecting the URL path.

```
src/app/
├── (dashboard-layout)/
│   ├── layout.tsx      # Shared layout (sidebar, header)
│   ├── page.tsx       # / (overview page)
│   └── products/
│       └── page.tsx   # /products
├── layout.tsx          # Root layout (providers, fonts)
└── globals.css
```

### The Gotcha: Layout Inheritance

**Problem:** The sidebar was missing on the `/products` page while appearing correctly on `/`.

**Root Cause:** The `products` folder was created at `app/products/` instead of inside `app/(dashboard-layout)/`. Pages outside a route group do not inherit the parent layout.

**Solution:**
```bash
# Wrong structure (before)
app/
├── products/page.tsx        # No layout inheritance
└── (dashboard-layout)/page.tsx  # Has layout

# Correct structure (after)
app/
└── (dashboard-layout)/
    ├── page.tsx             # / with sidebar
    └── products/page.tsx   # /products with sidebar
```

**Command to fix:**
```powershell
Move-Item -Path "app\products" -Destination "app\(dashboard-layout)\products"
```

---

## 2. Data Fetching & Caching

### The Problem

Initial page navigation took 18+ seconds, and subsequent page switches took 1-2 seconds despite using static JSON files.

**Observed timings:**
- First `/`: 18.4s (5390 modules compiled)
- First `/products`: 1.7s (reused compiled modules)
- Subsequent navigations: 1-2s

**Root Cause:** Each page navigation triggered a fresh `fetch()` call to load JSON data from `/public/data/`. Even though the files were local, the browser still made HTTP requests.

### Solution: In-Memory Cache

Added a simple cache object in `lib/data.ts` to store fetched data in memory:

```typescript
// src/lib/data.ts
const dataCache: Record<string, unknown> = {}

export async function getOverviewData(): Promise<OverviewData> {
  if (dataCache.overview) {
    return dataCache.overview as OverviewData
  }
  const res = await fetch("/data/overview.json")
  if (!res.ok) throw new Error("Failed to fetch overview data")
  const data = await res.json()
  dataCache.overview = data
  return data
}

export async function getProductsData(): Promise<ProductsData> {
  if (dataCache.products) {
    return dataCache.products as ProductsData
  }
  const res = await fetch("/data/products.json")
  if (!res.ok) throw new Error("Failed to fetch products data")
  const data = await res.json()
  dataCache.products = data
  return data
}
```

### Result

After implementing the cache:
- First load: 18s (compilation overhead, unavoidable)
- Subsequent navigations: **15-31ms**

### Why Not React Query?

For this use case, React Query would add unnecessary complexity. The data:
- Is static (never changes during a session)
- Is small (< 1MB JSON files)
- Only needs to be fetched once per session

A simple in-memory cache is the right tool for this job.

---

## 3. Component Loading States

### The Problem: "About This Dashboard" Not Clickable

When clicking "About This Dashboard" on Page 2 (Product Performance), nothing happened. After a few seconds, it started working.

**Investigation:** The component used `useState(false)` and toggled on click. Code looked correct.

**Root Cause:** The Interpretation Guide component was not rendered during the loading state. The page followed this pattern:

```typescript
if (loading) {
  return <skeleton placeholders />
}

return (
  <div>
    <InterpretationGuide />  {/* Only rendered AFTER loading completes */}
  </div>
)
```

During the loading phase (1-2 seconds), the component did not exist in the DOM. Clicks were ignored because there was nothing to click on.

### Solution: Render Skeleton During Loading

Updated the loading state to match the full page structure, including a skeleton for the Interpretation Guide:

```typescript
if (loading) {
  return (
    <div className="container p-4 space-y-6">
      {/* ... other skeletons ... */}
      <Skeleton className="h-12 w-full" />
    </div>
  )
}
```

Now the component is in the DOM immediately and is clickable as soon as the page renders, even while data is loading.

---

## 4. Build & Development Issues

### CSS 404 Errors on Page Switch

**Error:**
```
GET /_next/static/css/app/layout.css?v=... 404
```

**Root Cause:** Stale `.next` cache from previous development sessions. The dev server referenced CSS files that no longer existed after code changes.

**Solution:**
```powershell
# Stop dev server (Ctrl+C)
Remove-Item -Recurse -Force .next
npm run dev
```

**Prevention:** Clear `.next` whenever you see persistent 404 errors after making structural changes to the app.

---

### Recharts Tooltip Formatter Type Error

**Error:**
```
Type '(value: number) => [string, string]' is not assignable to type 'Formatter<ValueType, NameType>'
```

**Root Cause:** Recharts' Tooltip `formatter` prop expects a specific function signature that TypeScript couldn't verify as compatible with `number`.

**Solution:** Remove explicit type annotation and use type coercion:

```typescript
// Before (error)
<Tooltip formatter={(value: number) => [formatCurrency(value), "Revenue"]} />

// After (works)
<Tooltip formatter={(value) => [formatCurrency(Number(value) || 0), "Revenue"]} />
```

**Files affected:**
- `components/page2/monthly-trend-chart.tsx`
- `components/page2/revenue-bar-chart.tsx`
- `components/page2/scatter-chart.tsx`

---

### Prettier Formatting Failures

After writing new components, build failed due to Prettier formatting rules.

**Solution:** Run auto-format before build:
```bash
cd dashboard
npx prettier --write "src/components/page2/**" "src/app/products/**"
```

**Prevention:** Configure editor to format on save, or run Prettier as part of pre-commit hooks.

---

## 5. Sidebar Disappearance Bug

Documented in Section 1 above. Summary:

| Aspect | Detail |
|--------|--------|
| Symptom | Sidebar present on `/` but missing on `/products` |
| Root Cause | Page folder outside route group |
| Solution | Move `app/products` into `app/(dashboard-layout)/products` |
| Files Changed | Moved entire `products/` folder |

---

## 6. React Hooks Rules Violation

### The Problem

Build failed with error:
```
React Hook "useMemo" is called conditionally. React Hooks must be called in the exact same order in every component render.
```

**Root Cause:** The `useMemo` hook for filtered data was placed AFTER an early `return` statement (loading state check). React hooks must always be called in the same order on every render.

**Wrong pattern:**
```typescript
if (loading) {
  return <Skeleton />  // Early return
}

const filtered = useMemo(() => { ... }, [data])  // Hook AFTER return — VIOLATION
```

**Correct pattern:**
```typescript
const filtered = useMemo(() => { ... }, [data])  // Hook BEFORE any return

if (loading) {
  return <Skeleton />
}
```

**Rule:** All React hooks (`useState`, `useMemo`, `useEffect`, etc.) must be called at the top level of the component, before any conditional returns.

---

## 7. Array.filter() Does Not Mutate In Place

### The Problem

Filters on Page 2 were not working — selecting a filter had no effect on the displayed data.

**Root Cause:** The `.filter()` method returns a NEW array. The original code called `.filter()` but never assigned the result:

```typescript
// Bug — filter result discarded
productTypeRevenue.filter((p) => p.product_type === filterType)
monthlyTrend.filter((m) => m.product_type === filterType)
```

**Solution:** Assign the filtered result back to the variable:
```typescript
productTypeRevenue = productTypeRevenue.filter((p) => p.product_type === filterType)
monthlyTrend = monthlyTrend.filter((m) => m.product_type === filterType)
```

**Key takeaway:** `Array.filter()`, `Array.map()`, `Array.sort()` all return NEW arrays. They do NOT mutate the original. Always capture the return value.

---

## 8. Global Filter Pattern Across Pages

### Architecture

Global filters (Month, Transaction Type, Product Type) are implemented per-page with local state and `useMemo` filtering. Each page:

1. Declares filter state: `useState("all")` for each filter dimension
2. Renders `<OverviewFilters />` component for the filter UI
3. Uses `useMemo` to compute filtered data from raw data + filter states
4. Passes filtered data to all child components (charts, tables, KPI cards)

### Data Requirements

For filters to work, the JSON data must include the necessary breakdown fields:

| Filter | Required Data Fields |
|--------|---------------------|
| Month | `year_month` in each data row |
| Transaction Type | `transaction_type` or `revenue_outpatient`/`revenue_inpatient` |
| Product Type | `product_type` or `revenue_generic`/`revenue_branded` |

### ETL Updates Required

When adding new filter dimensions, the ETL export must be updated to include the necessary fields:

```python
# overview.json — added product type breakdown
SUM(f.revenue) FILTER (WHERE p.product_type = 'Generic')::float AS revenue_generic,
SUM(f.revenue) FILTER (WHERE p.product_type = 'Branded')::float AS revenue_branded

# products.json — added transaction type breakdown
SELECT p.product_type, t.transaction_type, SUM(f.revenue) ...
GROUP BY p.product_type, t.transaction_type
```

---

## 9. KPI Cards Should Reflect Filtered Data

### The Pattern

KPI cards must derive their values from the **filtered** dataset, not the raw data. This ensures that when users apply filters, the summary numbers update accordingly.

**Correct pattern:**
```typescript
const filtered = useMemo(() => { /* apply filters */ }, [data, month, productType])
const displayData = filtered || data

// Cards use displayData, not raw data
const total = displayData.product_type_revenue.reduce(...)
```

**Cards should be simple:**
- Show the aggregated total that reflects current filter state
- Avoid redundant breakdowns that duplicate what charts already show
- Let the charts and tables provide the detailed breakdown

---

## 10. Quick Reference

### Common Commands

| Issue | Command |
|-------|---------|
| Clear stale cache | `Remove-Item -Recurse -Force .next` |
| Auto-fix formatting | `npx prettier --write "src/**/*.{ts,tsx}"` |
| Rebuild | `npm run build` |
| Start dev server | `npm run dev` |

### Debugging Checklist

When encountering issues:

1. **Clear `.next` cache** — most mysterious dev server issues are cache-related
2. **Check folder structure** — ensure pages are in the correct route group for layout inheritance
3. **Verify component is rendered** — check if the component exists in DOM during the problematic state
4. **Check browser console** — network errors, React errors
5. **Check server terminal** — build errors, compilation messages

---

## 11. React Context for Centralized Data Loading

### The Problem

Each page fetched its own JSON data independently via `fetch()` in a `useEffect`. This meant:
- Page 1 loaded `overview.json`
- Page 2 loaded `products.json`
- Page 3 would load `margin_risk.json`

Each page had its own loading state, error handling, and data-cache boilerplate — duplicated code and no shared loading state.

### Solution: DataProvider + useData() Hook

Created a centralized `DataProvider` at the root layout level that loads all 3 datasets simultaneously via `Promise.all`:

```typescript
// src/contexts/data-context.tsx
useEffect(() => {
  let cancelled = false

  Promise.all([
    getOverviewData().catch((e) => { if (!cancelled) setError(e.message); return null }),
    getProductsData().catch(() => null),
    getMarginRiskData().catch(() => null),
  ]).then(([ov, pr, mr]) => {
    if (!cancelled) setState({ overview: ov, products: pr, marginRisk: mr })
  })

  return () => { cancelled = true }
}, [])
```

Pages then consume via `useData()`:

```typescript
const { overview, products, marginRisk, loading } = useData()
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `Promise.all` over sequential | All 3 datasets are independent — parallel fetch is faster |
| `cancelled` flag | Prevents setState after unmount (no "can't perform React state update" warning) |
| Per-fetch `.catch()` | One dataset failing doesn't block the others — partial data still renders |
| Shared `loading` | True only when ALL datasets are null; individual datasets can be partially loaded |

### Result

- One `useEffect` call instead of 3
- Shared loading state across pages
- Single error boundary point
- Pages are simpler — just consume context

---

## 12. Debounced Slider Pattern

### The Problem

The margin threshold slider fires `onValueChange` on every tick. Without debouncing, every tick triggers:
1. Re-filtering all SKUs by threshold
2. Re-computing scatter chart data (including sampling logic)
3. Re-rendering charts and table

At 30 possible slider positions, this is fine. But the slider emits values on `mousemove` — potentially dozens of events per second as the user drags.

### Solution: useDebounce Hook

```typescript
// src/hooks/use-debounce.ts
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}
```

In Page 3:

```typescript
const [threshold, setThreshold] = useState(10)
const debouncedThreshold = useDebounce(threshold, 120)

// Derived data only depends on debounced value
const atRiskSKUs = useMemo(() =>
  filteredSkus.filter(s => s.avg_margin_pct < debouncedThreshold),
  [filteredSkus, debouncedThreshold]
)
```

### How It Works

| Layer | Updates When | Purpose |
|-------|-------------|---------|
| `threshold` (raw state) | Every slider tick | Instant UI feedback (badge shows current value) |
| `debouncedThreshold` (derived) | 120ms after last change | Expensive filtering, chart rendering |

### Result

- Slider feels responsive (badge updates immediately)
- Chart data recomputes only after the user stops dragging for 120ms
- Avoids jank during fast slider drags

---

## 13. Scatter Chart Data Sampling for Large SKU Sets

### The Problem

The scatter chart (Volume vs Margin %) plots all 2,232 SKUs. Recharts ScatterChart with 2,000+ SVG elements causes:
- Slow initial render (2-3 seconds)
- Laggy tooltip hover
- Large DOM size (hundreds of KB)

### Solution: Smart Sampling with Top-K Preservation

```typescript
const MAX_POINTS = 500
const needsSampling = validData.length > MAX_POINTS

const sourceData = needsSampling
  ? (() => {
      const topSKUs = validData.slice(0, 200)        // Top 200 by revenue
      const remaining = validData.slice(200)
      const step = Math.ceil(remaining.length / (MAX_POINTS - 200))
      return [...topSKUs, ...remaining.filter((_, i) => i % step === 0)]
    })()
  : validData
```

### Strategy Rationale

| Group | Count | Why Preserve |
|-------|-------|-------------|
| Top 200 SKUs by revenue | 200 | High-revenue SKUs are the most important to see |
| Every nth remaining | ~300 | Representative sample of the long tail |
| **Total** | **~500** | Below Recharts perf threshold |

### Result

- Chart renders in < 200ms
- Tooltip works smoothly
- All high-value SKUs visible
- "Showing X of Y SKUs (sampled)" label prevents misinterpretation

---

## 14. Threshold-Driven Visual Styling (Not Data Filtering)

### The Pattern

The global filters (Month, Transaction Type, Product Type) use `useMemo` to **subset the data** — rows are included or excluded.

The threshold slider works differently: it controls **visual properties** (color, fill) based on threshold comparison, without removing any data points.

### Scatter: Dot Color

```typescript
for (const s of sourceData) {
  const point = { ...s, margin: s.avg_margin_pct }
  if (s.avg_margin_pct < threshold) {
    atRisk.push(point)   // Red dots
  } else {
    safe.push(point)     // Gray dots
  }
}

<Scatter data={safe} fill="#94a3b8" fillOpacity={0.4} />
<Scatter data={atRisk} fill="#ef4444" fillOpacity={0.6} />
```

### Histogram: Three-Tier Bar Coloring

```typescript
const fill = isBelow ? "#ef4444"        // Red — entirely below threshold
  : crossesThreshold ? "#f59e0b"        // Amber — crosses threshold
  : "#94a3b8"                           // Gray — above threshold
```

### Key Difference from Global Filters

| Aspect | Global Filters | Threshold Slider |
|--------|---------------|-----------------|
| What changes | Data rows passed to components | Visual properties (color, fill) |
| Data loss? | Yes — filtered rows excluded | No — all data visible |
| UX message | "Show me only X" | "Highlight SKUs below Y%" |
| Implementation | `useMemo` filtering | Color assignment in render |

This is important: the slider never hides data. The scatter always shows all SKUs, and the histogram always shows all 30 bins. Only the coloring changes.

---

## 15. Pagination with Smart Ellipsis

### The Problem

The at-risk SKU table can have 1 to 100+ pages (25 per page). Showing `[1][2][3]...[99][100]` with all intermediate numbers is:
- DOM-heavy (100+ button elements)
- Visually noisy
- Hard to navigate

### Solution: Smart Page Number Filtering

```typescript
Array.from({ length: totalPages }, (_, i) => i + 1)
  .filter((p) => {
    if (totalPages <= 7) return true           // Small dataset: show all
    if (p === 1 || p === totalPages) return true // Always show first + last
    if (Math.abs(p - page) <= 1) return true   // Neighbors of current
    return false
  })
  .reduce<(number | string)[]>((acc, p, i, arr) => {
    if (i > 0 && p - (arr[i - 1] as number) > 1) acc.push("...")
    acc.push(p)
    return acc
  }, [])
```

### Behavior by Page Count

| Total Pages | Example Display |
|-------------|----------------|
| 1–7 | `[1][2][3][4][5][6][7]` — all shown |
| 10, on page 4 | `[1]...[3][4][5]...[10]` — first, neighbors, last |
| 30, on page 1 | `[1][2]...[30]` — first + neighbor + last |

### Result

- Max 7 page buttons rendered regardless of total page count
- First + last pages always accessible
- Current page + neighbors visible for context
- Ellipsis reduces visual noise

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| In-memory cache over React Query | Simpler for static, session-scoped data. No need for caching, invalidation, or loading states beyond what we already had. |
| Skeleton UI pattern | Consistent with existing Page 1. Allows all UI elements (including collapsible sections) to be present and interactive from first render. |
| Route group pattern for shared layout | Clean separation between dashboard pages and utility pages (like `/_not-found`). Enables consistent sidebar across all dashboard routes. |
| Data context over per-page fetch | Centralizes loading state, error handling, and data availability. Avoids 3x `useEffect` duplication. Partial failure resilience via per-fetch `.catch()`. |
| Debounced threshold over raw state | Instant UI feedback (badge) + deferred expensive computation (chart data). 120ms matches perceptual "instant" threshold. |
| Scatter sampling over full render | Top 200 preserved (high-revenue SKUs), every nth from tail. < 200ms render vs 2-3s for full 2,232 points. |

---

## Related Documentation

- `implementation-plan.md` — Project task tracking
- `insights_log.md` — Business insights from data analysis
- `issues_log.md` — Data quality issues discovered during ETL
- `docs/bi-framework.md` — Business intelligence framework selection
- [Olist Marketing Funnel README](https://github.com/albarpambagio/olist-marketing-report/blob/master/README.md) — Reference for README structure patterns

---

## 16. QA Audit: setState Inside useMemo Causes Re-render Loops

### The Problem

```typescript
// at-risk-table.tsx — BUG
const filtered = useMemo(() => {
  setPage(1)  // ❌ State update during render
  if (!search) return skus
  return skus.filter(...)
}, [skus, search])
```

**Root Cause:** `useMemo` must be pure — no side effects. Calling `setPage(1)` inside a memoized computation triggers a state update during render, which causes React to re-render, which re-evaluates the `useMemo`, which calls `setPage(1)` again — infinite loop in React 18/19 Strict Mode.

### Solution

Move the side effect to `useEffect`:

```typescript
const filtered = useMemo(() => {
  if (!search) return skus
  return skus.filter(...)
}, [skus, search])

useEffect(() => {
  setPage(1)
}, [skus, search])
```

**Rule:** Never call `setState`, `dispatch`, or any side-effect function inside `useMemo`, `useCallback`, or the render body.

---

## 17. ETL Pipeline: Row-by-Row INSERT vs Batch Insert

### The Problem

```python
# transform.py — SLOW (30-60 minutes for 511K rows)
for row in rows_to_insert:
    cur.execute(insert_sql, row)
```

Each `cur.execute()` is one round-trip to the database. 511,559 rows = 511,559 network round-trips.

### Solution: psycopg2.extras.execute_values

```python
import psycopg2.extras

# FAST (< 30 seconds for 511K rows)
psycopg2.extras.execute_values(cur, insert_sql, rows_to_insert, page_size=10000)
```

`execute_values` uses PostgreSQL's `VALUES` syntax to batch rows into a single INSERT statement. `page_size=10000` means 10,000 rows per statement — 51 batches total instead of 511,559.

**Performance impact:** 30-60 minutes → < 30 seconds (100-200x faster).

---

## 18. ETL Pipeline: DROP TABLE vs TRUNCATE for Idempotent Loads

### The Problem

```sql
-- sql/02_create_star_schema.sql
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_transaction;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;
```

Every time `load.py` runs, it executes this SQL file — destroying all previously loaded data. This makes the pipeline non-idempotent: you can't re-run it safely without losing data.

### Solution: Separate Migration from Data Load

```python
# load.py — new function
def truncate_fact_tables(conn):
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE fact_sales, dim_transaction, dim_product, dim_date RESTART IDENTITY;")
    conn.commit()
    cur.close()
```

Replace `create_schema_tables(conn)` with `truncate_fact_tables(conn)` in `load.py`. Schema creation (`DROP TABLE` + `CREATE TABLE`) becomes a one-time migration. Data loads use `TRUNCATE` which is faster and preserves table structure, indexes, and constraints.

**Best Practice:** Schema changes should be managed via migration tools (Flyway, Alembic, etc.), not embedded in data load scripts.

---

## 19. Filter Composition: Avoid Mutating Source Data

### The Problem

```typescript
// page.tsx — BUG: filters overwrite each other
if (transactionType === "outpatient") {
  monthly = monthly.map((m) => ({ ...m, revenue: m.revenue_outpatient ?? 0 }))
}
if (productType === "generic") {
  monthly = monthly.map((m) => ({ ...m, revenue: m.revenue_generic ?? 0 }))
  // ❌ Overwrites the outpatient revenue set above!
}
```

When both filters are active, the second filter overwrites the revenue set by the first. The user sees generic revenue, not generic + outpatient revenue.

### Solution: Compute Derived Revenue in a Single Pass

```typescript
const displayMonthly = monthly.map((m) => {
  let revenue = m.revenue
  if (transactionType === "outpatient") revenue = m.revenue_outpatient ?? 0
  else if (transactionType === "inpatient") revenue = m.revenue_inpatient ?? 0
  if (productType === "generic") revenue = m.revenue_generic ?? 0
  else if (productType === "branded") revenue = m.revenue_branded ?? 0
  return { ...m, revenue }
})
```

Single `map` pass, all filter logic in one place, no intermediate mutations.

---

## 20. Lazy Data Fetching: Hybrid Approach with React Context

### The Problem

The original `DataProvider` fetched ALL 3 JSON files (~946 KB) on EVERY page load, even though:
- Overview page only needs `overview.json` (1.7 KB)
- Products page only needs `products.json` (442 KB)
- Margin Risk page only needs `margin_risk.json` (503 KB)

This wasted 944 KB on the Overview page — a **556x bandwidth waste**.

### Solution: Lazy Fetching with Shared Cache

```typescript
// data-context.tsx — lazy fetch functions
const fetchOverview = useCallback(async () => {
  if (state.overview || fetching.overviewLoading) return
  setFetching(prev => ({ ...prev, overviewLoading: true }))
  try {
    const data = await getOverviewData()
    setState(prev => ({ ...prev, overview: data }))
  } catch (e) {
    setError(prev => prev ?? (e as Error).message)
  } finally {
    setFetching(prev => ({ ...prev, overviewLoading: false }))
  }
}, [state.overview, fetching.overviewLoading])
```

Each page triggers its own fetch in `useEffect`:

```typescript
// page.tsx (Overview)
const { overview, loading, fetchOverview } = useData()
useEffect(() => { fetchOverview() }, [fetchOverview])
```

**Key design decisions:**

| Decision | Rationale |
|----------|-----------|
| `fetchOverview` exposed via context | Pages trigger their own data load |
| Guard: `if (state.overview) return` | Prevents double-fetch on navigation back |
| Shared cache (in-memory + sessionStorage) | Cross-page navigation = instant (already cached) |
| Per-dataset loading state | Overview can show data while Products is still loading |

**Result:** Overview page downloads 1.7 KB instead of 946 KB on first visit. Cross-page navigation still instant via shared cache.

---

## 21. Dynamic Imports with next/dynamic

### The Problem

All chart components were statically imported, meaning the browser downloaded and parsed JavaScript for ALL charts on the first page visit — even charts only used on other pages.

### Solution

```typescript
import dynamic from "next/dynamic"

const MonthlyRevenueChart = dynamic(
  () => import("@/components/page1/monthly-revenue-chart").then(m => m.MonthlyRevenueChart),
  { loading: () => <div className="h-[280px] animate-pulse rounded-lg bg-muted" /> }
)
```

**Impact on bundle size:**

| Route | Before | After | Change |
|-------|--------|-------|--------|
| `/` First Load JS | 259 kB | 143 kB | **-45%** |
| `/margin-risk` First Load JS | 264 kB | 147 kB | **-44%** |

**Tradeoff:** Dev server cold compile is ~1.6s slower (dynamic import overhead). Production is unaffected — chunks are pre-built.

**Best practice:** Always provide a `loading` fallback that matches the component's dimensions to avoid layout shift.

---

## 22. sessionStorage Cache Persistence

### The Problem

In-memory cache (`dataCache` object) is lost on page reload, causing all 3 JSON files to re-fetch.

### Solution

```typescript
function loadFromSessionStorage(key: string): unknown | null {
  if (typeof window === "undefined") return null
  try {
    const raw = sessionStorage.getItem(`pharmacy_cache_${key}`)
    if (!raw) return null
    const { data, timestamp } = JSON.parse(raw)
    if (Date.now() - timestamp > CACHE_TTL) {
      sessionStorage.removeItem(`pharmacy_cache_${key}`)
      return null
    }
    return data
  } catch {
    return null
  }
}
```

Cache lookup order: in-memory → sessionStorage → network fetch.

**Why sessionStorage (not localStorage):** Data is scoped to the current tab/session. Closing the tab clears the cache — appropriate for analytics data that might be regenerated.

**Why not both:** In-memory is fastest (no serialization). sessionStorage is the fallback for page reloads. The TTL check ensures stale data is not served.

---

## 23. CSV Export: Proper Field Quoting

### The Problem

```typescript
// BUG: values with commas break CSV structure
const csv = [headers, ...rows].map(r => r.join(",")).join("\n")
// If a field contains a comma: "SKU,Name",100,50 → breaks parsing
```

### Solution

```typescript
const csv = [headers, ...rows]
  .map(r => r.map(v => `"${v}"`).join(","))
  .join("\n")
```

Quote-wrap every value. This is the simplest correct CSV escaping. For production use, consider a proper CSV library (e.g., `papaparse`) that handles edge cases like embedded quotes and newlines.

---

## 24. Exception Handling: Uninitialized Variable in Error Handler

### The Problem

```python
# load.py — BUG
try:
    conn = psycopg2.connect(**DB_CONFIG)
    # ... do work
except Exception as e:
    update_lineage(conn, ...)  # ❌ conn was never assigned if connect() failed
```

If `psycopg2.connect()` raises an exception, `conn` is undefined. The `except` block references it, causing a `NameError` that swallows the original connection failure.

### Solution

```python
except Exception as e:
    if 'conn' in locals():
        try:
            update_lineage(conn, batch_id, 0, 0, 0, {"error": str(e)}, 'FAILED')
        except Exception:
            pass
```

Guard with `if 'conn' in locals()` to check if the variable was assigned before the exception.

---

## 25. `connectNulls=true` Creates False Continuity in Line Charts

### The Problem

```typescript
// monthly-trend-chart.tsx — MISLEADING
<Line connectNulls={true} dataKey="revenue" />
```

With only 5 months of data across 12 calendar months, `connectNulls` draws straight lines across 3-4 month gaps (Apr→Aug, skipping May-Jun-Jul). Users see a continuous trend that doesn't exist.

### Solution

Remove `connectNulls` (defaults to `false`). Gaps display as breaks in the line, which is the honest representation:

```typescript
<Line dataKey="revenue" />  // No connectNulls — gaps are visible
```

**Rule:** Never use `connectNulls` when data gaps represent missing data rather than zero values. A break in the line is more honest than a misleading straight connection.

---

## 26. Charts Must Respect Active Filter Scope

### The Problem

The SKU scatter chart and margin histogram always render all 12 months of SKU data regardless of the active month filter on Page 2. Users filtering to "January" still see the full-year scatter plot — the filter is silently ignored.

### Solution

Pipe the month filter into the data pipeline:

```typescript
// Option A: Filter at the aggregate level (preferred)
const filteredSkus = useMemo(() => {
  if (month === "all") return data.sku_scatter
  return data.sku_scatter.filter(s => s.year_month === month)
}, [data, month])

// Option B: Filter at the query level (ETL export)
// GROUP BY kd_obat, product_type, year_month
// WHERE d.year_month = :selected_month
```

**Rule:** Every filter on a page must affect every chart on that page. If a chart can't be filtered (e.g., histogram bins are pre-computed), document the limitation visibly.

---

## 27. Median Lines Must Match Displayed Data

### The Problem

```typescript
// scatter-chart.tsx — MISALIGNED
const medianX = data.reduce((sum, s) => sum + s.revenue, 0) / data.length  // Full 2,233 SKUs
// But chart only displays 500 sampled points
<ReferenceLine x={medianX} />  // Quadrant doesn't match visible points
```

The quadrant chart samples to 500 points but computes median lines from the full 2,233 SKU dataset. The visual quadrants don't match the visible points.

### Solution

Compute medians from the sampled (displayed) data:

```typescript
const sampledData = sampleData(data.sku_scatter, MAX_POINTS)
const medianX = sampledData.reduce((sum, s) => sum + s.revenue, 0) / sampledData.length
const medianY = sampledData.reduce((sum, s) => sum + (s.avg_margin_pct ?? 0), 0) / sampledData.length
```

**Rule:** Reference lines (medians, means, thresholds) must be computed from the same dataset that's being displayed. Mismatched reference lines create visual confusion.

---

## 28. KPI Delta Must Compare Same Cohort Over Time

### The Problem

```typescript
// page.tsx — MISLEADING
const prevMonth = useMemo(() => {
  const last = sorted[sorted.length - 1]
  const prev = sorted[sorted.length - 2]
  return {
    revenue: ((last.revenue - prev.revenue) / prev.revenue) * 100,
    // ❌ When a product-type filter is active, this compares
    //    different products across months, not the same cohort
  }
}, [filtered.monthly])
```

When a product-type or channel filter is active, the delta compares different products/channels across months rather than the same cohort over time.

### Solution

Compute period-over-period deltas after applying filters, ensuring the same cohort is compared:

```typescript
const prevMonth = useMemo(() => {
  if (!data || month !== "all") return null
  // Filter to same cohort as current display
  const cohortData = filtered.monthly.filter(m => m.year_month !== "all")
  if (cohortData.length < 2) return null
  const last = cohortData[cohortData.length - 1]
  const prev = cohortData[cohortData.length - 2]
  return {
    revenue: prev.revenue > 0
      ? ((last.revenue - prev.revenue) / prev.revenue) * 100
      : 0,
  }
}, [filtered.monthly, data, month])
```

**Rule:** Period-over-period comparisons must use the same filter cohort. A delta that mixes different products or channels is meaningless.

---

## 29. Silent Error Swallowing in DataProvider

### The Problem

```typescript
// data-context.tsx — NO ERROR FEEDBACK
const fetchProducts = useCallback(async () => {
  try {
    const data = await getProductsData()
    setState(prev => ({ ...prev, products: data }))
  } catch (e) {
    setError(prev => prev ?? (e as Error).message)  // Only sets error if none exists
  }
}, [...])
```

Errors in `getProductsData` and `getMarginRiskData` are caught but the `error` state is only set if `prev` is null (`prev ?? ...`). If overview already loaded successfully, product/margin errors are silently swallowed.

### Solution

Always surface errors, don't suppress them:

```typescript
catch (e: unknown) {
  const msg = (e as Error).message
  setError(prev => prev ? `${prev}; ${msg}` : msg)  // Append, don't suppress
}
```

**Rule:** Error state should accumulate, not suppress. Multiple errors can coexist — join them with semicolons or use an error array.

---

## 30. Missing Year Validation in NO_RESEP Parser

### The Problem

```python
# transform.py — ACCEPTS INVALID YEARS
def _valid_month(ym):
    parts = str(ym).split("-")
    m = int(parts[1])
    return 1 <= m <= 12  # ❌ Never checks the year!
```

A row like `RJ-01.9999-01-0001` passes as valid and appears in monthly charts under year 9999.

### Solution

Add year validation:

```python
def _valid_month(ym):
    try:
        parts = str(ym).split("-")
        year = int(parts[0])
        m = int(parts[1])
        return year == 2015 and 1 <= m <= 12  # Year guard added
    except (ValueError, IndexError):
        return False
```

**Rule:** Always validate all components of a parsed string, not just the parts you care about. Unvalidated components can introduce phantom data.

---

## 31. Division by Zero in KPI Delta Calculation

### The Problem

```typescript
// page.tsx — POSSIBLE INFINITY
const prevMonth = useMemo(() => {
  return {
    revenue: ((last.revenue - prev.revenue) / prev.revenue) * 100,
    // ❌ If prev.revenue === 0, this displays "Infinity%"
  }
}, [...])
```

### Solution

Add guard:

```typescript
revenue: prev.revenue > 0
  ? ((last.revenue - prev.revenue) / prev.revenue) * 100
  : 0,
```

**Rule:** Always guard division operations where the denominator can be zero. Display "N/A" or 0 instead of Infinity.

---

## 32. Cache-Busting Query Param for Development

### The Problem

```typescript
// data.ts — STALE DATA IN DEV
const res = await fetch("/data/overview.json")
```

The in-memory cache + sessionStorage persist across navigations with no expiry or rebuild trigger. Regenerated JSON files during a development session won't be picked up — you see stale data until you clear the cache manually or reload the page.

### Solution

Add a cache-busting timestamp query param in development mode:

```typescript
const CACHE_BUST =
  process.env.NODE_ENV === "development" ? `?t=${Date.now()}` : ""

const res = await fetch(`/data/overview.json${CACHE_BUST}`)
```

**How it works:**

| Environment | URL | Behavior |
|-------------|-----|----------|
| Development | `/data/overview.json?t=1716249600000` | Unique URL each load — bypasses browser cache |
| Production | `/data/overview.json` | Cached by CDN — optimal performance |

**Rule:** In development, always bust the cache for static data files. In production, rely on CDN caching for performance.

---

## 33. Visible Disclaimer for Charts That Can't Be Filtered

### The Problem

The SKU scatter chart and margin histogram show full-year aggregated data. When a user selects a month filter on Page 2, the trend chart updates but the scatter chart doesn't — creating a confusing inconsistency.

Fixing this properly would require changing the ETL export to include `year_month` in the SKU-level data, or computing per-month aggregates at query time.

### Solution: Honest Disclaimer

Instead of silently ignoring the filter, add a visible amber disclaimer:

```tsx
<div className="flex items-center gap-1 text-amber-600">
  <span>Full-year data — month filter applies to trend chart only</span>
</div>
```

**Why this pattern works:**

| Approach | Pros | Cons |
|----------|------|------|
| Fix properly (ETL change) | Correct behavior | Requires pipeline rebuild, schema change |
| Hide the chart when filtered | Honest | Removes useful context |
| Disclaimer (chosen) | Honest, no pipeline changes | User sees limitation |

**Rule:** When a chart can't respect a filter due to data structure limitations, document the limitation visibly rather than silently ignoring it. An amber disclaimer is better than silent inconsistency.

---

## 34. Strip Template Boilerplate Before Deploy

### The Problem

The Shadboard starter kit includes features designed for a full SaaS dashboard:
- User authentication UI (avatar, dropdown with Profile/Settings/Sign Out)
- Command palette / search menu
- Fullscreen toggle
- Horizontal + vertical layout switching
- Theme color switching (zinc, blue, etc.)
- Border radius customization
- RTL language support
- Toast notifications

For a static analytics portfolio with 3 pages, all of these are dead code that:
- Adds unnecessary bundle weight
- Creates confusing UI elements (fake user "John Doe")
- Risks build errors from unused imports
- Distracts from the actual content

### Solution: Surgical Removal

Removed 15+ files and simplified 8 more:

| Removed | Reason |
|---------|--------|
| `user-dropdown.tsx`, `user.ts` | Fake user data, no auth needed |
| `command-menu.tsx` | Search adds no value for 3 pages |
| `full-screen-toggle.tsx` | Nice-to-have, not portfolio-critical |
| `horizontal-layout/` (4 files) | Only vertical layout used |
| `avatar.tsx`, `keyboard.tsx`, `toaster.tsx`, `sonner.tsx`, `menubar.tsx`, `calendar.tsx`, `drawer.tsx` | Unused UI components |
| `use-is-vertical.tsx`, `use-is-rtl.tsx`, `use-mode.tsx`, `use-radius.tsx` | Dead hooks |

| Simplified | Change |
|------------|--------|
| `settings-context.tsx` | `SettingsType` with 5 fields → `{ mode: ModeType }` only |
| `types.ts` | Removed `UserType`, `LayoutType`, `SettingsType`, etc. |
| `providers/index.tsx` | Removed `locale` prop |
| `theme-provider.tsx` | Removed theme/radius class logic |
| `mode-provider.tsx` | Uses settings context directly instead of deleted `use-mode` hook |
| `sidebar.tsx` | Removed CommandMenu + horizontal layout check |
| `vertical-layout-header.tsx` | Only ModeDropdown + SidebarTrigger |
| `layout/index.tsx` | Always renders `<VerticalLayout>` |

### Result

- Build passes cleanly with no dead imports
- No confusing UI elements (no fake user, no search)
- Smaller bundle (fewer components to compile)
- Codebase reflects actual feature set, not starter kit defaults

### Rule

Always audit template/starter kit code before shipping. Every component that doesn't serve the actual use case is a liability — not just bundle size, but maintenance burden and potential confusion for reviewers.

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
| Lazy data fetching over eager | 556x bandwidth reduction on Overview page (1.7 KB vs 946 KB). Cross-page caching preserved via shared context. |
| Dynamic imports for charts | 45% smaller JS bundles on Overview and Margin Risk pages. Dev compile penalty (~1.6s) is acceptable tradeoff. |
| sessionStorage for cache persistence | Survives page reload without re-fetching. Scoped to tab/session — appropriate for analytics data. |
| psycopg2.extras.execute_values over row-by-row | 100-200x faster ETL transform (30-60 min → < 30 sec). |
| TRUNCATE over DROP TABLE for data loads | Idempotent pipeline — re-running load.py doesn't destroy schema. Faster than DROP + CREATE. |
| Computed derived revenue in single pass | Prevents filter composition bugs where second filter overwrites first filter's result. |
| Single package manager lockfile | Mixing npm and pnpm lockfiles causes dependency resolution inconsistencies. |
| `.env` in `.gitignore` | Standard security practice — `.env` files often contain secrets. |
| Remove unused font imports | Each unused font adds ~50-200 KB to initial page load. |
| README as executive brief | Scenario-first, findings with citations, recommendations with confidence — mirrors proven portfolio project structure. |
| No `connectNulls` on line charts | Gaps in data are meaningful — a break in the line is more honest than a misleading connection. |
| Reference lines from displayed data | Median/mean lines must be computed from the same dataset being displayed, not the full source. |
| KPI delta uses same cohort | Period-over-period comparisons must apply the same filters to both periods. |
| Error state accumulates | Multiple errors can coexist — append with semicolons rather than suppressing subsequent errors. |
| Validate all parsed string components | Don't just validate the parts you use — unvalidated components can introduce phantom data. |
| Guard all division operations | Denominators can be zero — always check before dividing. |
| Cache-busting in development | Stale JSON files during dev sessions won't be picked up without cache invalidation. Unique URL per load solves this. |
| Visible disclaimer over silent inconsistency | When a chart can't respect a filter, document the limitation visibly. An amber disclaimer is better than confusing behavior. |
| Strip template boilerplate before deploy | Dashboard starter kits ship with user auth, search, theme switching, layout options — none needed for a static analytics portfolio. Removing dead code reduces bundle size, eliminates confusing UI elements, and prevents build errors. |
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

## 35. Filter Composition: Cross-Tabulated Data Required for Multi-Dimension Filters

### The Problem

Page 1 had two filters (Transaction Type, Product Type) that were supposed to work together. When both were active (e.g., "Outpatient" + "Generic"), the productType filter overwrote the transactionType filter:

```typescript
// page.tsx — BUG: sequential overwrites
let revenue = m.revenue
if (transactionType === "outpatient") {
  revenue = m.revenue_outpatient ?? 0    // Set to outpatient
}
if (productType === "generic") {
  revenue = m.revenue_generic ?? 0       // OVERWRITES with generic (all channels!)
}
```

**Root Cause:** The ETL export only had single-dimension breakdowns:
- `revenue_outpatient`, `revenue_inpatient` (by channel only)
- `revenue_generic`, `revenue_branded` (by product only)

There was no way to compute the intersection (Outpatient + Generic) because the data didn't exist.

**Additional issues found:**
- `transactions` count was never filtered — always showed total
- `avg_margin_pct` was never filtered — always showed overall average
- Page 2 `SKUQuadrantChart` ignored productType filter entirely
- Page 3 `MarginHistogram` used pre-computed bins from all SKUs, ignoring productType filter

### Solution: Cross-Tabulated ETL + Single-Pass Lookup

Added 8 new fields to the ETL export query:

```sql
-- Revenue intersections
SUM(f.revenue) FILTER (WHERE t.transaction_type = 'Outpatient' AND p.product_type = 'Generic')::float AS revenue_outpatient_generic,
SUM(f.revenue) FILTER (WHERE t.transaction_type = 'Outpatient' AND p.product_type = 'Branded')::float AS revenue_outpatient_branded,
SUM(f.revenue) FILTER (WHERE t.transaction_type = 'Inpatient' AND p.product_type = 'Generic')::float AS revenue_inpatient_generic,
SUM(f.revenue) FILTER (WHERE t.transaction_type = 'Inpatient' AND p.product_type = 'Branded')::float AS revenue_inpatient_branded,
-- Transaction counts per channel
COUNT(*) FILTER (WHERE t.transaction_type = 'Outpatient')::int AS transactions_outpatient,
COUNT(*) FILTER (WHERE t.transaction_type = 'Inpatient')::int AS transactions_inpatient,
-- Margin averages per dimension
AVG(f.margin_pct) FILTER (WHERE t.transaction_type = 'Outpatient')::float AS avg_margin_pct_outpatient,
AVG(f.margin_pct) FILTER (WHERE t.transaction_type = 'Inpatient')::float AS avg_margin_pct_inpatient,
AVG(f.margin_pct) FILTER (WHERE p.product_type = 'Generic')::float AS avg_margin_pct_generic,
AVG(f.margin_pct) FILTER (WHERE p.product_type = 'Branded')::float AS avg_margin_pct_branded
```

Frontend uses a single lookup table with all 9 combinations (4 intersections + 2 channel-only + 2 product-only + 1 all):

```typescript
if (txn === "outpatient" && prod === "generic") {
  revenue = m.revenue_outpatient_generic ?? 0
  transactions = m.transactions_outpatient ?? 0
  avg_margin_pct = m.avg_margin_pct_generic ?? null
} else if (txn === "outpatient" && prod === "branded") {
  // ... etc for all 9 combinations
}
```

### Other Pages Fixed

| Page | Issue | Fix |
|------|-------|-----|
| **2** | `SKUQuadrantChart` ignored productType filter | Pass filtered `data.sku_scatter` instead of raw |
| **3** | `MarginHistogram` used pre-computed bins | Recompute bins client-side from filtered SKUs |

### Rule

When supporting multi-dimension filters, the data export must include cross-tabulated fields for every combination. Don't try to compose single-dimension fields at the frontend — the intersection data must exist in the source.

### Type Safety Note

Adding nullable fields (`avg_margin_pct` can be `null` when filters produce no data) requires null guards everywhere the value is used:

```typescript
// Sort comparison
cmp = (a.avg_margin_pct ?? 0) - (b.avg_margin_pct ?? 0)

// Display
{(d.avg_margin_pct ?? 0).toFixed(1)}%

// Delta calculation
last.avg_margin_pct !== null && prev.avg_margin_pct !== null
  ? last.avg_margin_pct - prev.avg_margin_pct
  : 0
```

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

> **SUPERSEDED 2026-06-02** — HF Spaces replaces Cloudflare Pages as deployment target. §80's "Plotly EDA → Plotly dashboard" parity now realized.

## 75. Cloudflare Pages Constraint Hard-Blocks All Python Server Frameworks

### The Problem

When evaluating Vizro (McKinsey's low-code Python dashboard toolkit) as a replacement for the planned Next.js + Shadboard stack, the initial framing was "low-code velocity vs. full-code control." The actual binding constraint turned out to be the **deployment target**: Cloudflare Pages is a static-site host. Vizro is a Dash server. The two are not directly compatible.

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

Comparing "Vizro vs. Next.js + Shadboard" is a structural mismatch — different runtimes, different deployment models, different LOC profiles, different community sizes. Without an explicit scoring method, the comparison collapses to "Vizro is low-code" vs. "Next.js is more familiar" — both of which are vibes, not decisions. The same trap applies to any framework choice: Streamlit vs. Dash, PostgreSQL vs. DuckDB, dbt vs. SQLMesh.

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

The Phase 6 dashboard plan (Next.js + Shadboard) was designed against a specific data contract: 5 JSON files in `dashboard/public/data/` (one per mart model) + `forecast.json` (819 records). All five files are already produced by `export/export_json.py` with `verify_export()` row-count validation. Switching to Vizro, Streamlit, Dash, etc. would discard this data layer in favor of "the framework queries DuckDB directly."

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

## 79. LEARNINGS.md Patterns Are Stack-Specific — Switching Means Losing the Knowledge Base

### The Problem

This LEARNINGS.md file has 74 sections, of which 35+ are specific to the Next.js + Shadboard stack (sections §1–§34 plus downstream references). These document real bugs, real fixes, and real patterns earned through implementation. Switching to Vizro (or any other dashboard framework) does not just cost implementation time — it costs **the entire knowledge base**, because the patterns don't transfer:

| LEARNINGS.md section | Applies to Next.js? | Applies to Vizro? |
|---------------------|--------------------:|------------------:|
| §5 — Sidebar Disappearance (route group) | Yes | No (Vizro uses `pages/` config) |
| §6 — React Hooks Before Early Return | Yes | No (Vizro is callback-based) |
| §11 — DataProvider for Centralized Loading | Yes | No (Vizro has built-in `data_manager`) |
| §19 — Filter Composition (No Mutation) | Yes | Partial (different bug, same concept) |
| §21 — Dynamic Imports (`next/dynamic`) | Yes | No (Vizro bundles differently) |
| §22 — sessionStorage Cache | Yes | No (Vizro server-side state) |
| §25 — `connectNulls` Avoidance | Yes | Partial (Vizro uses Plotly; same chart, different API) |
| §26 — Charts Must Respect Filters | Yes | No (Vizro has built-in cross-filter) |
| §34 — Strip Shadboard Boilerplate | Yes | No (Vizro has its own boilerplate) |
| §35 — Cross-Tabulated Data for Filters | Yes | Yes (universal concept) |

About **70% of the dashboard-stack-specific sections become inapplicable** on a switch. The remaining 30% are about the data pipeline (dbt, DuckDB, forecast) and transfer to any framework.

### The Real Cost

Switching to a new dashboard framework doesn't just mean writing new framework code. It means:

1. **Re-discovering every bug** — `connectNulls` issue, filter composition bug, hooks order, dynamic imports, etc., will recur in the new framework with new symptoms
2. **Re-documenting every fix** — sections §5, §6, §11, §19, §21, §22, §25, §26, §34 all need to be re-earned
3. **Carrying dead knowledge** — the old sections stay in LEARNINGS.md as historical record, but the patterns don't help anyone building on the new stack

For a solo project, the cost of a framework switch includes **2-4 weeks of equivalent bug-hunting and LEARNINGS.md work** that doesn't show up in any feature comparison chart.

### Solution

Treat LEARNINGS.md sections specific to a stack as **sunk cost in that stack's favor**. When a new framework is proposed, count:

- **Stack-specific sections in LEARNINGS.md** that don't transfer → switching cost
- **Stack-specific community knowledge** not yet captured in this file → additional risk
- **Estimated re-discovery time** for the 10-15 most expensive bugs → 2-4 weeks

Add this to the framework comparison matrix as a row. For a 30+ section knowledge base, this row should be weighted 8-10 — higher than most "feature" rows.

### Rule

A LEARNINGS.md file is a stack-specific asset. Switching frameworks means abandoning most of the existing entries and re-earning them in the new framework. The cost of a switch is **the cumulative implementation experience**, not just the next 2 weeks of work. This cost is invisible in feature comparisons but very real in delivery timelines.

---

## 80. Chart Engine Parity Between EDA and Dashboard Saves Migration Cost

### The Problem

This project has two visualization layers:

1. **EDA / Marimo notebook** (`analysis/eda.py`, 1670+ lines) — uses **Plotly** for all charts
2. **Dashboard** (Phase 6, Next.js + Shadboard) — uses **Recharts** (SVG-based React lib)

The chart engine mismatch means every chart spec must be **translated** from Plotly to Recharts when promoting EDA findings to dashboard pages. Translation is not free — Plotly's `add_vline`, `make_subplots`, `add_annotation` API has no direct Recharts equivalent, so charts get simplified or rewritten from scratch.

### Why This Matters for Framework Choice

If the dashboard used **Plotly** (via Dash, Streamlit's `st.plotly_chart`, Panel, or Vizro), the EDA notebook's chart code is **directly portable** to the dashboard. Example: a `go.Figure()` with `add_vline(x="2022-01-15", line_dash="dash", annotation_text="Cooking oil shock")` works in both `eda.py` and a Dash `dcc.Graph(figure=fig)`. The same chart in Recharts requires a `<ReferenceLine x="2022-01-15" strokeDasharray="..." label="..." />` JSX component, with different prop names and a different event API.

### The Migration Cost Matrix

| EDA Library | Dashboard Library | Port Cost |
|------------|-------------------|----------:|
| Plotly | Recharts (current plan) | **High** — translate every chart spec |
| Plotly | Plotly (via Dash) | **None** — copy chart code verbatim |
| Plotly | Plotly (via Streamlit) | **None** — `st.plotly_chart(fig)` |
| Plotly | Plotly (via Vizro) | **None** — Vizro uses Plotly natively |
| Plotly | Plotly (via Panel) | **None** — Panel wraps Plotly |
| Matplotlib | Recharts | High — translate |
| Matplotlib | Plotly | Medium — different API |

### Hidden Benefit Beyond Migration Cost

Beyond the literal "translate less code" benefit, Plotly parity enables:

- **Chart spec reuse** — the `for fig in figs: mo.mpl.interactive(fig)` patterns in marimo can drop into Dash `dcc.Graph`
- **Consistent visual identity** — same color palette, same font, same `tickformat="~s"` patterns work everywhere
- **Same documentation lookup** — one Plotly reference, not Plotly + Recharts
- **Same bug fix** — `connectNulls` discussion in LEARNINGS.md §25 transfers directly to a Plotly dashboard

### The Trade-off

Recharts is genuinely better in some cases:
- Smaller bundle (SVG vs. canvas)
- Native React integration
- Tighter TypeScript types

But for a portfolio project where the **analytical depth** is the selling point and the **chart richness** is the centerpiece (forecast CI, lag heatmap, Ramadan overlay), Plotly's expressive API matters more than Recharts' bundle size. Cloudflare Pages CDN neutralizes the bundle-size concern.

### Rule

When choosing a dashboard framework, check the chart engine against the EDA notebook's chart library. If they match, chart specs are portable; if they don't, every chart in the dashboard must be re-implemented. The translation cost is proportional to the number of unique chart types in the EDA — count them before deciding.

---

## 81. Dash Pages Routing: `dash.register_page` + `use_pages=True`

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
| LEARNINGS.md sections as stack-specific sunk cost | 35+ sections of this file are Next.js+Shadboard specific and don't transfer to a new framework. Switching means re-discovering every bug (route groups, hooks order, dynamic imports, filter composition) and re-documenting each fix. Cost is invisible in feature charts but real in delivery timelines. |
| Chart engine parity between EDA and dashboard | Plotly EDA → Recharts dashboard requires translating every chart spec. Plotly EDA → Dash/Streamlit/Vizro/Panel dashboard = verbatim copy. For a portfolio project where analytical depth is the selling point and chart richness is the centerpiece, Plotly parity saves real translation cost. |
| Dash Pages over manual URL routing | `use_pages=True` + `dash.register_page` eliminates per-page URL callback boilerplate. One `page_container` in app layout replaces manual `dcc.Location` + pathname matching. |
| `lru_cache` over per-callback DuckDB connections | 4 pages × 3 filters = 12+ connections per user session. `lru_cache(maxsize=32)` serves repeated queries from in-process memory; `read_only=True` prevents accidental writes. |
| Global filter IDs over `dcc.Store` for filter state | Dash Pages shares the same layout across pages — global filter IDs work without intermediate Store. `dcc.Store` only needed for cross-reload persistence. |
| Port 7860 for HF Spaces | HF Spaces standard port; changing requires Space config update. Local dev matches production port for parity. |
| Dash 3.x strict output declaration | Dash 3.x raises `InvalidCallback` for undeclared outputs (Dash 2.x silently ignored). All `@callback` outputs must be declared and returned. |
