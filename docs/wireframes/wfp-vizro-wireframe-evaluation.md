# WFP Food Price Intelligence Dashboard — Vizro Wireframe Evaluation

**Wireframes reviewed:** Pages 1–4 (Price Trends & Forecast, Seasonal Patterns, Geographic Disparity, Commodity Signals)  
**Target framework:** Vizro (McKinsey) via `vizro-e2e-flow` Claude Code plugin  
**Vizro build path:** `dashboard-design` skill → `dashboard-build` skill with Playwright MCP  
**Evaluation scope:** Component compatibility, implementation complexity, spec quality, cross-cutting concerns

---

## Table of Contents

1. [Overall Assessment](#1-overall-assessment)
2. [Vizro Framework Capabilities — Reference](#2-vizro-framework-capabilities--reference)
3. [Page 1 — Price Trends & Forecast](#3-page-1--price-trends--forecast)
4. [Page 2 — Seasonal Patterns](#4-page-2--seasonal-patterns)
5. [Page 3 — Geographic Disparity](#5-page-3--geographic-disparity)
6. [Page 4 — Commodity Signals](#6-page-4--commodity-signals)
7. [Cross-Cutting Issues](#7-cross-cutting-issues)
8. [Implementation Effort Summary](#8-implementation-effort-summary)
9. [Specification Quality Assessment](#9-specification-quality-assessment)
10. [Recommended Changes Before Build](#10-recommended-changes-before-build)

---

## 1. Overall Assessment

These wireframes are well-specified for a mid-fidelity handoff. Each page declares its audience, the decision it enables, its data sources, its interactive states, and the rationale behind every annotation. That level of specification is exactly what the Vizro `dashboard-design` skill is designed to produce, and it gives the `dashboard-build` phase a clear, unambiguous brief.

The primary concern is not the quality of the spec — it is component mismatch. Several elements the wireframes treat as standard UI patterns (sparklines in KPI cards, conditional chart visibility, an animated choropleth map, a Ramadan-calendar-aligned multi-line chart) fall outside Vizro's declarative configuration model and require custom implementation at the Dash/Plotly layer. This does not make them unbuildable; Vizro's extension model is specifically designed for this. It does mean the build phase will include more custom `@capture("figure")` functions, `dcc.Store` patterns, and Dash callbacks than a pure low-code Vizro project.

**Summary verdict by page:**

| Page | Spec Quality | Vizro Friction | Blocking Issues |
|------|-------------|----------------|-----------------|
| 1 — Price Trends & Forecast | Excellent | Moderate | Sparklines in KPI cards; filter persistence |
| 2 — Seasonal Patterns | Excellent | High | Conditional chart visibility; Ramadan overlay x-axis |
| 3 — Geographic Disparity | Excellent | High | Custom GeoJSON choropleth; animated year slider |
| 4 — Commodity Signals | Excellent | Moderate | Matrix-click interactions; implication card callbacks |

---

## 2. Vizro Framework Capabilities — Reference

Before evaluating each page, the following table summarises what Vizro provides natively (as of v0.1.20+) and what must be built via its extension model. This serves as the lens for all component assessments below.

### 2.1 Native Vizro Components

| Component | Vizro Model | Notes |
|-----------|------------|-------|
| Line, bar, scatter, area charts | `vm.Graph` wrapping `px.*` | Standard Plotly Express charts |
| KPI card (value only) | `vizro.figures.kpi_card` | Requires `vizro >= 0.1.20` |
| KPI card with reference/delta | `vizro.figures.kpi_card_reference` | Shows value + delta vs reference column |
| Interactive data table | `vm.AgGrid` wrapping `dash_ag_grid` | Sortable, searchable, sticky columns |
| Dropdown filter | `vm.Dropdown` | Single or multi-select |
| Range slider | `vm.RangeSlider` | Dual-handle; maps to year range use case |
| Radio items / checklist | `vm.RadioItems`, `vm.Checklist` | Tab-style toggle approximation |
| Static text / markdown | `vm.Card` | Supports full Markdown including headers |
| Multi-page navigation | `vm.Dashboard` with `vm.Page` list | Nav links auto-generated from page titles |
| Page-level grid layout | `vm.Layout` with grid spec string | CSS grid; rows and columns configurable |
| Filter-to-chart action | `vm.Filter` | Standard controls-to-component binding |
| Parameter (non-data control) | `vm.Parameter` | Passes named args to figure functions |

### 2.2 Requires Custom Extension

| Need | Extension Mechanism |
|------|---------------------|
| Chart type not in Plotly Express | `@capture("figure")` custom function returning `go.Figure` |
| KPI card with embedded sparkline | Custom `@capture("figure")` returning `dbc.Card` with nested `dcc.Graph` |
| Conditional chart show/hide | Dash callback toggling `style={"display": "none/block"}` |
| Cross-component click interactions | `vm.Action` or manual Dash `@callback` with `dcc.Store` |
| Filter state persistence across pages | `dcc.Store` at dashboard layout level with callbacks |
| Custom GeoJSON choropleth | `px.choropleth` with `featureidkey` arg, or `go.Choroplethmapbox` |
| Animated slider playback | `dcc.Interval` component + callback stepping through values |
| Skeleton loading states | `dcc.Loading` wrapper (spinner only) or custom HTML skeleton blocks |
| Signal/implication text cards from data | Custom figure returning `dbc.Card` or `dbc.ListGroup` |

---

## 3. Page 1 — Price Trends & Forecast

**Audience:** Category Manager (primary), Procurement Analyst (secondary)  
**Decision enabled:** "Is now a good time to lock in bulk purchase contracts for key commodities?"  
**Data sources:** `price_trends.json`, `forecast.json`

### 3.1 Component Assessment

#### ✅ Natively supported

**Global filters [3]**  
All three global filters map directly to Vizro selectors:
- Commodity dropdown → `vm.Dropdown`
- Island Group dropdown → `vm.Dropdown`
- Year range dual-handle slider → `vm.RangeSlider` with `min=2007, max=2024`

The filter persistence note [3b] ("all filters persist across page navigation") is **not** handled natively — see [Section 7.1](#71-global-filter-persistence).

**KPI cards with YoY delta [4]**  
`vizro.figures.kpi_card_reference` handles value + delta vs reference column. The four commodity cards (Rice, Cooking Oil, Sugar, Flour) can be declared as `vm.Figure` instances using this function. Color coding (red for increase, green for decrease) is handled by the `kpi_card_reference` default styling.

> **Note on [4d]:** "Four cards always shown regardless of filter" — since KPI cards are `vm.Figure` components not linked to the commodity filter, they will naturally remain visible. Confirm that no filter is accidentally wired to them.

**Multi-series trend chart [5]**  
`vm.Graph` wrapping `px.line` with `color="commodity"`. The commodity toggle [5d] maps to a `vm.Dropdown` (or `vm.Checklist`) bound via `vm.Filter` to the chart's `data_frame`.

**YoY inflation table [7]**  
`vm.AgGrid` handles sortable columns [6a], conditional cell styling (red >10%, green decrease [6b/6c]), and year range filtering [6d] via a `vm.Filter` binding.

#### ⚠️ Requires custom implementation

**Forecast + 95% confidence interval overlay [5]**  
Vizro has no native forecast chart type. This requires a custom `@capture("figure")` function that constructs a `go.Figure` with:
- A `go.Scatter` trace for actual historical prices (solid line)
- A `go.Scatter` trace for the forecast (dashed line)
- A filled `go.Scatter` trace for the 95% CI band using `fill="toself"` and low opacity

The vertical dashed separator between actuals and forecast [5b] must be added via `fig.add_vline(x=separator_date, line_dash="dash")` inside this same function.

The structural break annotation [5e] ("2022 Export Ban") must also be added via `fig.add_annotation()` inside the custom figure. This is low-effort but cannot be expressed in Vizro's YAML/Pydantic config.

**Sparklines inside KPI cards [4c]**  
`kpi_card` and `kpi_card_reference` do not support embedded mini-charts. A custom figure is needed that returns a `dbc.Card` containing both the value/delta display and a small `dcc.Graph` with a 24-month sparkline trace. The dotted extension for forecast [4c] requires the sparkline to also accept forecast data.

This is the most underestimated component on this page. Budget accordingly.

**Buy Signal Monitor [6]**  
No native Vizro component maps to a coloured status list (BUY NOW / HOLD / WATCH with per-commodity rows). Options:
1. **`vm.Card` with dynamic Markdown** — simplest, but requires a callback to regenerate the Markdown string when filters change.
2. **Custom `vm.Figure` returning `dbc.ListGroup`** — cleaner, more interactive, supports click events.

The signal logic (BUY NOW = forecast lower bound < current price, etc.) runs as pure Python in the figure function or in a pre-processing step against `forecast.json → signals[]`.

**Model selector dropdown inside chart header [5, last annotation]**  
The wireframe places a `[Model: AutoARIMA ▼]` dropdown inside the chart area. Vizro's layout system does not support controls embedded within a chart container — controls exist in the filter panel. 

**Recommendation:** Move this to the global filter row as a `vm.Dropdown` bound via `vm.Parameter` to the custom figure function's `model` argument. This is functionally equivalent and requires no layout hacking.

### 3.2 Layout Notes

The wireframe's two-column lower section (Buy Signal Monitor ~35% | YoY Table ~65%) maps to Vizro's grid layout:

```python
layout=vm.Layout(grid=[[0, 0, 1, 1, 1],   # filters row
                        [2, 2, 2, 2, 2],   # KPI cards
                        [3, 3, 3, 3, 3],   # trend chart
                        [4, 4, 5, 5, 5]])  # signal monitor | YoY table
```

The limitations footnote [8] should be a `vm.Card` placed as the final row. Set the grid row to a fixed small height to prevent it from collapsing.

### 3.3 Mobile Considerations

The mobile layout (390px) specifies stacked KPI cards and horizontal scroll on the YoY table. Vizro's grid does not have responsive breakpoints by default. A CSS override targeting `@media (max-width: 576px)` will be needed to:
- Stack the four KPI cards vertically
- Enable `overflow-x: auto` on the AgGrid container
- Reduce the trend chart height to 260px

---

## 4. Page 2 — Seasonal Patterns

**Audience:** Procurement Analyst (primary), Category Manager (secondary)  
**Decision enabled:** "When should we increase stock for each commodity based on historical seasonal patterns?"  
**Data source:** `seasonal_patterns.json`

### 4.1 Component Assessment

#### ✅ Natively supported

**Global filters + page-specific driver toggle [3]**  
Global filters (Commodity, Island Group, Year Range) are identical to Page 1. The Seasonal Driver Toggle [3a] can be implemented as a `vm.RadioItems` styled with custom CSS to appear as a tab row, or as a proper `vm.Tabs` component if each driver maps to a full page section. `vm.RadioItems` is preferable here since the toggle changes chart content, not page structure.

**Year-end bar chart [8]**  
Simple `px.bar` with 4 commodity bars in a `vm.Graph`. Horizontal version on mobile via a `vm.Parameter` toggling `orientation`.

**Seasonal summary table [9]**  
`vm.AgGrid` with sortable columns [9b], negative premium styling [9c], and the Lead Time column [9d] as a plain text string column.

#### ⚠️ Requires custom implementation

**Seasonal heatmap — 4×12 commodity/month grid [5]**  
`px.imshow` or `go.Heatmap` on a 4×12 matrix of `(commodity, month, premium_pct)` values can produce this chart. The implementation challenge is the interaction requirement [5]: when the Commodity filter is active, "heatmap dims other rows." 

This requires a custom `@capture("figure")` that:
1. Accepts a `selected_commodity` parameter
2. Applies a custom colorscale that reduces opacity on non-selected rows (no native Plotly parameter for per-row opacity in a heatmap)
3. Returns a `go.Figure` with per-cell annotations for hover

The single-hue scale [5b] (white → dark, no rainbow) maps to `colorscale="Blues"` or a custom sequential scale.

The calendar note [5, ⓘ annotation] must be added via `fig.add_annotation()` or placed in the chart's `vm.Graph` footer/description property.

**Ramadan overlay chart — 17 overlaid lines, Eid-relative x-axis [6]**  
This is the most analytically complex chart in the project. The implementation requires:

1. **Data pre-processing:** The `ramadan_overlay[]` array uses `week_relative` (T-8 to T+6 weeks from Eid al-Fitr) as the x-axis unit. This is not a calendar date — it is a calculated offset. The data must be pre-pivoted so each year is a separate series.

2. **Chart construction:** A `go.Figure` loop over 17 years, each as a thin semi-transparent `go.Scatter` line (`opacity=0.35`, `line_width=1`), plus one bold `go.Scatter` for the 17-year average (`line_width=2.5`).

3. **2022 outlier label [6, annotation]:** Added via `fig.add_annotation()` pointing to the 2022 line's peak. This must be present — the cooking oil export ban creates an extreme outlier that without labelling appears as a data error.

4. **Commodity selector inside chart [6]:** Implemented as a `vm.Parameter` targeting the figure function's `commodity` argument, rather than a dropdown inside the chart header.

**Conditional chart visibility based on driver toggle [States table]**  
The wireframe specifies:
- Driver = Ramadan/Lebaran → Show [6], hide [7][8]
- Driver = Harvest → Show [7], hide [6][8]  
- Driver = Year-End → Show [8], hide [6][7]
- Driver = All Drivers → Show only [5][9]

Vizro has no built-in conditional rendering of `vm.Graph` components within a page. This requires a Dash callback that:
1. Reads the driver toggle value from a `dcc.Store` or from the `vm.RadioItems` component state
2. Sets `style={"display": "none"}` on hidden chart containers
3. Sets `style={"display": "block"}` on the active chart container

This callback must be registered outside Vizro's declarative model, added to the `app.callback` registry after `Vizro().build(dashboard)`.

**Procurement timing action cards [4]**  
Same pattern as the Buy Signal Monitor on Page 1 — a custom `vm.Figure` returning `dbc.Card` instances populated from `seasonal_patterns.json → action_windows[]`. The cards update when the driver toggle changes, requiring the figure function to accept `driver` as a parameter.

The consistency score display ("14 of 17 years" [4b]) and the spike magnitude sorting [4e] are computed in the figure function from the `action_windows[]` data.

**Data availability notice [4f]**  
A `vm.Card` with static Markdown placed immediately above the heatmap in the layout grid. Mark it as non-interactive (no filters wired to it). The "small callout, not a warning style" instruction [4f] should be expressed via a custom CSS class on the card container.

### 4.2 Layout Notes

Page 2 has the most complex conditional layout of any page. The grid must accommodate:
- Always-visible components: filters, driver toggle, action cards, data notice, heatmap, summary table
- Driver-conditional components: Ramadan overlay [6], Harvest chart [7], Year-end chart [8]

The cleanest approach is to render all three driver-specific charts in the grid but hide two of them via callback at any given time. Reserve a fixed grid row for the driver chart slot so the layout does not reflow when charts toggle.

```python
layout=vm.Layout(grid=[[0, 0, 0, 0],   # filters
                        [1, 1, 1, 1],   # driver toggle
                        [2, 2, 2, 2],   # action cards
                        [3, 3, 3, 3],   # data availability notice
                        [4, 4, 4, 4],   # heatmap
                        [5, 5, 5, 5],   # driver-specific chart slot (Ramadan/Harvest/Year-end)
                        [6, 6, 6, 6]])  # summary table
```

---

## 5. Page 3 — Geographic Disparity

**Audience:** Procurement Analyst (primary)  
**Decision enabled:** "Which island group or province offers the best sourcing price right now?"  
**Data source:** `geographic_disparity.json`

### 5.1 Component Assessment

#### ✅ Natively supported

**Island group comparison line chart [6]**  
`px.line` with 5 series (Java + 4 island groups), rendered via `vm.Graph`. Java as a flat horizontal reference line at index 100 can be added via `fig.add_hline(y=100)` inside a custom figure, or expressed as a fifth series with constant values.

**Province drill-down table [7]**  
`vm.AgGrid` with:
- Sortable columns [7a] via default AgGrid behaviour
- Search field [7, subtitle] via `vm.AgGrid`'s built-in search
- "vs Java" conditional cell colouring [7d] via `cellStyle` in `columnDefs`
- Coverage column [7c] as a plain text column
- Table footer note [7e] (excluded provinces) via the `footer` argument on `vm.AgGrid`

**KPI cards [4]**  
Five island group KPI cards using `kpi_card_reference` with Java (index=100) as the reference column. The "clicking a card filters the province table" interaction [4d] requires a callback — see below.

**Data availability banner [3c]**  
A `vm.Card` with Markdown content, placed prominently above the map in the layout. Light yellow background via a custom CSS class. Non-collapsible by nature (it is a static card).

#### ⚠️ Requires custom implementation

**Indonesia choropleth map [5] — highest complexity component in the project**  
This is the most technically demanding component across all four pages. The implementation path depends on whether a Mapbox token is available in the deployment environment.

**Option A — No Mapbox token (recommended for portability):**  
Use `px.choropleth` with `geojson=` pointing to the bundled GeoJSON file and `featureidkey="properties.island_group"`. This renders in Plotly's built-in SVG map renderer — no token required, works offline. The GeoJSON must be a 5-feature file (one per island group) with `properties.island_group` matching the data values exactly.

```python
import json
with open("assets/indonesia_island_groups.geojson") as f:
    geojson = json.load(f)

fig = px.choropleth(
    df,
    geojson=geojson,
    locations="island_group",
    featureidkey="properties.island_group",
    color="index",
    color_continuous_scale="Blues",
    ...
)
fig.update_geos(fitbounds="locations", visible=False)
```

**Option B — With Mapbox token:**  
Use `px.choropleth_mapbox` for tile-layer backgrounds (satellite, street map). Requires a `MAPBOX_ACCESS_TOKEN` environment variable in the deployment environment.

Either way, the map must be wrapped in a custom `@capture("figure")` that accepts a `year` parameter for the year slider interaction.

**Year slider + animate button [5c/5d/5e]**  
This is the second-highest complexity component. The year slider maps to a `vm.Slider` bound via `vm.Parameter` to the map figure's `year` argument — that part is native Vizro.

The **Animate button** [5e] ("plays 2007→2024 at 1 second per year") is entirely outside Vizro's declarative model. It requires:
1. A `dcc.Interval` component (triggers a callback every 1000ms)
2. A `dcc.Store` holding the current animation year and a boolean `is_playing` flag
3. A callback that increments the year in the store on each interval tick
4. A second callback that reads the store and updates the map figure
5. A custom HTML button (or `dbc.Button`) that sets `is_playing=True` and transitions to a Pause label while running

This is the most callback-heavy interaction in the entire project. Test it early.

**Bidirectional click interactions [4d, 5, 7b]**  
The wireframe specifies a three-way interaction: clicking a KPI card highlights the corresponding island group on the map AND filters the province table; clicking the map does the same. This requires:

1. A `dcc.Store` holding `selected_island_group` (string or None)
2. A callback with inputs from both the KPI card click events and the map `clickData`
3. Outputs updating the map's highlight styling, the province table's `filterModel`, and the KPI card focus rings

`vm.Action` can handle simple filter-on-chart-click for Plotly figures, but the multi-component fan-out here (map → table AND cards; cards → map) requires manual callback registration.

### 5.2 Data Scope Note

The wireframe's data scope annotation is correctly specified: all geographic analysis is Cooking Oil only. The commodity filter [3a] defaulting to Cooking Oil and showing a grayed-out state for other commodities [States table] must be enforced via a callback that detects the selected commodity and either hides the geographic components or overlays the "National-level only — see Page 1" message.

### 5.3 GeoJSON Asset

The wireframe specifies the GeoJSON at `/dashboard/public/indonesia_island_groups.geojson`. In a Vizro/Dash project, static assets are served from the `assets/` directory. The correct path is `dashboard/assets/indonesia_island_groups.geojson`. Ensure the file is loaded once at module import, not on every callback invocation, to avoid repeated disk reads on filter changes.

The GeoJSON file must have 5 features (one per island group: Java, Sumatera, Kalimantan, Sulawesi, Eastern Indonesia). Each feature must have `properties.island_group` matching the string values in `geographic_disparity.json → annual_index[].island_group`. The `featureidkey="properties.island_group"` argument on `px.choropleth` binds the data to the map polygons.

### 5.4 Layout Notes

The map [5] at 340px height is the dominant visual element. Reserve it a generous grid row. The year slider belongs inside the map component (rendered via Plotly's built-in `sliders` config) rather than as a separate `vm.Slider`, to keep it visually co-located with the map.

---

## 6. Page 4 — Commodity Signals

**Audience:** Category Manager (primary), Procurement Analyst (secondary)  
**Decision enabled:** "Which commodities should we monitor as early warning indicators for others?"  
**Data source:** `commodity_correlation.json`

### 6.1 Component Assessment

#### ✅ Natively supported

**Correlation matrix heatmap [5]**  
`px.imshow` on a 4×4 DataFrame of correlation values, rendered via `vm.Graph`. Configuration notes:
- Single-hue colorscale [5d]: `colorscale="Blues"` or similar
- Diagonal blanked [5a]: set diagonal cells to `NaN` before passing to `px.imshow`
- Matrix asymmetry [5b]: the upper triangle (A leads B) and lower triangle (B leads A) contain different values — this is structurally correct for a lagged correlation matrix. The label clarification [5c] ("Row commodity leads column commodity at selected lag") must be added as an annotation or as the chart's subtitle property
- Strongest cell highlighted [5f]: `fig.add_shape()` to draw a border rect around the max-value cell

**Scatter chart with pre/post 2022 colour split [6]**  
`px.scatter` with `color="period"` (where `period` is a column with values `"pre-2022"` or `"post-2022"`). Trend line overlay [6c] via `trendline="ols"` on each group separately, or `fig.add_traces()` with a separate OLS trace.

**Rolling correlation stability line chart [7]**  
`px.line` with `y="rolling_r_3yr"`. Additional elements:
- `r = 0.3` floor reference line: `fig.add_hline(y=0.3, line_dash="dot")`
- 2022 vertical marker [7b]: `fig.add_vline(x="2022-01-01", line_dash="dash")`

**Full correlation detail table [9]**  
`vm.AgGrid` with sortable columns and the lag toggle [9f] bound via `vm.Parameter` to the table's data function. The `Pre-2022 r` vs `Post-2022 r` split columns [9b] are the key analytical differentiator — ensure they are formatted to 2 decimal places and coloured (large divergence = amber/red flag).

**Lag selector [3, page-specific]**  
`vm.RadioItems` with options `[0, 1, 2, 3]`, bound via `vm.Parameter` to the correlation matrix figure's `lag` argument. Default [3b]: 1 month.

**Island Group filter disabled state [3c]**  
The Island Group dropdown should be rendered with `disabled=True` and a tooltip ("National-level analysis — Island Group disabled"). In Vizro, `vm.Dropdown` does not have a native `disabled` prop in config, but it can be set via a `clientside_callback` or by overriding the component's `disabled` attribute after build.

#### ⚠️ Requires custom implementation

**Leading indicator callout cards [4]**  
Identical pattern to the Buy Signal Monitor (Page 1) and action cards (Page 2). A custom `@capture("figure")` returns a `dbc.Card` layout populated from `commodity_correlation.json → top_relationships[]`. The card content updates when the lag selector changes, requiring `lag` as a figure function parameter.

The plain-language implication text [4b] ("When rice rises, expect flour to follow within 2 months") is pulled from the `implication_text` field in `top_relationships[]` — not generated dynamically. Confirm with the data spec that this field is pre-written and not computed at render time.

The "Stable post-2022" flag [4c] maps to the `stable` boolean in `top_relationships[]`. Display as a green/amber badge inside the card.

**Procurement implication card [8]**  
The analytical centrepiece of Page 4. A `dbc.Card` populated from the selected matrix pair, showing:
- Plain-language procurement recommendation [8d]
- Conditional `⚠ Relationship weakened post-2022` caveat [8b] — triggered when `abs(pre_2022_r - post_2022_r) > threshold`

This card updates whenever the selected matrix pair changes (via matrix click [5] or the commodity dropdowns in [6]). It requires a `dcc.Store` holding the current pair and callbacks fanning out to [6], [7], and [8] simultaneously.

The disclaimer at the bottom of [8] ("This recommendation is generated from the data. It does not account for supplier contract terms...") should be expressed as static Markdown in the card footer — not conditional.

**Matrix cell click → dual chart update [5, 6, 7]**  
The click interaction on the correlation matrix [5] updates both the scatter chart [6] and the stability chart [7]. This is the most callback-dense interaction on this page:

1. `clickData` from the matrix `vm.Graph` feeds a `dcc.Store` storing `(leader, follower)`
2. Two callbacks read the store: one updates the scatter chart, one updates the stability chart
3. A third callback updates the implication card [8]

`vm.Action` can partially handle this — Vizro's `filter_interaction` action propagates click data to a target component. However, propagating one click to three targets simultaneously currently requires manual `@callback` registration.

### 6.2 Layout Notes

The two-column lower section (scatter [6] ~40% | stability chart [7] ~55%) maps to:

```python
layout=vm.Layout(grid=[[0, 0, 0, 0],       # filters + lag selector
                        [1, 1, 1, 1],       # leading indicator cards
                        [2, 2, 2, 2],       # correlation matrix
                        [3, 3, 4, 4, 4],   # scatter | stability chart
                        [5, 5, 5, 5],       # implication card
                        [6, 6, 6, 6]])      # detail table
```

The implication card [8] should visually stand out. Consider a `vm.Card` with a custom CSS class that adds a left border accent (coloured by signal strength).

---

## 7. Cross-Cutting Issues

### 7.1 Global Filter Persistence

**Spec requirement:** Filters persist across page navigation [3b, Page 1 annotation].  
**Vizro behaviour:** `vm.Filter` state is reset when navigating to a new page. Vizro does not persist filter state natively.

**Implementation:** Add a `dcc.Store` at the dashboard layout level (outside any `vm.Page`) storing `{commodity, island_group, year_start, year_end}`. Register callbacks on each page that:
1. Write filter values to the store on change
2. Read from the store and set initial filter values on page load

This requires accessing the underlying Dash app object:

```python
app = Vizro().build(dashboard)
app.layout.children.append(dcc.Store(id="global-filter-store", storage_type="session"))
```

### 7.2 TanStack Table vs. AG Grid

**Spec language:** Pages 1, 2, and 4 reference "TanStack Table" in annotations.  
**Vizro reality:** Vizro uses AG Grid (`vm.AgGrid` wrapping `dash_ag_grid`), not TanStack Table.

All stated requirements — sortable columns, searchable rows, sticky columns, horizontal scroll, conditional cell styling — are fully supported in AG Grid. There is no functional gap. Update all "TanStack Table" references in the spec to "AG Grid" before the build phase to avoid confusion.

### 7.3 Mobile Responsive Layouts

The wireframes include detailed mobile layouts (390px) for all four pages. Vizro's grid layout system is not responsive by default — it uses a fixed CSS grid that does not change at narrow viewports.

**Required CSS overrides (in `assets/custom.css`):**

```css
@media (max-width: 576px) {
  /* Stack KPI cards vertically */
  .kpi-row { flex-direction: column; }
  
  /* Enable horizontal scroll on tables */
  .ag-root-wrapper { overflow-x: auto; }
  
  /* Reduce chart heights */
  .js-plotly-plot { min-height: 220px !important; }
  
  /* Stack filter controls */
  .filter-panel { flex-direction: column; }
  
  /* Driver toggle as scrollable row */
  .driver-toggle { overflow-x: auto; white-space: nowrap; }
}
```

The mobile-specific behaviours specified in the wireframes (sticky year column on tables, horizontal scroll with sticky first column, pinch-to-zoom on charts) can all be addressed via AG Grid's `pinned: "left"` column option and Plotly's built-in `config={"scrollZoom": True}` prop.

### 7.4 Skeleton Loading States

**Spec requirement:** All pages specify skeleton gray placeholder loading states.  
**Vizro behaviour:** `vm.Graph` and `vm.AgGrid` render empty while data loads but do not show skeleton UI.

**Available options:**
1. **`dcc.Loading` wrapper** (simplest): wraps chart containers with a spinner. Not a skeleton, but signals loading state.
2. **Custom skeleton blocks**: HTML divs with animated gradient background, toggled via callback on `data-loading` state. More effort but matches the spec.
3. **Plotly's built-in loading spinner**: appears on charts automatically during callback execution.

For a portfolio/demo project, option 1 is sufficient. For production, option 2 matches the wireframe intent.

### 7.5 Limitations Footnotes

Pages 1 and 2 specify always-visible limitations footnotes [8 on Page 1]. These map directly to `vm.Card` components placed as the final item in the page layout grid. Two requirements to enforce:

1. **"Always visible without scrolling on desktop"** [8a, Page 1] — the page layout must not allow the footnote to fall below the fold. On a 1280px desktop with a full-page chart stack, this is a real risk. Set the grid to `100vh` height with `overflow-y: auto` so the footnote anchors to the bottom of the viewport rather than the bottom of the content.

2. **"See methodology →" link** [8b] — `vm.Card` supports Markdown links. `[See methodology →](https://github.com/your-repo/docs/model_methodology.md)` renders as a clickable link that opens in a new tab.

### 7.6 Data Availability Banners

Pages 2, 3, and 4 all display data availability notices (Cooking Oil is the only commodity with province-level data). The implementation is consistent:
- A `vm.Card` with static Markdown content
- Placed prominently in the layout (above the first chart that is affected)
- Non-collapsible (a static card is non-collapsible by default)

Page 3 [3c] specifies a light yellow background for the banner. This requires a custom CSS class:

```css
.data-availability-banner .card {
  background-color: #FFFBEA;
  border-left: 3px solid #F59E0B;
}
```

Apply via `className` prop on the card's underlying `dbc.Card` component.

### 7.7 CSS Class Reference

The following custom CSS classes are referenced across all four pages. Define them in `dashboard/assets/custom.css`.

| Class | Used By | Purpose | Style |
|-------|---------|---------|-------|
| `.data-availability-banner .card` | Pages 2, 3, 4 | Data scope notice | Light yellow background, left amber border |
| `.limitations-footnote .card` | Pages 1, 2 | Model limitations footer | Smaller font, muted background, always visible |
| `.signal-card .card` | Page 1 | Buy Signal Monitor status cards | Colored left border by signal (BUY=green, HOLD=gray, WATCH=amber) |
| `.implication-card .card` | Page 4 | Procurement recommendation | Left accent border, warning variant for weakened relationships |
| `.action-card .card` | Page 2 | Procurement timing cards | Commodity-colored top border |
| `.kpi-row` | Page 1, 3 | Flex container for KPI cards | `display: flex; gap: 1rem` |
| `.driver-toggle` | Page 2 | Seasonal driver tab row | `overflow-x: auto; white-space: nowrap` for mobile scroll |
| `.empty-state` | Pages 3, 4 | No-data placeholder message | Centered text, muted color, min-height 120px |

### 7.8 Interaction Pattern Mapping

Each page's interactive elements mapped to Vizro implementation patterns. Patterns reference the `wiring-vizro-actions` skill terminology.

| Page | Element | Vizro Pattern | Source | Control | Target | Notes |
|------|---------|---------------|--------|---------|--------|-------|
| 1 | Global filters → trend chart | Standard filter | `vm.Filter` | Commodity, Island Group, Year Range | Trend chart `vm.Graph` | Native Vizro binding |
| 1 | Model selector → trend chart | Parameter | `vm.Dropdown` | Model name | Custom figure `model` arg | `vm.Parameter` with `vm.Dropdown` |
| 2 | Driver toggle → chart visibility | Conditional show/hide | — | `vm.RadioItems` | 3 chart containers | Manual Dash callback on `style.display` |
| 2 | Driver toggle → action cards | Parameter | `vm.RadioItems` | Driver name | Custom figure `driver` arg | `vm.Parameter` |
| 3 | Map click → province table + KPI highlight | Multi-Dimensional Slice (adapted) | Map `clickData` | `dcc.Store` | Province table `filterModel` + KPI focus ring | Manual callback; `vm.Figure` cannot be click source |
| 3 | KPI card click → map + table | Multi-Dimensional Slice (adapted) | KPI card click | `dcc.Store` | Map highlight + table filter | Manual callback; `vm.Figure` cannot be `set_control` source |
| 3 | Animate button → map + slider | Animation loop | `dbc.Button` | `dcc.Interval` + `dcc.Store` | Map figure `year` arg + slider value | Manual callback; not a Vizro pattern |
| 4 | Matrix click → scatter + stability + implication | Multi-Dimensional Slice | Matrix `vm.Graph` `clickData` | `dcc.Store` | Scatter, stability, implication | `vm.Action` for 2 targets; manual callback for 3rd |
| 4 | Lag selector → matrix + cards | Parameter | `vm.RadioItems` | Lag value | Matrix figure, callout figures | `vm.Parameter` on each target |

**Critical constraint:** `vm.Figure` (KPI cards) cannot be a `set_control` source — only `vm.Graph` and `vm.AgGrid` carry click-data. Page 3's bidirectional KPI↔map interaction requires manual Dash callbacks, not declarative `va.set_control`.

---

## 8. Implementation Effort Summary

The following table rates every non-trivial component by implementation effort in the context of a Vizro build. Effort levels assume familiarity with Dash/Plotly callbacks.

| Component | Page | Vizro Path | Effort |
|-----------|------|-----------|--------|
| KPI cards with YoY delta | 1 | `kpi_card_reference` — native | 🟢 Low |
| Global filter controls | All | `vm.Dropdown`, `vm.RangeSlider` — native | 🟢 Low |
| Multi-series trend line chart | 1, 3 | `px.line` in `vm.Graph` — native | 🟢 Low |
| Scatter with pre/post 2022 colour | 4 | `px.scatter(color="period")` — native | 🟢 Low |
| Rolling correlation stability chart | 4 | `px.line` + `add_hline/vline` — minor custom | 🟢 Low |
| AgGrid sortable tables | 1, 2, 4 | `vm.AgGrid` — native | 🟢 Low |
| Year-end bar chart | 2 | `px.bar` — native | 🟢 Low |
| Correlation matrix heatmap | 4 | `px.imshow` + diagonal masking | 🟡 Medium |
| Seasonal heatmap (4×12) | 2 | `go.Heatmap` + per-row opacity callback | 🟡 Medium |
| Forecast + CI band overlay | 1 | Custom `go.Figure` with 3 traces | 🟡 Medium |
| Sparklines in KPI cards | 1 | Custom `dbc.Card` + `dcc.Graph` | 🟡 Medium |
| Buy signal / implication cards | 1, 4 | Custom `vm.Figure` → `dbc.ListGroup` | 🟡 Medium |
| Procurement action cards | 2 | Custom `vm.Figure` → `dbc.Card` list | 🟡 Medium |
| Conditional chart visibility | 2 | Dash callback on `style.display` | 🟡 Medium |
| Matrix-click → dual chart update | 4 | `dcc.Store` + multi-output callback | 🟡 Medium |
| Global filter persistence | All | `dcc.Store` at dashboard level | 🟡 Medium |
| Ramadan overlay (17 lines, Eid-relative x) | 2 | Custom `go.Figure` loop + axis config | 🟠 Medium-high |
| KPI card → map bidirectional click | 3 | Multi-source callback + `dcc.Store` | 🟠 Medium-high |
| Indonesia choropleth (custom GeoJSON) | 3 | `px.choropleth` + `featureidkey` | 🔴 High |
| Year animate button + `dcc.Interval` | 3 | `dcc.Interval` + step callback | 🔴 High |

**Total custom `@capture("figure")` functions required:** ~8  
**Total Dash callbacks outside Vizro's declarative model:** ~10–12  
**Estimated ratio of declarative vs. custom code:** ~50/50

---

## 9. Specification Quality Assessment

The wireframes are evaluated against the criteria the `vizro-e2e-flow` `dashboard-design` skill enforces.

### 9.1 What the spec does well

| Criterion | Assessment |
|-----------|-----------|
| Analytical question per page | ✅ Clearly stated at the top of every page ("Decision Enabled") |
| Audience identification | ✅ Primary and secondary audience named on every page |
| Data source mapping | ✅ Every component traces back to a named JSON file and field path |
| Interactive states documented | ✅ Full states table on every page (loading, filter active, hover, click) |
| Annotation rationale | ✅ Every annotation explains *why* the element must be present, not just *what* it is |
| Mobile layout | ✅ All four pages include 390px breakpoint layouts |
| Data quality honesty | ✅ Coverage columns, data scope banners, and 2022 outlier labels are first-class requirements |
| Uncertainty communication | ✅ Limitations footnotes, CI bands, and "Stable post-2022" flags are non-negotiable requirements |

### 9.2 What the spec could improve

All items from §9.2 have been resolved in the wireframe updates:

| Gap | Resolution |
|-----|------------|
| TanStack Table references | ✅ Replaced with "AG Grid" across Pages 2, 3, 4 |
| Filter persistence mechanism | ✅ Page 1 annotation [3b] now specifies `dcc.Store` with `storage_type="session"` |
| Animate button UX details | ✅ Page 3 states table now specifies IDLE → PLAYING → COMPLETE |
| Ramadan x-axis data contract | ⚠ Partial — wireframe annotation [6d] specifies integer `week_relative` with formatted tick labels, but source data is monthly (not weekly). Build-phase resolution: use `month_relative` T-2 to T+1 (4 monthly buckets) instead of `week_relative` T-8 to T+6. Wireframe deviation — surface in PR description per Phase C handoff rule. See LEARNINGS §100, HANDOFF-page2 §2. |
| Empty states | ✅ Pages 3 and 4 states tables now include empty state rows |
| Choropleth GeoJSON property names | ✅ Page 3 content spec specifies `featureidkey="properties.island_group"` |

---

## 10. Recommended Changes Before Build

The following changes should be made to the wireframe spec before passing it to the `dashboard-build` phase.

### 10.1 Required (will block build if not addressed)

All items from §10.1 have been resolved — see §10.4.

### 10.2 Recommended (will cause confusion if not addressed)

All items from §10.2 have been resolved — see §10.4.

### 10.3 Open Items (still require resolution)

| # | Item | Status | Action |
|---|------|--------|--------|
| 1 | Mapbox token requirement | Open | Confirm `px.choropleth` (no token) is the target; add deployment note |
| 2 | `post_2022_r` divergence threshold | Open | Wireframes now specify `abs(pre_2022_r - post_2022_r) > 0.2` — confirm in evaluation §6.1 |
| 3 | GeoJSON creation | Open | Create `dashboard/assets/indonesia_island_groups.geojson` (5 features, province→island-group merge) |

### 10.4 Resolved Items

| # | Item | Resolution |
|---|------|------------|
| 1 | Confirm GeoJSON property names | Added `featureidkey="properties.island_group"` to Page 3 content spec and evaluation §5.1/§5.3 |
| 2 | Clarify `week_relative` type | Page 2 annotation [6d] now specifies integer with formatted tick labels — **but the actual build will use `month_relative` T-2 to T+1 (4 monthly buckets), not `week_relative` T-8 to T+6 (15 weekly buckets), because source data is monthly. Wireframe deviation surfaced in PR.** |
| 3 | Animate button state machine | Page 3 states table now specifies IDLE → PLAYING → COMPLETE |
| 4 | Replace "TanStack Table" → "AG Grid" | Pages 2, 3, 4 annotations updated; evaluation §7.2 already noted this |
| 5 | Move model selector to filter row | Page 1 annotation [5] now shows "relocated to global filter row [3]" |
| 6 | Add empty states | Pages 3 and 4 states tables now include empty state rows |
| 7 | Document filter persistence mechanism | Page 1 annotation [3b] now specifies `dcc.Store` with `storage_type="session"` |
| 8 | CSS class names | Added §7.7 CSS class reference table with 8 classes |
| 9 | Interaction pattern mapping | Added §7.8 mapping table with 9 interaction patterns |
| 10 | GeoJSON path corrected | Page 3 content spec updated from `/dashboard/public/` to `dashboard/assets/` |
| 11 | Page 3 friction reclassified | Verdict table updated from "Highest" to "High" |

---

*Evaluation prepared against Vizro v0.1.20+, vizro-e2e-flow plugin (mckinsey/vizro), and Plotly/Dash standard library. All component assessments verified against the Vizro ReadTheDocs documentation and the e2e-flow README.*
