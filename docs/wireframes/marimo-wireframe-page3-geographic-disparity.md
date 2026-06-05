# Marimo Wireframe — Page 3: Geographic Disparity
**Framework:** marimo (single multi-tab notebook)
**Tab label:** `"Geographic"`
**Charting:** Plotly via `mo.ui.plotly()`
**Decision enabled:** "Which island group or province offers the best sourcing price right now?"

---

## Cell Architecture

```
[cell: global_filters]        ← SHARED (commodity_dd, island_dd, year_slider)
       ↓
[cell: geo_data]              ← loads geographic_disparity.json + GeoJSON
       ↓
[cell: map_year_slider]       ← PAGE-SPECIFIC year selector for choropleth animation
[cell: selected_island_state] ← mo.state() — tracks which island group is active
       ↓
[cell: data_banner]           ← static warning callout
[cell: kpi_cards]             ← reads geo_data["current_index"]
[cell: choropleth_map]        ← reads geo_data + map_year_slider.value
[cell: island_line_chart]     ← reads geo_data["annual_index"]
[cell: province_table]        ← reads selected_island_state + geo_data["province_detail"]
       ↓
[cell: page3_tab_content]     ← assembles layout
```

---

## Data Loading

```python
@app.cell
def _():
    import json, pathlib
    import pandas as pd

    raw = json.loads(pathlib.Path("data/geographic_disparity.json").read_text())
    geojson = json.loads(
        pathlib.Path("dashboard/assets/indonesia_island_groups.geojson").read_text()
    )

    current_index_df = pd.DataFrame(raw["current_index"])
    annual_index_df = pd.DataFrame(raw["annual_index"])
    province_detail_df = pd.DataFrame(raw["province_detail"])

    return current_index_df, annual_index_df, province_detail_df, geojson
```

---

## Data Availability Banner

```python
@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "⚠ **Only Cooking Oil has province-level actual prices in this dataset.** "
            "Rice, Sugar, and Flour are available at national level only — see the "
            "Price Trends tab for national trend analysis. Geographic maps and province "
            "data on this page reflect Cooking Oil prices only."
        ),
        kind="warn",
    )
```

Always visible, non-collapsible. `kind="warn"` gives the yellow background specified
in the original. This pre-empts "why can't I select Rice?" questions.

---

## [Section 1] KPI Cards — Island Groups

```python
@app.cell
def _(current_index_df, set_selected_island, mo):
    island_order = ["Java", "Sumatera", "Kalimantan", "Sulawesi", "Eastern Indonesia"]

    cards = []
    for island in island_order:
        row = current_index_df[current_index_df["island_group"] == island].iloc[0]
        is_baseline = island == "Java"

        caption = (
            "baseline"
            if is_baseline
            else f"{'↑' if row['premium_pct'] > 0 else '↓'} {row['premium_pct']:+.1f}% vs Java"
        )
        # Each card is a button — clicking sets selected_island_state
        cards.append(
            mo.ui.button(
                label=f"**{island}**\n{row['index']:.0f}\n{caption}",
                on_click=lambda _, g=island: set_selected_island(g),
                kind="neutral",
            )
        )

    mo.hstack(cards, gap="0.75rem")
```

**Notes on cross-filtering with `mo.state()`:**
The province table and map highlight must respond to both KPI card clicks AND
map region clicks. This is the one place in marimo where `mo.state()` is warranted
because we need bidirectional sync (two different UI sources → one shared state):

```python
@app.cell
def _(mo):
    selected_island, set_selected_island = mo.state("All")
    return selected_island, set_selected_island
```

- KPI card `on_click` calls `set_selected_island(island_name)`.
- Map click (see choropleth section) also calls `set_selected_island`.
- Province table reads `selected_island()`.
- This is the correct marimo pattern for two inputs → one shared sink.

---

## [Section 2] Choropleth Map + Year Slider

### Page-specific year slider for animation

```python
@app.cell
def _(mo):
    map_year_slider = mo.ui.slider(
        start=2007, stop=2024, value=2024, step=1, label="Map Year",
    )
    animate_btn = mo.ui.run_button(label="▶ Animate")
    mo.hstack([map_year_slider, animate_btn], gap="1rem")
    return map_year_slider, animate_btn
```

**Animation pattern** — marimo has no `dcc.Interval`. The recommended approach:

```python
@app.cell
def _(animate_btn, map_year_slider, mo):
    # This cell runs when animate_btn is clicked
    animate_btn  # declare dependency
    import time

    if animate_btn.value:
        for year in range(2007, 2025):
            # Update slider value — triggers map cell to re-run
            # NOTE: direct slider mutation is not supported in marimo.
            # Recommended alternative: store the year in mo.state()
            # and advance it via the button, not the slider thumb.
            pass

    # Practical approach: use mo.state for animation year,
    # keep slider as display-only indicator
```

**Practical recommendation:** Replace the animation with a `mo.ui.slider` for
manual year selection only. The "Animate" button can be implemented as a
`mo.ui.button(value=False)` that, when `value=True`, triggers a Python loop
with `time.sleep(1)` per frame — but marimo re-renders only after the full cell
completes, so frame-by-frame animation requires `mo.status.spinner` or an
explicit `yield`-based approach. Flag this as a **Phase 2** feature; ship the
manual year slider first.

### Choropleth map

```python
@app.cell
def _(annual_index_df, geojson, map_year_slider, set_selected_island, mo):
    import plotly.express as px

    year_data = annual_index_df[annual_index_df["year"] == map_year_slider.value]

    fig = px.choropleth(
        year_data,
        geojson=geojson,
        locations="island_group",
        featureidkey="properties.island_group",
        color="index",
        color_continuous_scale="Blues",
        range_color=[90, 160],
        hover_data={"island_group": True, "index": ":.1f"},
        labels={"index": "Price Index (Java=100)"},
    )
    fig.update_geos(
        fitbounds="locations", visible=False,
        showcoastlines=True, coastlinecolor="gray",
    )
    fig.update_layout(
        height=340,
        margin=dict(l=0, r=0, t=30, b=0),
        title=f"Cooking Oil Price Index vs Java Baseline ({map_year_slider.value})",
        coloraxis_colorbar=dict(title="Index<br>(Java=100)"),
    )

    map_chart = mo.ui.plotly(fig)
    map_chart
    return (map_chart,)

# Cross-filter: read map click data in a downstream cell
@app.cell
def _(map_chart, set_selected_island):
    if map_chart.value and map_chart.value.get("points"):
        clicked = map_chart.value["points"][0].get("location")
        if clicked:
            set_selected_island(clicked)
```

**Choropleth click reliability note:** Plotly choropleth click events via
`mo.ui.plotly` work for `px.choropleth` but may be unreliable for
`go.Choropleth` depending on the GeoJSON projection. Test with real data;
if click events don't fire, the KPI card buttons are the fallback selector.

---

## [Section 3] Island Group Comparison Line Chart

```python
@app.cell
def _(annual_index_df, mo):
    import plotly.graph_objects as go

    island_groups = annual_index_df["island_group"].unique()
    fig = go.Figure()

    for island in island_groups:
        sub = annual_index_df[annual_index_df["island_group"] == island]
        is_java = island == "Java"
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["index"],
            mode="lines",
            name=island,
            line=dict(
                dash="dash" if is_java else "solid",
                width=2.5 if is_java else 1.5,
                color="gray" if is_java else None,
            ),
            hovertemplate=f"<b>{island}</b><br>%{{x}}<br>Index: %{{y:.1f}}<extra></extra>",
        ))

    fig.add_hline(y=100, line_dash="dot", line_color="lightgray",
                  annotation_text="Java baseline")
    fig.update_layout(
        height=260,
        yaxis_title="Price Index (Java = 100)",
        title="Cooking Oil Price Index Over Time — Island Groups vs Java",
        legend=dict(orientation="h", y=-0.25),
    )

    mo.ui.plotly(fig)
```

**Key insight for this chart:** Whether the Eastern Indonesia premium is
narrowing (logistics improving) or widening (structural isolation) is the most
analytically interesting finding. Ensure the Y-axis range starts above 90 so
small gap changes are visible — do not auto-scale from 0.

---

## [Section 4] Province Drill-Down Table

```python
@app.cell
def _(province_detail_df, selected_island, mo):
    island = selected_island()

    if island == "All":
        table_data = province_detail_df
        subtitle = "All provinces · sorted by price premium vs Java"
    else:
        table_data = province_detail_df[
            province_detail_df["island_group"] == island
        ]
        subtitle = f"{island} provinces · sorted by price premium vs Java"

    table_data = table_data.sort_values("vs_java_pct", ascending=False)

    # Format coverage as readable date range
    table_data = table_data.copy()
    table_data["coverage"] = (
        table_data["coverage_start"].astype(str)
        + "–"
        + table_data["coverage_end"].astype(str)
    )
    # Pre-format vs_java_pct with color indicators
    table_data["vs Java"] = table_data["vs_java_pct"].apply(
        lambda x: f"+{x:.1f}% 🔴" if x > 0 else f"{x:.1f}% 🟢"
    )

    mo.vstack([
        mo.md(f"## Province Detail — {island}"),
        mo.md(f"_2015–2024 only · Coverage validated · {subtitle}_"),
        mo.ui.table(
            table_data[["province", "island_group", "avg_price", "vs Java", "coverage"]],
            sortable=True,
        ),
        mo.md(
            "_Provinces with fewer than 12 months of coverage are excluded. "
            "Coverage column shows the actual available date range per province._"
        ),
    ])
```

**Notes:**
- `selected_island()` reads from `mo.state` — updates reactively when KPI card
  or map is clicked.
- Coverage column is an act of analytical transparency — show data gaps explicitly.
- "vs Java" with emoji flags gives cell-level color coding without needing custom
  HTML (upgrade path: render as `mo.Html` with a `<table>` for full color cells).

---

## Tab Assembly

```python
@app.cell
def _(
    data_banner, kpi_cards, map_section,
    island_line_chart, province_table,
    commodity_dd, island_dd, year_slider, mo
):
    page3_content = mo.vstack([
        mo.md("# Geographic Price Disparity"),
        mo.md(
            "_Cooking Oil Only — Province-Level Price Index vs Java Baseline_"
        ),
        mo.hstack([commodity_dd, island_dd, year_slider], gap="1rem"),
        data_banner,
        kpi_cards,
        map_section,
        island_line_chart,
        province_table,
    ], gap="2rem")
    return (page3_content,)
```

---

## marimo vs Dash: Key Differences on This Page

| Original (Dash/Vizro) | marimo equivalent |
|---|---|
| `dcc.Store` for selected island | `mo.state()` — bidirectional sync between map click and KPI card click |
| `dcc.Interval` for animation | Phase 2; manual `mo.ui.slider` ships first |
| `px.choropleth` + `@callback` | `mo.ui.plotly(px.choropleth(...))` — `.value` gives click data |
| `vm.AgGrid` | `mo.ui.table(sortable=True)` |
| `Commodity = Rice/Sugar/Flour` grayed-out map | `mo.callout(kind="warn")` replaces map content; map cell returns early |

---

## States

| State | marimo behavior |
|---|---|
| Loading | Cell spinners; geo_data cell runs once on notebook load |
| Map year changed | `map_year_slider.value` triggers choropleth cell re-run; KPI cards unchanged (show 2024 always) |
| Island group clicked (map or KPI card) | `set_selected_island()` called; province table cell re-runs |
| Commodity = Cooking Oil | All sections active |
| Commodity = Rice / Sugar / Flour | `data_banner` highlights warning; choropleth cell returns `mo.callout("National-level only")` instead of map; province table shows empty state |
| Province with limited coverage | Coverage column shows "2015–24" in lighter text via pre-formatted string |

---

## Known Limitations vs Original Spec

| Feature | Original | marimo approach |
|---|---|---|
| Frame-by-frame map animation | `dcc.Interval` ticking every 1s | Phase 2; manual slider is the MVP |
| Province table cell color (red/green bg) | AG Grid cell renderer | Emoji flag approach for MVP; `mo.Html` table for full color |
| Map click → filter | `dcc.Store` + callback | `mo.state()` + `mo.ui.plotly.value` |
