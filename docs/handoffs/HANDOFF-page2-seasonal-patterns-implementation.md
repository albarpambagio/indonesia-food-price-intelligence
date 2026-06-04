# Handoff: Page 2 Seasonal Patterns — Implementation

**Generated:** 2026-06-04 14:22
**Gap-fixed:** 2026-06-04 (post-verification pass — see "Gap-Fix Notes" at bottom)
**Context:** Systematic gap analysis performed before implementing Dashboard Page 2 (Seasonal Patterns) in Vizro.

---

## What Was Done

A full gap analysis was run against `docs/wireframes/wfp-wireframe-page2-seasonal-patterns.md` by examining:

- `dashboard/pages/seasonal_patterns.py` (222 lines of old Dash code — must be overwritten)
- `dashboard/public/data/seasonal_patterns.json` (35 records — Cooking Oil only, 2024-06 → 2024-12, NOT what the wireframe expects — see §1 below)
- `dashboard/app.py` (only Page 1 wired in; Page 2 import + `pages=[...]` entry must be added)
- `dashboard/charts/` (4 files for Page 1, zero for Page 2)
- `dashboard/data_manager.py` (all 6 marts + `forecast` already registered — reusable as-is)
- `dashboard/data_access.py` (framework-agnostic — reusable as-is; extend with new pre-computation helpers per §5)
- `transform/models/marts/mart_seasonal_patterns.sql` (current source model — covers Cooking Oil × island_group only)
- `transform/models/marts/mart_price_trends_national.sql` (the REAL source for cross-commodity seasonal analysis — 17-year history, all 4 commodities)
- `transform/seeds/islamic_calendar.csv` (year, ramadan_start, eid_date) + `int_islamic_calendar` model (year, eid_date, eid_month, t_minus_1, t_minus_2, t_minus_3, t_plus_1)
- `docs/LEARNINGS.md` §87–98 (Vizro patterns; §97 and §98 are CRITICAL Page-1 bugs that will recur on Page 2 — see §7 below)
- `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md` (earlier handoff for Phase C)
- `dashboard/charts/trend_forecast.py`, `kpi_sparklines.py`, `yoy_bar.py`, `signal_badges.py` (reference @capture("graph") patterns)
- `dashboard/spike/custom_charts.py` (minimal `px.imshow` reference — relevant for the heatmap)
- AGENTS.md "Known Limitations" table (data constraint that drives the wireframe's [3d] / [4f] callouts)

## Key Findings

### 1. Data Source Mismatch (CRITICAL — corrected from original draft)
The wireframe expects 4 commodities × 12 months × ~17 years of seasonal data. The originally cited source (`mart_seasonal_patterns` / `seasonal_patterns.json`) **cannot deliver this** — verified directly against DuckDB:

| Source | Rows | Commodities | Date span | Notes |
|--------|------|-------------|-----------|-------|
| `mart_seasonal_patterns` (DuckDB) | **35** | Cooking Oil only | 2024-06 → 2024-12 | Filtered to `island_group IS NOT NULL AND price_flag='actual'` — eliminates national-only commodities |
| `seasonal_patterns.json` (legacy) | 35 | Cooking Oil only | 2024-06 → 2024-12 | Exported from the same mart; same shape |
| `mart_price_trends_national` (DuckDB) | 639 total | All 4 (Cooking Oil 165 mo, Rice/Sugar/Flour 158 mo each) | 2007-01 → 2024-12 (Cooking Oil), 2007-01 → 2020-03 (others) | **Use this as the primary source for the heatmap, Ramadan overlay, year-end chart, summary table, and action cards.** |
| `mart_commodity_correlation` (DuckDB) | 165 | All 4 (wide format: `rice_price`, `oil_price`, `sugar_price`, `flour_price`) | 2007-01 → 2024-12 | Alternative for the heatmap if a single wide-format query is preferred. |

**Decision:** Page 2 reads from **two marts**, not one:

1. **`mart_price_trends_national`** — primary source. Compute `price_index = (avg_price_idr / annual_avg(year, commodity)) * 100` in pandas inside the chart functions. Drives heatmap [5], Ramadan overlay [6], harvest chart [7], year-end chart [8], summary table [9], and action cards [4].
2. **`mart_seasonal_patterns`** — only when the global Island Group filter is set to a specific island AND commodity is Cooking Oil. Provides island-disaggregated price_index already pre-computed.

Both are already registered in `dashboard/data_manager.py` (lines 13–14). No pipeline change needed. Document the per-commodity date floor (Rice/Sugar/Flour data ends 2020-03 because the national price series stopped there) in the subtitle [2] or as an info callout, otherwise reviewers will ask why the heatmap doesn't show 2021–2024 data for those commodities.

### 2. Ramadan `week_relative` Must Be Month-Granularity, Not Weekly
The centerpiece chart (multi-year overlay relative to Eid al-Fitr) requires an integer time index. **All upstream data is monthly**, not weekly — `int_prices_normalised.month` is a TIMESTAMP truncated to the 1st of each month per AGENTS.md, and `mart_price_trends_national` aggregates by month.

**Decision:** Compute `month_relative` not `week_relative`. Range becomes T-2 to T+1 (4 months: 2 before Eid, the Eid month, and 1 after) instead of T-8 to T+6 (which would imply weekly data we don't have).

Implementation: in the chart function, load the Islamic calendar via:
```python
import duckdb
conn = duckdb.connect(DB_PATH, read_only=True)
cal = conn.execute("SELECT year, eid_date FROM wfp_intermediate.int_islamic_calendar ORDER BY year").fetchdf()
```
Then for each (commodity, year) in the price data, compute `month_relative = (price.month.year * 12 + price.month.month) - (eid.year * 12 + eid.month)` and bucket. Bold avg = mean across all 17 years per `month_relative`. Update wireframe annotation [6d] in the implementer's PR description to call out the granularity change (do **not** edit the wireframe itself per Phase C handoff §"Do NOT Touch").

`int_islamic_calendar` schema (verified):
```
year INTEGER, eid_date DATE, eid_month VARCHAR (YYYY-MM), t_minus_1 VARCHAR, t_minus_2 VARCHAR, t_minus_3 VARCHAR, t_plus_1 VARCHAR, source VARCHAR
```

### 3. Conditional Visibility — Pick One of Three Documented Patterns
Three mutually exclusive charts (Ramadan overlay [6], Harvest [7], Year-End [8]) must toggle based on the seasonal driver selector. Vizro 0.1.x has no declarative conditional visibility (LEARNINGS §96).

Three patterns, ranked by recommendation:

| # | Pattern | LOC | Pros | Cons |
|---|---------|-----|------|------|
| **A (RECOMMENDED)** | Empty-figure swap via `vm.Parameter` — all 3 charts always in DOM; inactive ones return `go.Figure().add_annotation(text="")` and `height=0` to collapse vertically | ~5 per chart | No Dash callback, pure Vizro, easy to test | Tiny vertical residue from chart frame even at height=0 (mitigated by `margin=dict(t=0,b=0)`) |
| B | Post-build Dash callback toggling `display:none` on the container `id` (LEARNINGS §96 verbatim) | ~20 in `app.py` | Cleanly hides components | Adds a Dash callback after `Vizro().build()`; ID coupling is brittle to Vizro version bumps |
| C | `vm.Tabs` with 3 tabs (Ramadan / Harvest / Year-End) — wireframe deviation but Vizro-native | ~10 | Idiomatic Vizro, no hack | Loses the "driver toggle" semantic — wireframe shows pill buttons [3], not tabs |

**Decision:** Pattern A. Implement the empty placeholder with `height=1, margin=dict(t=0,b=0,l=0,r=0), xaxis_visible=False, yaxis_visible=False` and a `showlegend=False` toggle. The driver Dropdown is passed via `vm.Parameter(targets=["ramadan_overlay.driver", "harvest_chart.driver", "yearend_chart.driver"])` — each chart returns the empty placeholder when `driver != "its driver"`.

### 4. No Custom Chart Files Exist
| Required File | Purpose | Vizro Wrapper | Reference Pattern |
|---------------|---------|---------------|-------------------|
| `charts/seasonal_heatmap.py` | 4×12 heatmap via `px.imshow` | `vm.Graph` | `dashboard/spike/custom_charts.py:lag_heatmap` (closest match) |
| `charts/ramadan_overlay.py` | Multi-year line chart, bold avg, 2022 outlier label | `vm.Graph` | `charts/trend_forecast.py` (CI fill, annotation, vline) |
| `charts/harvest_chart.py` | Rice deviation bars + harvest vrect shading | `vm.Graph` | `charts/yoy_bar.py` (bar + ref lines + vrect) |
| `charts/yearend_chart.py` | 4-commodity Nov–Dec premium bar | `vm.Graph` | `charts/yoy_bar.py` |
| `charts/seasonal_summary_table.py` | Sortable summary | **`vm.AgGrid`** (verified available in 0.1.x — `dir(vizro.models)` includes `AgGrid`) | No reference yet; see Vizro docs `vm.AgGrid` |

**Action cards [4] are NOT a chart.** Build them with `vm.Card(text=markdown)` inside a `vm.Container(layout=vm.Flex(direction="row"))`, following the pattern in `dashboard/pages/price_trends.py:16-56` (`_build_model_info_card`). Add a `_build_action_cards(driver: str) -> vm.Container` helper in `dashboard/pages/seasonal_patterns.py` that pulls pre-computed action-window stats from `data_access.py` and renders them as markdown. The data-availability notice [4f] is a separate `vm.Card` with a single markdown line.

### 5. Action Window Pre-computation — Add to `data_access.py`
Spike %, consistency (N of available years), and lead months must be computed per driver × commodity pair. Per Page 1's convention all helpers live in `data_access.py` (not in chart modules).

Add these signatures (test names included for tracking):

```python
def compute_action_windows(
    df_national: pd.DataFrame,   # mart_price_trends_national
    driver: str,                 # "Ramadan" | "Harvest" | "Year-End"
    islamic_cal: pd.DataFrame,   # int_islamic_calendar
) -> pd.DataFrame:
    """Return per-commodity row with columns:
    {commodity, spike_pct, consistency_score, total_years, lead_months, data_scope}
    Filter to commodities with spike_pct > 3 per wireframe [4a]."""

def compute_heatmap_matrix(
    df_national: pd.DataFrame,
) -> pd.DataFrame:
    """4×12 matrix indexed by commodity, columns 1-12 = month_of_year,
    values = mean premium % vs annual avg pooled across years."""

def compute_ramadan_overlay(
    df_national: pd.DataFrame,
    commodity: str,
    islamic_cal: pd.DataFrame,
) -> pd.DataFrame:
    """Return long DataFrame {year, month_relative, price_index}
    where month_relative ∈ [-2, +1] and price_index = (price / annual_avg) * 100."""
```

Formulas:
- `spike_pct = (mean(price_index during driver months) - mean(price_index during non-driver months)) / mean(non_driver) * 100`
- `consistency_score = count(years where avg_driver > avg_annual) / total_years_with_data`
- `lead_months` = derived from the driver: Ramadan → "2 months before Eid"; Harvest → "Mar–Apr or Aug–Sep"; Year-End → "Nov–Dec"

### 6. Island Group Filter Constraint — Concrete Handling
Wireframe [3d]: Island filter applies only to Cooking Oil. **Implementation rule for every chart function:**

```python
@capture("graph")
def some_chart(data_frame, commodity_filter="All", island_filter="All"):
    if island_filter != "All" and commodity_filter != "Cooking Oil" and commodity_filter != "All":
        # silently ignore island filter for non-Cooking-Oil
        island_filter = "All"
    elif island_filter != "All":
        # Cooking Oil specific path — query mart_seasonal_patterns instead
        from dashboard.data_access import load_mart
        data_frame = load_mart("mart_seasonal_patterns", island_group=island_filter)
    # ... rest of logic uses data_frame
```

The `[4f]` data-availability callout `vm.Card` stays always-visible regardless of filter state — it explains the constraint statically, not reactively.

### 7. Cross-Page Filter Persistence + Two Critical Page-1 Bugs (LEARNINGS §97, §98)
All `vm.Filter` instances must set `show_in_url=True` (LEARNINGS §89). **However, Page 1 uses `vm.Parameter`, NOT `vm.Filter`,** because of two production bugs that will recur on Page 2 if ignored:

- **LEARNINGS §97 — `vm.Filter` does NOT support "All" as a sentinel.** `vm.Filter(column="commodity_consolidated", selector=vm.Dropdown(options=["All", "Rice", ...]))` calls `series.isin(["All"])` literally → empty DataFrame. Page 2's three "All-aware" dropdowns (Commodity, Island Group, Driver) must use `vm.Parameter(targets=[...], selector=vm.Dropdown(...))` instead, and chart functions must guard `if commodity_filter != "All":` themselves.
- **LEARNINGS §98 — Never pass literal default args in `vm.Graph(figure=fn(commodity_filter="commodity_filter"))`.** First-render `_get_parametrized_config` returns the literal string `"commodity_filter"` because the `vm.Parameter` callback hasn't fired yet → function sees a bogus value. Pass only `data_frame=` and let the Python default kick in: `vm.Graph(figure=fn(data_frame="mart_price_trends_national"))`.

For the **Year Range** filter (numeric range over `month` column), `vm.Filter` IS appropriate — it doesn't use an "All" sentinel; it uses min/max bounds. Use `vm.Filter(column="month", selector=vm.RangeSlider(...), show_in_url=True)`.

Component mapping summary:

| Wireframe control | Vizro component | Why |
|-------------------|------------------|-----|
| Commodity dropdown ([3]) | `vm.Parameter` + `vm.Dropdown` (options include "All") | §97 sentinel bug |
| Island Group dropdown ([3]) | `vm.Parameter` + `vm.Dropdown` (options include "All") | §97 sentinel bug + per-commodity override (§6) |
| Year Range slider ([3]) | `vm.Filter(column="month", selector=vm.RangeSlider(...), show_in_url=True)` | No sentinel; bounded numeric range |
| Driver toggle ([3]) | `vm.Parameter` + `vm.RadioItems` (Ramadan / Harvest / Year-End / All) | Drives empty-figure swap (§3 Pattern A) |

---

## Suggested Skills

The agent continuing this work should invoke these skills:

1. **`brainstorming`** — Before writing any code, confirm the conditional-visibility approach (§3 Pattern A) and chart function API shapes. Ensure the 4-month Ramadan overlay reframing (§2) is acceptable to the wireframe author.

2. **`frontend-design`** — For building the Vizro page layout: `vm.Container` grid spec, `vm.Card` action window styling, `vm.Flex` column layout, matching the Page 1 visual rhythm.

3. **`verification-before-completion`** — Run the smoke tests in §11 below. Do NOT run `dashboard/app.py` (blocks forever, per AGENTS.md).

4. **`polish`** — Final quality pass: alignment, color consistency with Page 1 (`COMMODITY_COLORS`), heatmap color scale (single-hue per wireframe [5b], NOT the `RdYlGn_r` used in the old Dash file).

5. **`clarify`** — Review UX copy: data availability callout [4f], calendar note on heatmap [5e], 2022 outlier label [6h], per-commodity date floor disclosure (§1 — Rice/Sugar/Flour end 2020-03).

---

## Reference Artifacts (Read, Don't Duplicate)

| What | Path |
|------|------|
| Full wireframe spec | `docs/wireframes/wfp-wireframe-page2-seasonal-patterns.md` |
| Phase C handoff (infra, patterns, Day 1–4 plan) | `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md` |
| Vizro patterns (show_in_url, conditional vis, @capture) | `docs/LEARNINGS.md` §87–96 |
| **Critical Vizro bugs (Filter "All" sentinel + Parameter literal bind)** | `docs/LEARNINGS.md` §97, §98 |
| Page 1 reference (working Vizro code) | `dashboard/pages/price_trends.py` + `dashboard/charts/*.py` |
| `_build_*` Markdown card helper pattern | `dashboard/pages/price_trends.py:16-56` |
| Old Dash code (contents reference only — DELETE after rewrite) | `dashboard/pages/seasonal_patterns.py` |
| Raw data schema (legacy — NOT used by Vizro) | `dashboard/public/data/seasonal_patterns.json` |
| **Primary dbt mart for Page 2** | `transform/models/marts/mart_price_trends_national.sql` |
| Secondary mart (island-disaggregated Cooking Oil) | `transform/models/marts/mart_seasonal_patterns.sql` |
| Islamic calendar lookup | `transform/seeds/islamic_calendar.csv` + `int_islamic_calendar` dbt model |
| Data access layer (reusable helpers — extend with §5 functions) | `dashboard/data_access.py` |
| Vizro data registration (already complete — do not modify) | `dashboard/data_manager.py` |
| Vizro spike (minimal `px.imshow` reference) | `dashboard/spike/custom_charts.py` |
| Data constraints (Cooking Oil only at island level) | `AGENTS.md` "Known Limitations" table |

## Do NOT Modify

| Item | Reason |
|------|--------|
| `dashboard/data_access.py` (existing functions) | Framework-agnostic, reused by all pages. **Extending** with §5 helpers is allowed; do not change existing function signatures. |
| `dashboard/data_manager.py` | Already correct, registers all 6 marts + forecast |
| `transform/` (any dbt model) | Complete, 77 tests pass — re-running dbt is fine; editing models is out of scope |
| `export/export_json.py` | Complete, verified — `seasonal_patterns.json` is exported here but Vizro does not consume it |
| `forecast/run_forecast.py` | Complete |
| `dashboard/charts/*.py` for Page 1 | Do not touch — Page 1 working code |
| `dashboard/pages/price_trends.py` | Do not touch — Page 1 working code |
| `docs/wireframes/*` | Reference only — do NOT edit even if §2 (`week_relative` → `month_relative`) feels like a contradiction; surface the deviation in the PR description |

---

## 8. Page Registration (one-line wiring task — easy to miss)

After creating `dashboard/pages/seasonal_patterns.py` exporting `seasonal_patterns_page = vm.Page(...)`:

Edit `dashboard/app.py` at lines 16, 19:

```python
# Add to imports
from dashboard.pages.seasonal_patterns import seasonal_patterns_page

# Add to dashboard pages list
dashboard = vm.Dashboard(
    pages=[price_trends_page, seasonal_patterns_page],
)
```

Vizro auto-builds the top navigation bar from `pages`. The wireframe nav `[1]` will render automatically; no extra `vm.NavBar` config required. Page order in the `pages=` list determines navigation order.

---

## 9. Data Source Map — Which Mart Drives Which Component

| Wireframe element | Primary source | Secondary source (filter-dependent) | Pre-compute function (§5) |
|-------------------|----------------|--------------------------------------|----------------------------|
| Action cards [4] | `mart_price_trends_national` | `mart_seasonal_patterns` (when Island Group ≠ All AND Commodity = Cooking Oil) | `compute_action_windows(...)` |
| Data availability notice [4f] | None — static `vm.Card` markdown | — | — |
| Heatmap [5] | `mart_price_trends_national` (all 4 commodities at national level) | — (ignore island filter; show all 4 rows always) | `compute_heatmap_matrix(...)` |
| Ramadan overlay [6] | `mart_price_trends_national` + `int_islamic_calendar` | — (commodity selector inside the chart toolbar drives which lines render) | `compute_ramadan_overlay(...)` |
| Harvest chart [7] | `mart_price_trends_national` (Rice only — filter inside the chart fn) | — | inline; reuse `compute_heatmap_matrix` then slice to Rice |
| Year-End chart [8] | `mart_price_trends_national` (all 4 commodities, Nov–Dec only) | — | inline; reuse `compute_action_windows(driver="Year-End")` |
| Summary table [9] | `mart_price_trends_national` | — | `compute_action_windows(...)` called 3× (one per driver), concatenated |

Register all needed data on the page via `vm.Page` `components=[vm.Graph(figure=fn(data_frame="mart_price_trends_national"))]`. Vizro's `data_manager` already exposes both marts (see `dashboard/data_manager.py:11-18`).

---

## 10. Chart Function Signatures (Concrete API per File)

All chart functions follow the Page 1 pattern: `@capture("graph")`, accept `data_frame: pd.DataFrame` as the first arg, plus `vm.Parameter`-driven kwargs with sensible defaults (per LEARNINGS §98). All return `go.Figure`.

```python
# charts/seasonal_heatmap.py
@capture("graph")
def seasonal_heatmap(
    data_frame: pd.DataFrame,         # mart_price_trends_national
    commodity_filter: str = "All",     # dims non-matching rows
) -> go.Figure: ...

# charts/ramadan_overlay.py
@capture("graph")
def ramadan_overlay(
    data_frame: pd.DataFrame,         # mart_price_trends_national
    commodity_filter: str = "All",
    driver: str = "All",               # returns empty fig if driver != "Ramadan"
) -> go.Figure: ...

# charts/harvest_chart.py
@capture("graph")
def harvest_chart(
    data_frame: pd.DataFrame,
    driver: str = "All",               # returns empty fig if driver != "Harvest"
) -> go.Figure: ...

# charts/yearend_chart.py
@capture("graph")
def yearend_chart(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
    driver: str = "All",               # returns empty fig if driver != "Year-End"
) -> go.Figure: ...

# charts/seasonal_summary_table.py
# Returns vm.AgGrid via @capture("ag_grid") — NOT @capture("graph")
@capture("ag_grid")
def seasonal_summary_table(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
) -> "pd.DataFrame": ...   # AgGrid wraps the returned DataFrame
```

Empty-figure helper (use across the 3 conditional charts per §3 Pattern A):

```python
def _empty_collapsed_fig() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        height=1,
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
```

---

## 11. Smoke Tests (Run Before Claiming Done)

```bash
# 1. Vizro picks up Page 2 — must print 2
uv run python -c "from dashboard.app import dashboard; print(len(dashboard.pages))"

# 2. Page 2 ID present
uv run python -c "from dashboard.app import dashboard; print([p.title for p in dashboard.pages])"
# Expect: ['Price Trends & Forecast', 'Seasonal Patterns']

# 3. Each chart function builds without error (uses Page 1 data — just smoke test the import + render path)
uv run python -c "
from dashboard.charts.seasonal_heatmap import seasonal_heatmap
from dashboard.data_access import load_mart
fig = seasonal_heatmap(load_mart('mart_price_trends_national'))
print('heatmap traces:', len(fig.data))
"

# 4. Pre-compute helpers (§5) work end-to-end
uv run python -c "
from dashboard.data_access import load_mart, compute_action_windows
import duckdb
cal = duckdb.connect('data/wfp.duckdb', read_only=True).execute('SELECT * FROM wfp_intermediate.int_islamic_calendar').fetchdf()
df = compute_action_windows(load_mart('mart_price_trends_national'), 'Ramadan', cal)
print(df)
"

# 5. dbt unchanged — sanity check (optional; only if you touched any model)
cd transform && dbt build && cd ..

# 6. Manual: launch dashboard, navigate Page 1 → Page 2, confirm filter URL state persists
# uv run python dashboard/app.py  # HUMAN USE ONLY — blocks forever per AGENTS.md
```

Acceptance bar: smoke tests 1–4 pass without exception, output matches expected values.

---

## 12. Top Pitfalls (Will Bite Page 2 If Ignored)

1. **`vm.Filter` with "All" option silently empties the dataset** (LEARNINGS §97). Use `vm.Parameter` for any Dropdown containing "All".
2. **`vm.Graph(figure=fn(commodity_filter="commodity_filter"))` shows "No data" on first render** (LEARNINGS §98). Pass only `data_frame=`; rely on function default.
3. **`mart_seasonal_patterns` has only 35 rows / Cooking Oil only / 7 months** (§1 above). Use `mart_price_trends_national` as primary source.
4. **Rice/Sugar/Flour national prices end at 2020-03** (§1). The heatmap and summary table must either disclose this or apply `WHERE month <= '2020-03-01'` when computing per-commodity means to avoid biased index calculations.
5. **dbt `int_prices_normalised.month` is monthly, not weekly** (§2). Wireframe [6d] "T-8 to T+6 weeks" cannot be honored at original granularity; reframe as months T-2 to T+1.
6. **`vm.AgGrid` requires `@capture("ag_grid")`, not `@capture("graph")`** (§10). Mixing these silently produces a broken table.
7. **Dash callbacks coexist with Vizro but require `Vizro().build(dashboard).app.callback(...)`** (LEARNINGS §96), not bare `@callback`. Only relevant if you choose Pattern B over Pattern A in §3.
8. **`COMMODITY_COLORS` must match Page 1 exactly** (`#4C72B0`, `#DD8452`, `#55A868`, `#C44E52`). Centralize in `dashboard/charts/__init__.py` if you find yourself copy-pasting — current Page 1 charts duplicate it (acceptable for now per AGENTS.md "no premature abstraction").

---

## 13. Old Dash File Disposition

`dashboard/pages/seasonal_patterns.py` currently contains 222 lines of Dash code (registers `dash.register_page`, defines `dcc.Graph` + `dbc.Container`, uses `dash.callback`). Per Phase C handoff "User chose option (A): Rewrite in place," this file should be **overwritten** with the new Vizro `vm.Page` config. The git history preserves the Dash version.

`dashboard/components/filters.py`, `kpi_cards.py`, `layout.py` are Dash-era helpers used by the old Page 2. After Page 2 + Pages 3–4 are rewritten, these become dead code and should be deleted (Phase C handoff lines 42–44 marks them ⬜ "Retire"). Do **not** delete them while Pages 3–4 still import them.

---

## Gap-Fix Notes (2026-06-04 verification pass)

Original handoff (timestamp 14:22) contained these errors / omissions, now corrected:

| # | Original claim | Correction | Source of truth |
|---|----------------|------------|-----------------|
| 1 | `seasonal_patterns.json` has 597 records | 35 records (Cooking Oil only, 5 islands × 7 months in 2024) | Direct DuckDB query of `wfp_marts.mart_seasonal_patterns` + file inspection |
| 2 | "No pipeline change needed" with mart_seasonal_patterns as source | Pipeline OK; **source choice** was wrong — use `mart_price_trends_national` for cross-commodity views | DuckDB row counts + `transform/models/marts/*.sql` review |
| 3 | "Compute `week_relative` as `(month_date - eid_date) // 7`" | Source data is monthly; compute `month_relative` instead, range T-2 to T+1 | `int_prices_normalised` schema; `mart_price_trends_national` grain |
| 4 | `charts/seasonal_action_cards.py` modeled on `kpi_sparklines.py` | Action cards are `vm.Card` markdown components, not Plotly figures — pattern from `_build_model_info_card` in Page 1 | `dashboard/pages/price_trends.py:16-56` |
| 5 | Summary table "fallback: `go.Table`" | Wireframe [9e] specifies AG Grid; Vizro 0.1.x exposes `vm.AgGrid` (verified) | `dir(vizro.models)` + wireframe |
| 6 | `vm.Filter` for the 3 global filters | `vm.Parameter` for the 2 "All"-bearing dropdowns; `vm.Filter` only for the numeric Year Range | LEARNINGS §97, §98 |
| 7 | LEARNINGS §87–96 cited | §97 and §98 (Page 1 production bugs) **must** be cited; they will recur on Page 2 | LEARNINGS §97-98 |
| 8 | Skill name "`verify`" | Actual skill name is `verification-before-completion` | Skill registry |
| 9 | No instruction to update `dashboard/app.py` | Added §8 — must add import + `pages=` entry | `dashboard/app.py:16,19` |
| 10 | No concrete chart function signatures | Added §10 — explicit signatures for all 5 chart files | Page 1 conventions |
| 11 | No smoke test for Page 2 (only Phase C handoff's generic test) | Added §11 with 6 specific tests | — |
| 12 | No mention of `mart_price_trends_national` per-commodity date floor | Added pitfall #4 — Rice/Sugar/Flour end 2020-03 | DuckDB query |
| 13 | No mention of old Dash component files (filters.py / kpi_cards.py / layout.py) lifecycle | Added §13 — keep until Pages 3–4 are rewritten | Phase C handoff §31-44 |
| 14 | Heatmap reference cited `trend_forecast.py` (wrong — it's a line chart) | Cited `dashboard/spike/custom_charts.py:lag_heatmap` (the actual `px.imshow` reference) | Spike code review |
| 15 | No conditional-visibility trade-off discussion | Added §3 table comparing Patterns A / B / C with explicit pick (A) | LEARNINGS §96 |
