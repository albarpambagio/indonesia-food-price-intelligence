# Handoff: Dashboard Marimo Rewrite (Native UI, No Vizro Patterns)

**Generated:** 2026-06-08 (updated — added data shapes, dual-path code, cross-cell scoping, Page4 sync mechanism, validation failure modes)
**Trigger:** Agent was asked to plan and prepare execution of a full Marimo-native dashboard rewrite, replacing Vizro-derived visual hacks with proper Marimo UI components (`mo.stat()`, `mo.callout()`, etc.).

---

## Context

Previous handoff (`docs/handoffs/HANDOFF-vizro-to-marimo-migration.md`) already migrated from Vizro/Dash to a single Marimo notebook (`dashboard/app.py`). Chart functions still carried old patterns that look "very bad visually":

- **KPI cards** via Plotly `make_subplots` with annotation text overlays
- **Signal badges** via Plotly annotations on an invisible chart
- **Action cards** via Plotly annotations with background/border colors
- **YoY bar chart** replaced by `mo.ui.table` with emoji indicators (per wireframes)
- **Info boxes** via `mo.md("> ...")` blockquotes
- **Last cell bug**: `mo.hstack` + `mo.ui.tabs` were intermediate expressions, not final

User created detailed wireframes at `docs/wireframes/marimo-wireframe-*.md` (5 files). This handoff incorporates all wireframe-driven architecture decisions.

---

## Architecture (Per Wireframes)

### File Layout at Runtime (WASM)

```
dist/
├── index.html          ← marimo export html-wasm output
├── data/               ← copied from dashboard/public/data/
│   ├── price_trends.json
│   ├── forecast.json
│   ├── seasonal_patterns.json
│   ├── geographic_disparity.json
│   ├── commodity_correlation.json
│   └── correlation_summary.json
└── assets/
    └── indonesia_provinces.geojson
```

### Cell DAG (Granular — Not Monolithic)

```
imports
    ↓
data_loading (8 JSONs + islamic calendar CSV)
    ↓
global_filters          ← commodity_dd, island_dd, year_slider
    ↓
    ├── Page 1 cells:
    │   ├── page1_derived_data       ← filters + computes latest/yoy
    │   ├── kpi_cards                ← mo.stat() × 4 + sparkline charts
    │   ├── chart_commodity_radio    ← mo.ui.radio local to trend chart
    │   ├── trend_chart              ← mo.ui.plotly(go.Figure) with forecast
    │   ├── buy_signal_monitor       ← mo.md() with colored dots (native)
    │   ├── yoy_table                ← mo.ui.table with emoji flags
    │   └── footnote                 ← mo.callout(kind="info")
    │
    ├── Page 2 cells:
    │   ├── driver_toggle            ← mo.ui.radio (Ramadan/Harvest/Year-End/All)
    │   ├── action_cards             ← mo.stat() with mo.hstack()
    │   ├── data_notice              ← mo.callout(kind="info")
    │   ├── gregorian_heatmap        ← go.Heatmap(colorscale="Blues")
    │   ├── driver_chart             ← if/elif pattern: ramadan/harvest/yearend
    │   └── summary_table            ← mo.ui.table(sortable=True)
    │
    ├── Page 3 cells:
    │   ├── selected_island_state    ← mo.state("All") — cross-filter
    │   ├── kpi_cards_map            ← mo.ui.button(on_click=set_selected_island) × 5
    │   ├── map_year_slider          ← mo.ui.slider(2007–2024)
    │   ├── choropleth_map           ← mo.ui.plotly(px.choropleth)
    │   ├── island_line_chart        ← mo.ui.plotly(go.Scatter)
    │   └── province_table           ← mo.ui.table filtered by selected_island
    │
    ├── Page 4 cells:
    │   ├── selected_pair_state      ← mo.state(("Rice","Oil"))
    │   ├── lag_selector             ← mo.ui.radio({0,1,2,3})
    │   ├── leading_indicator_cards  ← mo.hstack(mo.vstack styled cards)
    │   ├── correlation_matrix       ← mo.ui.plotly(go.Heatmap)
    │   ├── pair_selector_dd         ← leader_dd + follower_dd → sync to state
    │   ├── pair_scatter             ← mo.ui.plotly(go.Scatter) pre/post 2022
    │   ├── stability_chart          ← mo.ui.plotly(go.Scatter) rolling r
    │   ├── implication_card         ← mo.callout(kind="warn"/"info")
    │   └── detail_table             ← mo.ui.table(on_select=...) → sync to state
    │
    └── tab_assembly_cell           ← mo.ui.tabs({4 tabs}) as FINAL expression
```

### mo.state() Usage (Two Instances)

| State | Page | Sources | Consumers | Why mo.state() |
|-------|------|---------|-----------|----------------|
| `selected_island` | 3 | KPI button `on_click`, choropleth map click | Province drill-down table | Two UI elements write to one shared value |
| `selected_pair` | 4 | Matrix click, pair dropdowns, table `on_select` | Scatter, stability, implication card | Three UI sources → one sink |

All other reactivity flows through marimo's normal DAG (widget `.value` as cell arguments).

---

## Data Contract — All DataFrame Shapes

Six JSON files are loaded at startup. Below are the exact schemas. An agent writing downstream cells (derived_data, chart assembly) must use these column names — one mismatch fails silently until `marimo check`.

### 1. `price_trends.json` → `price_trends_df`

**Source:** `wfp_marts.mart_price_trends` (export/export_json.py:22-24)
**Rows:** ~2,100+ · 17 years × 4 commodities × ~31 provinces
**Order by:** `month, commodity_consolidated, island_group, admin1`

| Column | Type | Notes |
|--------|------|-------|
| `month` | str `"YYYY-MM-DD"` | Truncated to 1st of month |
| `commodity_consolidated` | str | `Rice` / `Cooking Oil` / `Sugar` / `Flour` |
| `island_group` | str | `Java` / `Sumatera` / `Kalimantan` / `Sulawesi` / `Eastern Indonesia` |
| `admin1` | str | Province name |
| `market_count` | int | `COUNT(DISTINCT market_id)` |
| `avg_price_idr` | float | `AVG(price_idr)` |
| `avg_price_usd` | float | `AVG(price_usd)` |
| `min_price_idr` | float | `MIN(price_idr)` |
| `max_price_idr` | float | `MAX(price_idr)` |

### 2. `forecast.json` → `forecast_df`

**Source:** `forecast/run_forecast.py` JSON output (envelope: `{"metadata": {...}, "data": [...]}`)
**Rows:** ~819 (combined historical + 6mo forecast × 4 commodities)
**Usage:** Extract data array: `pd.DataFrame(json.loads(path.read_text())["data"])`

| Column | Type | Notes |
|--------|------|-------|
| `date` | str `"YYYY-MM-DD"` | Always present |
| `commodity` | str | `Rice` / `Cooking Oil` / `Sugar` / `Flour` |
| `actual_price` | float or None | Historical records only; None for forecast rows |
| `forecast_price` | float or None | Forecast records only (6 months); None for historical |
| `lower_95` | float or None | Forecast only — 95% CI lower bound |
| `upper_95` | float or None | Forecast only — 95% CI upper bound |
| `model_used` | str or None | `AutoARIMA` / `AutoETS`; None for historical |
| `scenario` | str or None | `post2022_robustness` only for Cooking Oil robustness check |

### 3. `seasonal_patterns.json` → `seasonal_patterns_df`

**Source:** `wfp_marts.mart_seasonal_patterns` (export/export_json.py:32-34)
**Rows:** ~35 (Cooking Oil only, 5 islands × ~7 months in 2024)
**Order by:** `month, commodity_consolidated, island_group`

| Column | Type | Notes |
|--------|------|-------|
| `month` | str `"YYYY-MM-DD"` | Base grain |
| `commodity_consolidated` | str | Normalised name |
| `island_group` | str | Geographic group |
| `avg_price` | float | Monthly avg price IDR |
| `annual_avg_price` | float | Yearly avg for index calc |
| `price_index` | float | `(avg_price / annual_avg_price) * 100` |
| `month_of_year` | int | 1–12 |
| `flag_harvest_mar_apr` | bool | Month in (3,4) |
| `flag_harvest_aug_sep` | bool | Month in (8,9) |
| `flag_year_end` | bool | Month in (11,12) |
| `flag_ramadan_eid_month` | bool | Month matches Eid |
| `flag_ramadan_t_minus_1` | bool | 1 month before Eid |
| `flag_ramadan_t_minus_2` | bool | 2 months before Eid |
| `flag_ramadan_t_minus_3` | bool | 3 months before Eid |
| `flag_ramadan_t_plus_1` | bool | 1 month after Eid |

### 4. `geographic_disparity.json` → `geographic_disparity_df`

**Source:** `wfp_marts.mart_geo_disparity` (export/export_json.py:37-39)
**Rows:** ~500+
**Order by:** `year, commodity_consolidated, island_group, admin1`

| Column | Type | Notes |
|--------|------|-------|
| `year` | int | `EXTRACT(YEAR FROM date)` |
| `commodity_consolidated` | str | Normalised name |
| `island_group` | str | Geographic group |
| `admin1` | str | Province name |
| `avg_price_idr` | float | Annual avg price |
| `months_with_data` | int | Data completeness |
| `java_avg_price` | float | Java baseline for same year/commodity |
| `price_index_vs_java` | float | `(avg_price_idr / java_avg_price) * 100`; Java = 100 |
| `yoy_change_index` | float or None | Year-over-year change in index; None for first year per partition |

### 5. `commodity_correlation.json` → `commodity_correlation_df`

**Source:** `wfp_marts.mart_commodity_correlation` (export/export_json.py:42-44)
**Rows:** ~200+
**Order by:** `month`

| Column | Type | Notes |
|--------|------|-------|
| `month` | str `"YYYY-MM-DD"` | One row per month |
| `rice_price` | float | National avg price for Rice |
| `oil_price` | float | National avg price for Cooking Oil |
| `sugar_price` | float | National avg price for Sugar |
| `flour_price` | float | National avg price for Flour |
| `rice_lag1` | float | Rice price lagged 1 month |
| `rice_lag2` | float | Rice price lagged 2 months |
| `rice_lag3` | float | Rice price lagged 3 months |
| `oil_lag1` | float | Oil price lagged 1 month |
| `oil_lag2` | float | Oil price lagged 2 months |
| `oil_lag3` | float | Oil price lagged 3 months |
| `sugar_lag1` | float | Sugar price lagged 1 month |
| `sugar_lag2` | float | Sugar price lagged 2 months |
| `sugar_lag3` | float | Sugar price lagged 3 months |
| `flour_lag1` | float | Flour price lagged 1 month |
| `flour_lag2` | float | Flour price lagged 2 months |
| `flour_lag3` | float | Flour price lagged 3 months |

### 6. `correlation_summary.json` → `correlation_summary_df`

**Source:** `wfp_marts.mart_correlation_summary` (export/export_json.py:47-49)
**Rows:** 24 (6 pairs × 4 lags)
**Order by:** `commodity_pair, lag_months`

| Column | Type | Notes |
|--------|------|-------|
| `commodity_pair` | str | Format `"rice-oil"` — alphabetical order, dash-separated |
| `lag_months` | int | 0, 1, 2, or 3 |
| `pearson_r` | float | Full-period Pearson r, rounded 4 decimals |
| `pearson_r_pre_2022` | float | Pre-2022-01-01 correlation, rounded 4 decimals |
| `pearson_r_post_2022` | float | From 2022-01-01 onward, rounded 4 decimals; None if no data |
| `rank_for_commodity` | int | `ROW_NUMBER()` per first commodity ordered by `ABS(pearson_r) DESC` |

### 7. `action_windows_df` (computed — not a JSON file)

**Source:** `compute_action_windows()` function (to be written in `data_access.py`)
**Derived from:** `mart_price_trends_national` + `islamic_calendar_df`

| Column | Type | Notes |
|--------|------|-------|
| `commodity` | str | Normalised commodity name |
| `driver` | str | `"Ramadan"` / `"Harvest"` / `"Year-End"` |
| `spike_pct` | float | `(mean(driver months) - mean(non-driver)) / mean(non-driver) * 100` |
| `consistency_score` | float | `count(years with effect) / total_years` |
| `total_years` | int | Years with data for this driver |
| `lead_months` | str | Human-readable: `"2 months before Eid"` etc. |
| `data_scope` | str | `"national"` or `"island"` |

**Filtering rule:** Only rows where `abs(spike_pct) > 3` appear in action cards.

### 8. `islamic_calendar_df`

**Source:** `transform/seeds/islamic_calendar.csv`
**Rows:** 18 (2007–2024)

| Column | Type | Notes |
|--------|------|-------|
| `year` | int | Gregorian year |
| `ramadan_start` | str `"YYYY-MM-DD"` | Start of Ramadan |
| `eid_date` | str `"YYYY-MM-DD"` | Date of Eid al-Fitr |
| `source` | str | `"IslamicFinder.org (calculated)"` |
| `eid_month` | str `"YYYY-MM"` | Computed: `STRFTIME(eid_date, '%Y-%m')` |
| `t_minus_1` | str | One month before Eid |
| `t_minus_2` | str | Two months before Eid |
| `t_minus_3` | str | Three months before Eid |
| `t_plus_1` | str | One month after Eid |

---

## Dual-Path Resolution (`data_static.py`)

This file must resolve JSON paths correctly in **both** local dev (relative to `dashboard/`) and WASM (relative to `dist/`). The exact pattern:

```python
# dashboard/data_static.py
from pathlib import Path

def _get_data_dir() -> Path:
    """Return Path to data directory regardless of runtime environment.
    
    Resolution logic:
    - Local dev: Path(__file__).parent / "public" / "data"
      (e.g., /home/.../dashboard/public/data/)
    - WASM: "data" directory is relative to the HTML file.
      Marimo's WASM mode runs with a different CWD. We detect WASM
      by checking if the expected local path exists. If not, fall
      back to "data" (relative to index.html).
    
    Build script (build.py) copies dashboard/public/data/* to dist/data/.
    """
    local_path = Path(__file__).resolve().parent / "public" / "data"
    if local_path.exists():
        return local_path
    # WASM fallback: data/ is relative to index.html
    return Path("data")


DATA_DIR = _get_data_dir()


def load_json(filename: str) -> list[dict]:
    import json
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def load_json_envelope(filename: str, key: str = "data") -> list[dict]:
    """For forecast.json which has {"metadata":..., "data": [...]} envelope."""
    import json
    raw = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
    return raw[key]


def load_csv(filename: str) -> "pd.DataFrame":
    import pandas as pd
    return pd.read_csv(DATA_DIR / filename)
```

**Do NOT hardcode `dashboard/` paths.** Do NOT use `os.getcwd()`. The `Path(__file__)` anchor is the only reliable root for both environments. The WASM build copies `dashboard/public/data/` to `dist/data/`, so the `Path("data")` fallback resolves from the index.html directory.

**Source of pattern:** `analysis/eda.py:91` uses `Path(__file__).resolve().parent.parent / "data" / "wfp.duckdb"`. This is the same `Path(__file__)` anchor convention.

---

## Cross-Cell Scoping Model

Marimo's reactive DAG means variables returned from one cell are available in downstream cells. Below is the complete export map. Every name here crosses a cell boundary — `ty` will report "unresolved reference" for all of them (this is expected, safe to ignore).

### Cell: `imports`
```
→ mo,                          # marimo
  go,                          # plotly.graph_objects
  px,                          # plotly.express
  pd,                          # pandas
  np,                          # numpy
  Path,                        # pathlib
  json,                        # json
```

### Cell: `data_loading`
```
→ price_trends_df,             # pd.DataFrame — from price_trends.json
  forecast_df,                 # pd.DataFrame — from forecast.json["data"]
  seasonal_patterns_df,        # pd.DataFrame — from seasonal_patterns.json
  geographic_disparity_df,     # pd.DataFrame — from geographic_disparity.json
  commodity_correlation_df,    # pd.DataFrame — from commodity_correlation.json
  correlation_summary_df,      # pd.DataFrame — from correlation_summary.json
  islamic_calendar_df,         # pd.DataFrame — from islamic_calendar.csv
```

### Cell: `global_filters`
```
→ commodity_dd,                # mo.ui.dropdown — All/Rice/Cooking Oil/Sugar/Flour
  island_dd,                   # mo.ui.dropdown — All/Java/Sumatera/...
  year_slider,                 # mo.ui.range_slider — 2007–2024
```

### Page 1 cells:

| Cell | Exported names |
|------|---------------|
| `page1_derived_data` | `filtered_df`, `latest_prices_df`, `yoy_df` |
| `kpi_cards_page1` | `kpi_cards_output` (mo.hstack) |
| `chart_commodity_radio` | `chart_commodity_radio` (mo.ui.radio) |
| `trend_chart` | `trend_chart_output` (mo.ui.plotly) |
| `buy_signal_monitor` | `buy_signal_output` (mo.md) |
| `yoy_table` | `yoy_table_output` (mo.ui.table) |
| `footnote` | `footnote_output` (mo.callout) |
| `page1_tab_content` | `page1_content` (mo.vstack) |

### Page 2 cells:

| Cell | Exported names |
|------|---------------|
| `page2_derived_data` | `action_windows_df`, `gregorian_heatmap_df`, `ramadan_overlay_df`, `harvest_index_df`, `yearend_premium_df`, `summary_df` |
| `driver_toggle` | `driver_toggle` (mo.ui.radio) |
| `action_cards` | `action_cards_output` (mo.vstack) |
| `data_notice` | `data_notice_output` (mo.callout) |
| `gregorian_heatmap` | `heatmap_output` (mo.ui.plotly) |
| `driver_chart` | `driver_chart_output` (mo.ui.plotly or mo.md) |
| `summary_table` | `summary_table_output` (mo.ui.table) |
| `page2_tab_content` | `page2_content` (mo.vstack) |

### Page 3 cells:

| Cell | Exported names |
|------|---------------|
| `selected_island_state` | `selected_island` (mo.state getter), `set_selected_island` (mo.state setter) |
| `kpi_cards_map` | `kpi_cards_map_output` (mo.hstack of mo.ui.button) |
| `map_year_slider` | `map_year_slider` (mo.ui.slider) |
| `choropleth_map` | `map_chart_output` (mo.ui.plotly or mo.callout) |
| `map_click_listener` | (none — side-effect cell that calls `set_selected_island`) |
| `island_line_chart` | `line_chart_output` (mo.ui.plotly) |
| `province_table` | `province_table_output` (mo.ui.table) |
| `page3_tab_content` | `page3_content` (mo.vstack) |

### Page 4 cells:

| Cell | Exported names |
|------|---------------|
| `page4_correlation_data` | `top_relationships_df`, `matrix_df`, `pairs_df`, `rolling_r_df`, `all_pairs_df` |
| `lag_selector` | `lag_selector` (mo.ui.radio) |
| `selected_pair_state` | `selected_pair` (mo.state getter), `set_selected_pair` (mo.state setter) |
| `leading_indicator_cards` | `indicator_cards_output` (mo.hstack) |
| `correlation_matrix` | `matrix_chart_output` (mo.ui.plotly) |
| `matrix_click_listener` | (none — side-effect cell that calls `set_selected_pair`) |
| `pair_selector_dd` | `leader_dd` (mo.ui.dropdown), `follower_dd` (mo.ui.dropdown) |
| `pair_dd_listener` | (none — side-effect cell that calls `set_selected_pair`) |
| `pair_scatter` | `scatter_chart_output` (mo.ui.plotly) |
| `stability_chart` | `stability_chart_output` (mo.ui.plotly) |
| `implication_card` | `implication_output` (mo.callout) |
| `detail_table` | `detail_table_output` (mo.ui.table) |
| `page4_tab_content` | `page4_content` (mo.vstack) |

### Cell: `tab_assembly` (final cell)
```
→ None — the cell body is the final expression:
  mo.ui.tabs({
    "Price Trends": page1_content,
    "Seasonal": page2_content,
    "Geographic": page3_content,
    "Commodity Signals": page4_content,
  })
```

### Scoping Rules
- Every name listed above under "→" is available as a function argument name in any downstream cell.
- `ty` will flag these as `unresolved-reference` — this is a known false positive (AGENTS.md LSP Quality table). **Always ignore ty errors on marimo cross-cell names.**
- `__` (double underscore) prefixed names are **not** exported by marimo — only use for module-level constants that no cell needs (e.g., `__COMMODITY_COLORS`).
- Single `_` prefix names are exported — use for cell-private variables you want to hide from DAG visualization without hiding from the reactive graph.

---

## Page 4 Three-Source Sync Mechanism (Most Complex Reactivity)

Three independent UI elements write to `selected_pair` state. All must converge on the same `set_selected_pair((leader, follower))` call. Here is the exact mechanism:

### Step 1: State definition (single cell, runs once)

```python
@app.cell
def _(correlation_summary_df, mo):
    default_pair = correlation_summary_df.nlargest(1, "pearson_r")
    default_leader = default_pair.iloc[0]["commodity_pair"].split("-")[0].title()
    default_follower = default_pair.iloc[0]["commodity_pair"].split("-")[1].title()
    selected_pair, set_selected_pair = mo.state((default_leader, default_follower))
    return selected_pair, set_selected_pair
```

### Step 2: Source A — Matrix heatmap click

```python
@app.cell
def _(matrix_chart_output, set_selected_pair):
    if matrix_chart_output.value and matrix_chart_output.value.get("points"):
        pt = matrix_chart_output.value["points"][0]
        leader = pt.get("y")
        follower = pt.get("x")
        if leader and follower and leader != follower:
            set_selected_pair((leader, follower))
```

This is a **side-effect cell** — it calls `set_selected_pair` but does not return any new widgets. Marimo handles this correctly as long as the cell has no final UI expression (returns nothing or a comment).

### Step 3: Source B — Pair dropdowns

Two cells work together. First, the dropdowns:

```python
@app.cell
def _(selected_pair, mo):
    leader_dd = mo.ui.dropdown(
        options=["Rice", "Cooking Oil", "Sugar", "Flour"],
        value=selected_pair()[0],        # reads current state as default
        label="Leading commodity",
    )
    follower_dd = mo.ui.dropdown(
        options=["Rice", "Cooking Oil", "Sugar", "Flour"],
        value=selected_pair()[1],        # reads current state as default
        label="Following commodity",
    )
    mo.hstack([leader_dd, mo.md("→"), follower_dd], gap="0.5rem")
    return leader_dd, follower_dd
```

Then the sync cell:

```python
@app.cell
def _(leader_dd, follower_dd, set_selected_pair):
    # Fires on every dropdown change. Prevents leader==follower.
    if leader_dd.value != follower_dd.value:
        set_selected_pair((leader_dd.value, follower_dd.value))
```

**Why two cells?** Marimo requires that the cell producing the dropdown widgets returns them first. The sync must be in a **separate downstream cell** that reads `.value` of both dropdowns — this creates the reactive dependency chain:
`dropdown widget changes → .value updates → sync cell re-runs → set_selected_pair fires → downstream cells re-run`

### Step 4: Source C — Table row click

```python
@app.cell
def _(all_pairs_df, lag_selector, set_selected_pair, mo):
    lag = lag_selector.value
    table_data = (
        all_pairs_df[all_pairs_df["lag"] == lag]
        .sort_values("r", ascending=False)
        .copy()
    )
    # Pre-format columns for display
    table_data["stability"] = table_data.apply(
        lambda r: "⚠" if abs(r["pre_2022_r"] - r["post_2022_r"]) > 0.2 else "✅",
        axis=1,
    )
    mo.ui.table(
        table_data[["leader", "follower", "lag", "r", "pre_2022_r", "post_2022_r", "stability"]],
        sortable=True,
        on_select=lambda rows: (
            set_selected_pair((rows[0]["leader"], rows[0]["follower"]))
            if rows else None
        ),
    )
```

### Step 5: Consumers — all read `selected_pair()` reactively

```python
@app.cell
def _(pairs_df, selected_pair, mo):
    leader, follower = selected_pair()
    pair_data = pairs_df[
        (pairs_df["leader"] == leader) & (pairs_df["follower"] == follower)
    ]
    # ... build scatter chart ...

@app.cell
def _(rolling_r_df, selected_pair, mo):
    leader, follower = selected_pair()
    # ... build stability chart ...

@app.cell
def _(all_pairs_df, selected_pair, lag_selector, mo):
    leader, follower = selected_pair()
    # ... build implication card ...
```

### Key constraints on this pattern:
- `leader_dd` and `follower_dd` must NOT have `leader != follower` guard inside the same cell that creates them — the guard goes in the downstream sync cell.
- The sync cell must read both `.value` attributes — declaring them as function arguments is sufficient for marimo's DAG to track dependencies.
- All three sources call `set_selected_pair((leader, follower))` with the same tuple shape — no partial state updates.
- `selected_pair()` is called (not `selected_pair` without parens) — mo.state returns a callable getter.

---

## Per-Page Wireframe Details

### Page 1 — Price Trends

| Section | Component | Implementation |
|---------|-----------|---------------|
| KPI cards | `mo.hstack` of `mo.stat()` | `mo.stat(value=f"Rp {price:,.0f}", label="Rice", caption="↑ +3.2% YoY", bordered=True, slot=mo.ui.plotly(sparkline))`. Sparkline = tiny `go.Scatter` with axes hidden, height ~60px. Red ↑ / green ↓ via f-string |
| Trend chart | `mo.ui.plotly(go.Figure)` | Local `chart_commodity_radio` independent of global `commodity_dd`. 17yr actual line + 6mo forecast dashed + 95% CI fill. Vertical separator at forecast start. 2022 structural break annotation |
| Buy signal monitor | `mo.md()` with inline HTML | Colored dots: `● BUY NOW` (green), `● HOLD` (gray), `● WATCH` (orange). No Plotly annotations |
| YoY table | `mo.ui.table` | Annual % change per commodity. Pre-format values with emoji: `"+12.3% 🔴"`, `"-2.1% 🟢"`. Columns: year, rice_pct, oil_pct, sugar_pct, flour_pct |
| Footnote | `mo.callout(kind="info")` | Model limitations plain language |

### Page 2 — Seasonal

| Section | Component | Implementation |
|---------|-----------|---------------|
| Driver toggle | `mo.ui.radio` | Horizontal button group. Options: "Ramadan / Lebaran", "Harvest Season", "Year-End", "All Drivers". Default: Ramadan |
| Action cards | `mo.stat()` in `mo.hstack` | Reads `action_windows_df` filtered by driver. Sort by abs(spike_pct) descending. Skip rows with abs < 3% threshold. Show `🛒 Commodity: +X.X%` |
| Data notice | `mo.callout(kind="info")` | "Seasonal analysis uses national-level data for Rice, Sugar, Flour. Island breakdown for Cooking Oil only." |
| Gregorian heatmap | `go.Heatmap(colorscale="Blues", zmid=0)` | 4×12 matrix. Single-hue white→dark scale centered at zero. Text shows ±%. Always shown regardless of driver |
| Driver chart | `if/elif` in one cell | Ramadan: multi-year overlay with 17yr avg bold line. Harvest: Rice bar chart with green/blue months. Year-End: commodity premium bar chart. All Drivers: info text |
| Summary table | `mo.ui.table(sortable=True)` | Sorted by abs(premium_pct). Pre-format negatives with 🟢, positives with 🔴 |

### Page 3 — Geographic

| Section | Component | Implementation |
|---------|-----------|---------------|
| Data banner | `mo.callout(kind="warn")` | "Only Cooking Oil has province-level prices. Rice/Sugar/Flour national only." Always visible |
| KPI cards | `mo.ui.button(on_click=...)` | 5 buttons, one per island group. Java = baseline (no %). Others: `↑ X.X% vs Java` or `↓ X.X% vs Java`. Clicking calls `set_selected_island(name)` |
| Map year slider | `mo.ui.slider(2007–2024)` | Page-specific. Manual only (no animation). Animatable in Phase 2 via `mo.state` + `time.sleep()` loop |
| Choropleth map | `mo.ui.plotly(px.choropleth)` | GeoJSON from `assets/indonesia_provinces.geojson`. Colorscale="Blues". Click calls `set_selected_island(clicked)`. Not rendered for non-Oil commodities |
| Island line chart | `mo.ui.plotly(go.Scatter)` | One line per island group over time. Java dashed gray. Y-axis > 90 to show small gaps |
| Province table | `mo.ui.table` | Filtered by `selected_island()`. Shows province, island_group, avg_price, vs Java (pre-formatted with emoji), coverage date range |

### Page 4 — Commodity Signals

| Section | Component | Implementation |
|---------|-----------|---------------|
| Island notice | `mo.callout(kind="info")` | "Island Group filter disabled on this page — correlation analysis is national level." Global dropdown stays enabled |
| Lag selector | `mo.ui.radio` | Options dict: `{"0 months": 0, "1 month": 1, "2 months": 2, "3 months": 3}`. Default: 1 |
| Leading indicator cards | `mo.hstack` of `mo.vstack` styled cards | Top 2 relationships by r at selected lag. Each card: `📈 Leader → Follower`, `r = X.XX`, `✅ Stable` / `⚠ Weakened post-2022`, plain-language implication text |
| Correlation matrix | `mo.ui.plotly(go.Heatmap)` | 4×4. Row = leader, column = follower. colorscale="Blues". Diagonal = None (white). Annotation: "Row commodity leads column commodity". Click updates `selected_pair` |
| Pair scatter | `mo.ui.plotly(go.Scatter)` | Pre-2022 blue dots, Post-2022 red dots. OLS trend line. Read from `selected_pair()` |
| Rolling stability | `mo.ui.plotly(go.Scatter)` | 3yr rolling r. Horizontal line at r=0.3. Vertical line at 2022 shock |
| Pair selector dropdowns | `mo.hstack([leader_dd, "→", follower_dd])` | Reads `selected_pair()[0]` as default. Changes sync back to state via downstream cell |
| Implication card | `mo.callout(kind="warn"/"info")` | Plain language only. No r-values. ⚠ warning if `abs(pre_r - post_r) > 0.2` is non-negotiable |
| Detail table | `mo.ui.table(on_select=...)` | All pairs at selected lag. Columns: leader, follower, r, pre_2022_r, post_2022_r, stability (✅/⚠). Row click updates `selected_pair` via `on_select` |

---

## Tab Labels (Match Wireframes)

| Label | Tab Content Variable |
|-------|---------------------|
| "Price Trends" | `page1_content` |
| "Seasonal" | `page2_content` |
| "Geographic" | `page3_content` |
| "Commodity Signals" | `page4_content` |

---

## Files to Modify

| File | Change |
|------|--------|
| `dashboard/charts/kpi_sparklines.py` | Rewrite → export `sparkline_chart()` returning tiny `go.Figure` (axes hidden, ~60px height). One trace per commodity. No annotations, no subplots, no KPI text |
| `dashboard/charts/seasonal_heatmap.py` | Rewrite → use `go.Heatmap(colorscale="Blues", zmid=0)` instead of `px.imshow(RdBu_r)` |

## Files to Delete

| File | Reason |
|------|--------|
| `dashboard/charts/signal_badges.py` | Replaced by `mo.md()` with inline HTML colored dots |
| `dashboard/charts/action_cards.py` | Replaced by `mo.stat()` in `mo.hstack()` |
| `dashboard/charts/yoy_bar.py` | Replaced by `mo.ui.table` with emoji indicators |

## Files to Create

| File | Source |
|------|--------|
| `dashboard/public/data/islamic_calendar.csv` | Copy from `transform/seeds/islamic_calendar.csv` |

## Files to Keep (as-is)

| Asset | Path |
|-------|------|
| JSON data loader | `dashboard/data_static.py` |
| Pandas compute helpers (5 functions) | `dashboard/data_access.py` |
| WASM build script | `dashboard/build.py` |
| Static JSON data (7 files) | `dashboard/public/data/*.json` |
| GeoJSON | `dashboard/assets/indonesia_provinces.geojson` |
| `trend_forecast.py` | Clean Plotly — unchanged |
| `ramadan_overlay.py` | Plotly — keep (called by driver_chart assembly) |
| `harvest_chart.py` | Plotly — keep (called by driver_chart assembly) |
| `yearend_chart.py` | Plotly — keep (called by driver_chart assembly) |
| `correlation_charts.py` | Plotly — keep (all 4 functions used) |
| `geo_charts.py` | Plotly — keep (all 3 functions used) |
| `seasonal_summary_table.py` | Returns pd.DataFrame — keep |

---

## Execution Notes

- **Marimo version:** 0.23.7 — `mo.stat()`, `mo.callout()`, `mo.style()`, `mo.accordion()` all available
- **Run commands:** `uv run marimo edit dashboard/app.py` (interactive), `uv run python dashboard/app.py` (script mode)
- **WASM export:** `marimo export html-wasm dashboard/app.py -o dist/index.html --mode run -f`
- **Linting:** `ruff check dashboard/` — existing E501/F821 false positives safe to ignore
- **Type checking:** `ruff check` only; `ty` cannot resolve marimo cross-cell scoping (see Cross-Cell Scoping Model section above for the full variable name list)
- **PEP 723 header** must be at top of `app.py`
- **All chart functions already stripped of `@capture` decorators** — no Vizro dependencies remain
- **Data source constraint:** Seasonality (Page 2) and correlation (Page 4) use **national-level** data. `mart_seasonal_patterns` (seasonal_patterns.json) has only 35 rows × Cooking Oil only × 7 months — do NOT use it as the primary source for the heatmap. Use `mart_price_trends_national` (via `price_trends_national.json`, exported but not listed above — you must add this to the export or compute from `price_trends.json` filtered to national). See `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` for full analysis.
- **Rice/Sugar/Flour national price data ends 2020-03.** The heatmap and summary table must either disclose this or apply a date floor to avoid biased index calculations.
- **Final expression rule:** Every cell must have its output as the last expression (bare `chart` or `fig`, not `mo.ui.plotly(fig)` as intermediate)
- **No `if` cell guards:** Use `if/elif` pattern (assign to variable, return last) not `if` around final expression
- **No `try/except` for control flow:** Let errors surface naturally

---

## Validation — With Failure Mode Diagnosis

| Check | Command | Pass/Fail Criteria | Failure Mode: What you'll see | How to diagnose |
|-------|---------|--------------------|------------------------------|-----------------|
| Marimo check | `marimo check dashboard/app.py` | Exit code 0, no errors | "SyntaxError" or "NameError: name 'X' is not defined" | Check that all `return (x,)` names match cell function arg names. Missing `mo` import is the most common. |
| Ruff lint | `ruff check dashboard/` | Pass (E501/F821 known false positives) | E999 (syntax error) or unexpected violations | Ruff E999 means a Python syntax error — fix the syntax. Other violations are likely real issues. |
| Script mode | `uv run python dashboard/app.py` | Exits cleanly (no traceback) | `ModuleNotFoundError` or `NameError` | Missing PEP 723 dependencies or undefined cross-cell reference. Run with `--debug` to see which cell fails. |
| WASM export | `marimo export html-wasm -o /tmp/test.html --mode run -f` | Succeeds, file created | "marimo: error: argument -o: expected one argument" or WASM build timeout | Check file permissions. If build times out, too many large inline data — inline data in WASM must be <50MB total. |
| Tabs render | Load in browser | 4 tabs visible, clicking between them works | Blank page, "Waiting for data..." spinner stuck, or JS console error | Open browser DevTools → Console. Common: CSV not found (check `data_static.py` path resolution), JSON parse error. |
| Global filters | Change commodity/year/island | All charts update within ~1s | Chart doesn't re-render, shows stale data | The cell reading `commodity_dd.value` is not in the DAG. Check the cell's function signature includes the widget name. |
| Page 3 KPI card click | Click an island KPI button | Province table filters to that island | Nothing happens on click | `on_click` lambda captures the island name correctly? Check: `on_click=lambda _, g=island: set_selected_island(g)` — the `g=island` default arg capture is critical (Python closure gotcha). |
| Page 4 matrix click | Click a heatmap cell | Scatter + stability + implication update | Click does nothing; or wrong pair selected | Is `matrix_chart_output.value["points"]` populated? Test with a standalone `print(matrix_chart_output.value)` cell. Plotly click events in WASM may be unreliable — matrix click can silently fail; dropdowns and table row click are the reliable fallbacks. |
| `mo.stat()` KPI cards | View Page 1 | 4 stat cards with prices, arrows, sparklines | Cards show "None" or "NaN", sparklines invisible | Check `latest_prices_df` has data for all 4 commodities. Sparkline `go.Scatter` must have `visible=True` and non-empty x/y. |
| `mo.callout()` info boxes | View each page | Info boxes visible on all 4 pages | `mo.callout` returns empty or renders as unformatted text | Marimo 0.23.7 requires `mo.callout(content, kind=...)` — content must be `mo.md()` or string, not a bare `mo.vstack()`. |

---

## Suggested Skills

| Skill | When to Use |
|-------|-------------|
| `marimo-notebook` | When writing/editing `app.py` notebook cells — cell structure patterns, UI component reference, script mode patterns, `mo.stop()` usage |
| `systematic-debugging` | If `marimo check` fails, chart rendering issues in WASM mode, or `mo.ui.plotly()` displays incorrectly |
| `cloudflare-pages-deploy` | After WASM export succeeds — for deploying `dist/` to Cloudflare Pages |
