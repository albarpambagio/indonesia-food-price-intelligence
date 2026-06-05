# Marimo Architecture Overview — WFP Food Price Intelligence Dashboard
**Structure:** Single multi-tab notebook (`app.py`)
**Charting:** Plotly (`mo.ui.plotly`)
**Data:** Real JSON files in `data/`

---

## File Structure

```
project/
├── app.py                          ← single marimo notebook (all 4 tabs)
├── data/
│   ├── price_trends.json
│   ├── forecast.json
│   ├── seasonal_patterns.json
│   ├── geographic_disparity.json
│   └── commodity_correlation.json
└── dashboard/
    └── assets/
        └── indonesia_island_groups.geojson
```

---

## Cell Execution Order (simplified DAG)

```
imports
    ↓
data_loading (all 5 JSON files)
    ↓
global_filters                 ← commodity_dd, island_dd, year_slider
    ↓                                   ↑ shared by all 4 tabs
    ├── page1_cells ─────────────────────┤
    ├── page2_cells ─────────────────────┤
    ├── page3_cells ─────────────────────┤
    └── page4_cells ─────────────────────┘
            ↓
        tabs_cell              ← mo.ui.tabs({...})
```

---

## The Tabs Cell

```python
@app.cell
def _(page1_content, page2_content, page3_content, page4_content, mo):
    tabs = mo.ui.tabs({
        "Price Trends": page1_content,
        "Seasonal": page2_content,
        "Geographic": page3_content,
        "Commodity Signals": page4_content,
    })
    tabs
    return (tabs,)
```

The tab contents (`page1_content`, etc.) are assembled in each page's
assembly cell and passed here by name. Global filters sit above this cell
and are read by all page cells — no `dcc.Store` needed.

---

## Global Filters (defined once, used everywhere)

```python
@app.cell
def _(mo):
    commodity_dd = mo.ui.dropdown(
        options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
        value="All", label="Commodity",
    )
    island_dd = mo.ui.dropdown(
        options=["All", "Java", "Sumatera", "Kalimantan",
                 "Sulawesi", "Eastern Indonesia"],
        value="All", label="Island Group",
    )
    year_slider = mo.ui.range_slider(
        start=2007, stop=2024, value=[2007, 2024], step=1, label="Year Range",
    )
    mo.hstack([commodity_dd, island_dd, year_slider], gap="1rem")
    return commodity_dd, island_dd, year_slider
```

These three widgets are rendered once above the tabs. Each page's cells receive
them as function arguments — marimo's DAG handles the wiring automatically.

**Per-page filter behaviour:**

| Filter | Page 1 | Page 2 | Page 3 | Page 4 |
|---|---|---|---|---|
| Commodity | Filters trend chart + YoY table | Filters action cards | Switches map to N/A state for non-Oil | Reduces correlation matrix |
| Island Group | Applies to Cooking Oil data only | Applies to Cooking Oil seasonal only | Filters province drill-down | Disabled (callout explains) |
| Year Range | Filters all charts + YoY table | Filters summary table | Filters map year range | Filters correlation period |

---

## `mo.state()` Usage (only where warranted)

Two places use `mo.state()` — both for bidirectional sync (multiple UI inputs
writing to one shared value):

| State | Page | Sources | Consumers |
|---|---|---|---|
| `selected_island` | Page 3 | KPI card buttons, choropleth map click | Province drill-down table |
| `selected_pair` | Page 4 | Matrix click, pair dropdowns, detail table row click | Scatter chart, stability chart, implication card |

All other reactivity flows through marimo's normal DAG (widget `.value` as
cell arguments). `mo.state()` is only used where two different UI elements must
write to the same piece of state.

---

## Running the App

```bash
# Interactive (browser)
uv run marimo run app.py

# Edit mode
uv run marimo edit app.py

# Lint check before shipping
uvx marimo check app.py
```

---

## Dependencies (`app.py` header)

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.20.4",
#     "pandas",
#     "plotly",
#     "numpy",
# ]
# ///
```

---

## What Was Dropped vs Original Spec (and Why)

| Original feature | Status | Reason |
|---|---|---|
| Map year animation (`dcc.Interval`) | Phase 2 | marimo has no native interval; manual slider ships first |
| AG Grid cell background colors | Simplified | `mo.ui.table` + emoji flags for MVP; `mo.Html` table for Phase 2 |
| Island Group dropdown disabled on Page 4 | Changed | Global widget stays enabled; callout explains no effect — avoids breaking shared state |
| Vizro dark/light theme swap | Replaced | marimo built-in dark mode; remove explicit `font.color` from Plotly annotations |
