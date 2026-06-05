# Marimo Wireframe — Page 2: Seasonal Patterns
**Framework:** marimo (single multi-tab notebook)
**Tab label:** `"Seasonal"`
**Charting:** Plotly via `mo.ui.plotly()`
**Decision enabled:** "When should we increase stock for each commodity based on historical seasonal patterns?"

---

## Cell Architecture

```
[cell: global_filters]        ← SHARED (commodity_dd, island_dd, year_slider)
       ↓
[cell: seasonal_data]         ← loads seasonal_patterns.json
       ↓
[cell: driver_toggle]         ← PAGE-SPECIFIC filter (Ramadan / Harvest / Year-End / All)
       ↓
[cell: action_cards]          ← reads driver_toggle.value + seasonal_data
[cell: data_notice]           ← static callout
[cell: gregorian_heatmap]     ← reads seasonal_data (always Gregorian — not driver-filtered)
[cell: ramadan_chart]         ← reads seasonal_data + driver_toggle.value
[cell: harvest_chart]         ← reads seasonal_data + driver_toggle.value
[cell: yearend_chart]         ← reads seasonal_data + driver_toggle.value
[cell: summary_table]         ← reads seasonal_data
       ↓
[cell: page2_tab_content]     ← assembles layout
```

---

## Data Loading

```python
@app.cell
def _():
    import json, pathlib
    import pandas as pd

    raw = json.loads(pathlib.Path("data/seasonal_patterns.json").read_text())

    action_windows_df = pd.DataFrame(raw["action_windows"])
    gregorian_heatmap_df = pd.DataFrame(raw["gregorian_heatmap"])   # 48 rows (4×12)
    ramadan_overlay_df = pd.DataFrame(raw["ramadan_overlay"])
    harvest_index_df = pd.DataFrame(raw["harvest_index"])
    yearend_premium_df = pd.DataFrame(raw["yearend_premium"])
    summary_df = pd.DataFrame(raw["summary"])

    return (
        action_windows_df, gregorian_heatmap_df, ramadan_overlay_df,
        harvest_index_df, yearend_premium_df, summary_df,
    )
```

---

## Page-Specific Filter: Driver Toggle

```python
@app.cell
def _(mo):
    driver_toggle = mo.ui.radio(
        options=["Ramadan / Lebaran", "Harvest Season", "Year-End", "All Drivers"],
        value="Ramadan / Lebaran",
        label="Seasonal Driver",
    )
    driver_toggle
    return (driver_toggle,)
```

**Note:** `mo.ui.radio` renders as a horizontal button group — visually equivalent
to the tab-style selector in the original spec. No extra styling needed for
standard use; wrap in `mo.hstack` with other global filters.

---

## [Section 1] Action Window Callout Cards

```python
@app.cell
def _(action_windows_df, driver_toggle, mo):
    driver_key = driver_toggle.value  # e.g. "Ramadan / Lebaran"

    relevant = action_windows_df[
        (action_windows_df["driver"] == driver_key) &
        (action_windows_df["spike_pct"].abs() > 3)   # threshold: meaningful effect
    ].sort_values("spike_pct", ascending=False)

    cards = []
    for _, row in relevant.iterrows():
        cards.append(
            mo.stat(
                value=f"+{row['spike_pct']:.1f}%",
                label=f"🛒 {row['commodity']}",
                caption=(
                    f"Stock up {row['lead_weeks']} weeks before · "
                    f"{row['consistency']}/17 years consistent"
                ),
            )
        )

    mo.vstack([
        mo.md(f"## Action Window — {driver_key}"),
        mo.hstack(cards, gap="1rem") if cards else mo.callout(
            mo.md("No statistically meaningful seasonal effect for this driver."),
            kind="warn",
        ),
    ])
```

**Notes:**
- `mo.stat()` is the cleanest primitive for this card pattern.
- Cards sorted by `spike_pct` descending — most urgent procurement action first.
- Rice card appears only when "Harvest Season" driver is selected (harvest discount,
  not a spike — spike_pct will be negative, so abs() > 3 still catches it).
- `data_scope` field from the JSON (`"national"` | `"island"`) can be shown as a
  small badge on each card to reinforce the data availability note.

---

## [Section 2] Data Availability Notice

```python
@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "**Data scope:** Seasonal analysis uses national-level data for Rice, Sugar, "
            "and Flour. Island-level breakdown is available for Cooking Oil only. "
            "The Island Group filter has no effect on Rice, Sugar, or Flour seasonal data."
        ),
        kind="info",
    )
```

Always visible above the heatmap — `mo.callout(kind="info")` is non-collapsible.

---

## [Section 3] Gregorian Calendar Heatmap

Always shown regardless of driver toggle. Uses Plotly heatmap.

```python
@app.cell
def _(gregorian_heatmap_df, mo):
    import plotly.graph_objects as go
    import pandas as pd

    # Pivot: rows = commodity, columns = month (1–12)
    pivot = gregorian_heatmap_df.pivot(
        index="commodity", columns="month", values="premium_pct"
    )
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=month_labels,
        y=pivot.index.tolist(),
        colorscale="Blues",          # single-hue, white → dark
        zmid=0,
        text=[[f"{v:+.1f}%" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        hovertemplate="<b>%{y}</b><br>%{x}<br>Premium: %{z:+.1f}%<extra></extra>",
        colorbar=dict(title="% vs annual avg"),
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=80, r=20, t=40, b=40),
        title="Monthly Price Premium vs Annual Average (%)",
    )

    mo.vstack([
        mo.ui.plotly(fig),
        mo.callout(
            mo.md(
                "**Calendar note:** Ramadan months shift each year. This heatmap shows "
                "Gregorian calendar months — use the Ramadan overlay below for an "
                "Islamic calendar-adjusted view."
            ),
            kind="info",
        ),
    ])
```

**Notes:**
- `colorscale="Blues"` gives the single-hue white→dark scale specified in the original.
- `zmid=0` centers the color scale at zero — cells below annual average appear lighter.
- `texttemplate` shows the exact ±% value in each cell (small font at 200px height,
  but readable on desktop). On mobile the heatmap scrolls horizontally.
- Driver toggle does **not** affect this chart — the callout explains why.

---

## [Section 4] Driver-Specific Charts

Three charts, each conditional on `driver_toggle.value`. In marimo, conditionals
in cell output are handled by returning the appropriate element from a single cell:

```python
@app.cell
def _(
    driver_toggle, ramadan_overlay_df, harvest_index_df,
    yearend_premium_df, commodity_dd, mo
):
    import plotly.graph_objects as go
    import pandas as pd

    driver = driver_toggle.value

    if driver == "Ramadan / Lebaran":
        chart = _build_ramadan_chart(ramadan_overlay_df, commodity_dd.value, mo)

    elif driver == "Harvest Season":
        chart = _build_harvest_chart(harvest_index_df, mo)

    elif driver == "Year-End":
        chart = _build_yearend_chart(yearend_premium_df, mo)

    else:  # "All Drivers"
        chart = mo.md(
            "_Select a specific driver above to see a detailed chart. "
            "The heatmap and summary table below show all drivers combined._"
        )

    chart
    return (chart,)
```

**IMPORTANT marimo rule:** The final expression of the cell renders. The `if/elif`
pattern assigns to `chart` and the final bare `chart` line renders it. This is
correct — do not put `mo.md(...)` directly inside the `if` branches as the last
statement; always assign first, return last.

### Ramadan Overlay Chart helper

```python
def _build_ramadan_chart(df, selected_commodity, mo):
    import plotly.graph_objects as go

    commodities = (
        ["Rice", "Cooking Oil", "Sugar", "Flour"]
        if selected_commodity == "All"
        else [selected_commodity]
    )
    fig = go.Figure()

    for commodity in commodities:
        sub = df[df["commodity"] == commodity] if "commodity" in df.columns else df

        # One thin line per year
        for year in sub["year"].unique():
            yr_data = sub[sub["year"] == year].sort_values("week_relative")
            is_2022 = (year == 2022)
            fig.add_trace(go.Scatter(
                x=yr_data["week_relative"],
                y=yr_data["price_index"],
                mode="lines",
                name=str(year),
                line=dict(
                    width=2.5 if is_2022 else 0.8,
                    color="red" if is_2022 else "rgba(100,100,180,0.4)",
                ),
                showlegend=is_2022,
                hovertemplate=f"{year}<br>Week: %{{x}}<br>Index: %{{y:.1f}}<extra></extra>",
            ))

        # 17-year average — bold line
        avg = sub.groupby("week_relative")["price_index"].mean().reset_index()
        fig.add_trace(go.Scatter(
            x=avg["week_relative"], y=avg["price_index"],
            mode="lines", name="17-yr average",
            line=dict(width=2.5, color="darkblue"),
        ))

    fig.add_hline(y=100, line_dash="dot", line_color="gray",
                  annotation_text="Annual average")
    fig.add_annotation(
        x=sub[sub["year"] == 2022]["week_relative"].mean(),
        y=df[df["year"] == 2022]["price_index"].max(),
        text="2022 outlier (export ban)",
        showarrow=True, arrowhead=2, font=dict(color="red"),
    )
    fig.update_layout(
        height=300,
        xaxis_title="Weeks relative to Eid al-Fitr",
        yaxis_title="Price Index (100 = annual avg)",
        title="Price Index Relative to Eid al-Fitr — All Years Overlaid",
    )
    return mo.ui.plotly(fig)
```

### Harvest Chart helper

```python
def _build_harvest_chart(df, mo):
    import plotly.graph_objects as go

    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]
    harvest_months = [2, 3, 7, 8]   # Mar, Apr, Aug, Sep (0-indexed)

    colors = [
        "rgba(34,139,34,0.6)" if i in harvest_months else "rgba(70,130,180,0.7)"
        for i in range(12)
    ]
    fig = go.Figure(go.Bar(
        x=month_labels,
        y=df["rice_index"],
        marker_color=colors,
        hovertemplate="%{x}<br>Rice index: %{y:.1f}<extra></extra>",
    ))
    fig.add_hline(y=100, line_dash="dot", line_color="gray",
                  annotation_text="Annual average")
    fig.update_layout(
        height=220,
        yaxis_title="Rice Price Index (100 = annual avg)",
        title="Rice Price Index by Month — Harvest Discount Windows",
    )
    return mo.ui.plotly(fig)
```

### Year-End Chart helper

```python
def _build_yearend_chart(df, mo):
    import plotly.graph_objects as go

    fig = go.Figure(go.Bar(
        x=df["commodity"],
        y=df["premium_pct"],
        marker_color=["rgba(70,130,180,0.8)"] * len(df),
        hovertemplate=(
            "<b>%{x}</b><br>Nov–Dec premium: %{y:+.1f}%<br>"
            "Consistency: %{customdata}/17 yrs<extra></extra>"
        ),
        customdata=df["consistency"],
    ))
    fig.update_layout(
        height=200,
        yaxis_title="Avg % premium vs rest of year",
        title="Year-End Price Premium (Nov–Dec) by Commodity",
    )
    return mo.ui.plotly(fig)
```

---

## [Section 5] Seasonal Summary Table

Always visible. `mo.ui.table` with sortable columns.

```python
@app.cell
def _(summary_df, mo):
    mo.vstack([
        mo.md("## Seasonal Effect Summary — All Drivers"),
        mo.ui.table(
            summary_df[[
                "driver", "commodity", "premium_pct",
                "consistency", "lead_time"
            ]].sort_values("premium_pct", key=abs, ascending=False),
            sortable=True,
        ),
        mo.md(
            "_**Lead Time** = weeks or months before the seasonal event when "
            "procurement action should be taken — the most actionable column._"
        ),
    ])
```

**Notes:**
- Sort by `abs(premium_pct)` descending — both spikes (+) and harvest discounts (-)
  are surfaced at the top.
- Negative premiums (discounts) can be visually distinguished by pre-formatting
  the column as strings: `"−3.2% 🟢"` vs `"+8.5% 🔴"`.
- For full AG-Grid-style interactivity, `mo.ui.dataframe(summary_df)` provides
  search, sort, and filter in one call — useful upgrade path.

---

## Tab Assembly

```python
@app.cell
def _(
    driver_toggle, action_cards, data_notice,
    gregorian_heatmap_section, driver_chart,
    summary_table, commodity_dd, island_dd, year_slider, mo
):
    page2_content = mo.vstack([
        mo.md("# Seasonal Patterns"),
        mo.md("_Price Premiums by Season · 2007–2024 Historical Average_"),
        mo.hstack([commodity_dd, island_dd, year_slider, driver_toggle], gap="1rem"),
        action_cards,
        data_notice,
        gregorian_heatmap_section,
        driver_chart,
        summary_table,
    ], gap="2rem")
    return (page2_content,)
```

---

## marimo vs Dash: Key Differences on This Page

| Original (Dash/Vizro) | marimo equivalent |
|---|---|
| `dcc.Tabs` / tab-style toggle | `mo.ui.radio` (horizontal options) |
| Conditional `display` via callback | `if/elif` in cell, assign to variable, return last |
| `vm.AgGrid` | `mo.ui.table(sortable=True)` or `mo.ui.dataframe()` |
| `go.Figure` returned from `@capture` | `mo.ui.plotly(go.Figure(...))` |
| `Vizro` theme for annotation colors | Use `rgba()` colors + plotly template |

---

## States

| State | marimo behavior |
|---|---|
| Driver: Ramadan | Ramadan chart rendered; harvest/year-end cells return `None` silently |
| Driver: Harvest | Harvest chart rendered; other driver charts not rendered |
| Driver: Year-End | Year-end chart rendered |
| Driver: All Drivers | Informational text rendered; heatmap + summary table still shown |
| Commodity filter active | Ramadan chart filters to selected commodity; heatmap dims unselected rows via `opacity` in trace |
| Loading | Cell spinner shown automatically while `seasonal_data` cell runs |
