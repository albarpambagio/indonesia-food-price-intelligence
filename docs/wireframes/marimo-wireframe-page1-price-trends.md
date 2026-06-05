# Marimo Wireframe — Page 1: Price Trends & Forecast
**Framework:** marimo (single multi-tab notebook)
**Tab label:** `"Price Trends"`
**Charting:** Plotly via `mo.ui.plotly()`
**Decision enabled:** "Is now a good time to lock in bulk purchase contracts for key commodities?"

---

## Cell Architecture

This page lives inside the shared `mo.ui.tabs` dict as one tab. All global filter
widgets (commodity, island group, year range) are defined in cells **above** the
tabs cell and are imported by this tab's cells via marimo's reactive DAG.

```
[cell: imports]
       ↓
[cell: data_loading]          ← loads price_trends.json, forecast.json
       ↓
[cell: global_filters]        ← SHARED across all tabs (defined once, above tabs)
  commodity_dd / island_dd / year_slider
       ↓
[cell: page1_derived_data]    ← filters dataframes using global_filters.value
       ↓
[cell: kpi_cards]             ← reads page1_derived_data
[cell: trend_chart]           ← reads page1_derived_data + commodity_dd.value
[cell: buy_signal_monitor]    ← reads page1_derived_data
[cell: yoy_table]             ← reads page1_derived_data
[cell: footnote]              ← static
       ↓
[cell: page1_tab_content]     ← assembles above into mo.vstack / mo.hstack layout
                                 returned as the tab's value in mo.ui.tabs dict
```

---

## Global Filters (defined above the tabs cell — shared with all pages)

```python
@app.cell
def _(mo):
    commodity_dd = mo.ui.dropdown(
        options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
        value="All",
        label="Commodity",
    )
    island_dd = mo.ui.dropdown(
        options=["All", "Java", "Sumatera", "Kalimantan", "Sulawesi", "Eastern Indonesia"],
        value="All",
        label="Island Group",
    )
    year_slider = mo.ui.range_slider(
        start=2007, stop=2024, value=[2007, 2024],
        step=1, label="Year Range",
    )
    return commodity_dd, island_dd, year_slider
```

**Notes:**
- `island_dd` filters Cooking Oil province data only. For Rice, Sugar, Flour it has no
  effect — a `mo.callout` note explains this inline near the filter row.
- `year_slider` uses `mo.ui.range_slider` (dual handle).
- All three widgets are passed by name into every tab's cells via marimo's DAG
  (function arguments). No `dcc.Store` needed.

---

## Data Loading

```python
@app.cell
def _():
    import json, pathlib
    import pandas as pd

    price_df = pd.read_json("data/price_trends.json")        # monthly[]
    forecast_df = pd.read_json("data/forecast.json")          # forecasts[]
    signals_df = pd.DataFrame(
        json.loads(pathlib.Path("data/forecast.json").read_text())["signals"]
    )
    annual_df = pd.read_json("data/price_trends.json")        # annual_change[]
    return price_df, forecast_df, signals_df, annual_df
```

---

## Page-Level Derived Data

```python
@app.cell
def _(price_df, forecast_df, commodity_dd, year_slider):
    # Apply year range filter
    yr_lo, yr_hi = year_slider.value
    filtered = price_df[
        (price_df["year"] >= yr_lo) & (price_df["year"] <= yr_hi)
    ]
    # Apply commodity filter
    if commodity_dd.value != "All":
        filtered = filtered[filtered["commodity"] == commodity_dd.value]

    # Latest price per commodity (for KPI cards)
    latest = (
        price_df.sort_values("date")
        .groupby("commodity")
        .last()
        .reset_index()
    )
    # YoY delta (May 2024 vs May 2023)
    # computed from price_df, not filtered — cards always show all 4
    ...
    return filtered, latest
```

**Note:** KPI cards always show all 4 commodities regardless of commodity filter
(faithful to the original spec — cross-commodity snapshot is the purpose of the cards).
`filtered` is used for the trend chart and YoY table only.

---

## [Section 1] KPI Cards Row

**marimo primitive:** `mo.hstack([card1, card2, card3, card4])`
Each card is `mo.stat()` or a custom `mo.Html` block.

```
┌──────────────────────────────────────────────────────────────┐
│  RICE          COOKING OIL      SUGAR           FLOUR        │
│                                                              │
│  Rp X,XXX/KG   Rp XX,XXX/L     Rp X,XXX/KG    Rp X,XXX/KG  │
│  ↑ +X.X% YoY   ↑ +X.X% YoY    ↑ +X.X% YoY    ↓ -X.X% YoY  │
│  [sparkline]   [sparkline]     [sparkline]     [sparkline]   │
└──────────────────────────────────────────────────────────────┘
```

**Implementation notes:**
- Use `mo.stat(value="Rp 14,500", label="Rice", caption="↑ +3.2% YoY")` for the
  headline figure. `mo.stat` renders cleanly with minimal boilerplate.
- Sparklines: a tiny `go.Figure` with a single `go.Scatter` trace, axes hidden,
  margins zeroed, height ~60px, wrapped in `mo.ui.plotly()`. The dotted extension
  for forecast is a second `go.Scatter` trace with `line=dict(dash="dot")`.
- "↑" colored red (rising) / "↓" colored green (falling) via f-string in caption.
- Loading state: `mo.skeleton()` — not natively in marimo; use `mo.md("Loading…")`
  as a placeholder while data cell runs.

---

## [Section 2] Main Trend + Forecast Chart

**marimo primitive:** `mo.ui.plotly(fig)` — reactive, captures click/hover data.

```
┌─────────────────────────────────────────────────────────────┐
│  17-Year Price History + 6-Month Forecast                   │
│                                                             │
│  Commodity toggle:                                          │
│  mo.ui.radio(["Rice","Cooking Oil","Sugar","Flour","All"])  │
│  (separate from global commodity_dd — local to this chart)  │
│                                                             │
│  IDR ▲                          ┆ FORECAST                  │
│      │                ╭─────────┆╌╌╌╌╌╌ ░░░░               │
│      │       ╭────────╯         ┆      ╌╌╌╌╌               │
│      └────────────────────────────────────────────▶         │
│       2007   2012   2017   2022  2024  Nov2024              │
│                                                             │
│  ░░░ 95% CI   ─── Actual   ╌╌╌ Forecast                    │
└─────────────────────────────────────────────────────────────┘
```

**Cell structure:**

```python
@app.cell
def _(mo):
    chart_commodity_radio = mo.ui.radio(
        options=["Rice", "Cooking Oil", "Sugar", "Flour", "All"],
        value="All",
        label="Show commodity",
    )
    chart_commodity_radio
    return (chart_commodity_radio,)

@app.cell
def _(filtered, forecast_df, chart_commodity_radio, mo):
    import plotly.graph_objects as go

    fig = go.Figure()

    commodities = (
        ["Rice", "Cooking Oil", "Sugar", "Flour"]
        if chart_commodity_radio.value == "All"
        else [chart_commodity_radio.value]
    )

    for c in commodities:
        sub = filtered[filtered["commodity"] == c]
        fc = forecast_df[forecast_df["commodity"] == c]

        # Actual line
        fig.add_trace(go.Scatter(
            x=sub["date"], y=sub["price_idr"],
            mode="lines", name=c,
            hovertemplate="%{x|%b %Y}<br>Price: Rp %{y:,.0f}<extra>" + c + "</extra>",
        ))
        # Forecast dashed line
        fig.add_trace(go.Scatter(
            x=fc["date"], y=fc["forecast"],
            mode="lines", name=f"{c} (forecast)",
            line=dict(dash="dash"),
            hovertemplate="%{x|%b %Y}<br>Forecast: Rp %{y:,.0f}<extra></extra>",
        ))
        # 95% CI shaded area
        fig.add_trace(go.Scatter(
            x=pd.concat([fc["date"], fc["date"][::-1]]),
            y=pd.concat([fc["upper_95"], fc["lower_95"][::-1]]),
            fill="toself", fillcolor="rgba(100,100,200,0.15)",
            line=dict(color="rgba(0,0,0,0)"),
            name="95% CI", showlegend=(c == commodities[0]),
        ))

    # Vertical separator: actuals vs forecast
    fig.add_vline(
        x="2024-05-01", line_dash="dash", line_color="gray", line_width=1.5,
        annotation_text="Forecast →", annotation_position="top right",
    )
    # Structural break annotation
    fig.add_annotation(
        x="2022-04-01", y=fig.data[0].y.max() * 0.9 if fig.data else 0,
        text="2022 Export Ban", showarrow=True, arrowhead=2,
        font=dict(size=11),
    )
    fig.update_layout(
        height=360,
        yaxis_title="IDR per KG / L",
        yaxis_tickformat=",d",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=60, r=20, t=40, b=80),
    )

    chart = mo.ui.plotly(fig)
    chart
    return (chart,)
```

**Notes:**
- `mo.ui.plotly(fig)` captures hover/click — `chart.value` exposes selected point
  data, which downstream cells can read (e.g. to cross-highlight the YoY table).
- The local `chart_commodity_radio` is intentional: the global `commodity_dd` controls
  the data scope; this toggle controls which series are drawn. They can be wired
  together or kept independent — default: independent so the user can see all 4 on
  the chart while filtering the table to one commodity.

---

## [Section 3] Buy Signal Monitor + YoY Table (side by side)

**marimo primitive:** `mo.hstack([buy_signal_block, yoy_table_block])`

### Buy Signal Monitor (~35% width)

```python
@app.cell
def _(signals_df, mo):
    signal_color = {"BUY NOW": "green", "HOLD": "gray", "WATCH": "orange"}

    rows = []
    for _, row in signals_df.iterrows():
        color = signal_color.get(row["signal"], "gray")
        rows.append(mo.md(
            f"**{row['commodity']}** &nbsp; "
            f"<span style='color:{color}'>● {row['signal']}</span>  \n"
            f"_{row['reason']}_"
        ))

    mo.vstack([
        mo.md("## Buy Signal Monitor"),
        *rows,
    ])
```

### YoY Inflation Table (~65% width)

```python
@app.cell
def _(annual_df, year_slider, mo):
    yr_lo, yr_hi = year_slider.value
    table_data = annual_df[
        (annual_df["year"] >= yr_lo) & (annual_df["year"] <= yr_hi)
    ].sort_values("year", ascending=False)

    # Color cells: red >10% increase, green for decrease
    # mo.ui.table supports basic display; for cell coloring use mo.Html
    mo.vstack([
        mo.md("## Annual Price Change"),
        mo.ui.table(
            table_data[["year", "rice_pct", "oil_pct", "sugar_pct", "flour_pct"]],
            sortable=True,
            filterable=False,
        ),
    ])
```

**Notes on cell coloring:** `mo.ui.table` does not support per-cell background colors
natively. Options:
1. Pre-format values as strings with emoji indicators: `"+12.3% 🔴"` / `"-2.1% 🟢"`.
2. Render as `mo.Html` with an inline `<table>` using inline `style` attributes.
   Option 2 is recommended for the production version; Option 1 is faster to ship.

---

## [Section 4] Model Limitations Footnote

```python
@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "**Forecast limitations:** This model describes historical price patterns. "
            "It cannot anticipate government price controls, import tariff changes, or "
            "weather events. Confidence intervals widen significantly beyond 3 months. "
            "[See methodology →](https://github.com/your-repo/docs/model_methodology.md)"
        ),
        kind="info",
    )
```

**Note:** `mo.callout(kind="info")` renders a permanent blue info box — not
collapsible, always visible, matches the original spec requirement.

---

## Tab Assembly

```python
@app.cell
def _(
    kpi_cards, trend_section, buy_signal_block,
    yoy_table_block, footnote, commodity_dd, island_dd, year_slider, mo
):
    page1_content = mo.vstack([
        mo.md("# Price Trends & Forecast"),
        mo.md("_Indonesian Staple Commodities · Jan 2007 – May 2024 + 6-Month Forecast_"),
        mo.hstack([commodity_dd, island_dd, year_slider], gap="1rem"),
        kpi_cards,
        trend_section,
        mo.hstack([buy_signal_block, yoy_table_block], widths=[0.35, 0.65]),
        footnote,
    ], gap="2rem")
    return (page1_content,)
```

---

## marimo vs Dash: Key Differences on This Page

| Original (Dash/Vizro) | marimo equivalent |
|---|---|
| `dcc.Store(storage_type="session")` for filter persistence | Variables defined above `mo.ui.tabs` — automatically shared |
| `@callback` with `Input`/`Output` | Cell function arguments — automatic DAG |
| `vm.AgGrid` for sortable YoY table | `mo.ui.table(sortable=True)` |
| `go.Figure` returned from `@capture("figure")` | `mo.ui.plotly(go.Figure(...))` |
| `dcc.Interval` for map animation | `mo.ui.slider` + run button pattern |
| Vizro theme tokens for dark/light | marimo's built-in dark mode toggle; use `prefers-color-scheme` in CSS |
| Explicit `font.color` in annotations | Remove — rely on plotly template; use `"plotly_white"` or `"plotly_dark"` |

---

## States

| State | marimo behavior |
|---|---|
| Loading | Cell shows spinner while dependency cells are running — automatic |
| Commodity = single | `filtered` df has one commodity; chart radio mirrors; YoY table columns unchanged (all 4 always shown) |
| Year range narrowed | `year_slider.value` triggers re-run of `page1_derived_data` and all downstream cells |
| Hover on forecast | Plotly tooltip natively; `chart.value` updates with hovered point |
| Structural break hover | Plotly `add_annotation` with `hovertext` on the vline |
