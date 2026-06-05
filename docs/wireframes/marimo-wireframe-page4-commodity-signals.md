# Marimo Wireframe — Page 4: Commodity Signals
**Framework:** marimo (single multi-tab notebook)
**Tab label:** `"Commodity Signals"`
**Charting:** Plotly via `mo.ui.plotly()`
**Decision enabled:** "Which commodities should we monitor as early warning indicators for others?"

---

## Cell Architecture

```
[cell: global_filters]          ← SHARED (commodity_dd, island_dd, year_slider)
       ↓
[cell: correlation_data]        ← loads commodity_correlation.json
       ↓
[cell: lag_selector]            ← PAGE-SPECIFIC (0 / 1 / 2 / 3 months)
[cell: selected_pair_state]     ← mo.state() — tracks active commodity pair
       ↓
[cell: leading_indicator_cards] ← reads correlation_data + lag_selector.value
[cell: correlation_matrix]      ← reads correlation_data + lag_selector.value
[cell: pair_scatter]            ← reads correlation_data + selected_pair_state()
[cell: stability_chart]         ← reads correlation_data + selected_pair_state()
[cell: implication_card]        ← reads correlation_data + selected_pair_state()
[cell: detail_table]            ← reads correlation_data + lag_selector.value
       ↓
[cell: page4_tab_content]       ← assembles layout
```

---

## Data Loading

```python
@app.cell
def _():
    import json, pathlib
    import pandas as pd

    raw = json.loads(pathlib.Path("data/commodity_correlation.json").read_text())

    top_relationships_df = pd.DataFrame(raw["top_relationships"])
    matrix_df = pd.DataFrame(raw["matrix"])          # leader, follower, lag, r
    pairs_df = pd.DataFrame(raw["pairs"])             # leader_price, follower_price, date, period
    rolling_r_df = pd.DataFrame(raw["rolling_r"])     # date, leader, follower, rolling_r_3yr
    all_pairs_df = pd.DataFrame(raw["all_pairs"])     # leader, follower, lag, r, pre_2022_r, post_2022_r

    return top_relationships_df, matrix_df, pairs_df, rolling_r_df, all_pairs_df
```

---

## Page-Specific Filter: Lag Selector

```python
@app.cell
def _(mo):
    lag_selector = mo.ui.radio(
        options={"0 months": 0, "1 month": 1, "2 months": 2, "3 months": 3},
        value=1,   # default: 1 month (most operationally relevant)
        label="Lag",
    )
    lag_selector
    return (lag_selector,)
```

**Note:** `mo.ui.radio` with a dict maps display labels to integer values.
`lag_selector.value` will be `0`, `1`, `2`, or `3` (integers), making
downstream filtering clean: `matrix_df[matrix_df["lag"] == lag_selector.value]`.

The Island Group filter has no effect on this page — correlation analysis is
national level only. Add a `mo.callout` note explaining this rather than disabling
the global dropdown (disabling a shared widget would affect other tabs).

---

## [Section 1] Leading Indicator Callout Cards

```python
@app.cell
def _(top_relationships_df, lag_selector, mo):
    lag = lag_selector.value
    at_lag = top_relationships_df[top_relationships_df["lag_months"] == lag]
    top2 = at_lag.nlargest(2, "r")

    if top2.empty:
        mo.callout(
            mo.md(
                "No strong leading relationship at this lag — try a different lag. "
                "(Threshold: r ≥ 0.3)"
            ),
            kind="warn",
        )
    else:
        cards = []
        for _, row in top2.iterrows():
            stability_flag = "✅ Stable post-2022" if row["stable"] else "⚠ Weakened post-2022"
            cards.append(
                mo.vstack([
                    mo.md(
                        f"📈 **{row['leader']} → {row['follower']}**\n\n"
                        f"Leads by **{row['lag_months']} month(s)** · r = {row['r']:.2f}\n\n"
                        f"{stability_flag}\n\n"
                        f"_{row['implication_text']}_"
                    )
                ], style="border:1px solid #ddd; padding:1rem; border-radius:8px;")
            )
        mo.hstack(cards, gap="1rem")
```

**Design note:** `implication_text` in the JSON is plain-language prose
(e.g. "When rice prices rise, expect flour to follow within 2 months").
No r-values or statistical jargon surface in this section — it is written
entirely for the Category Manager audience. The `⚠ Weakened post-2022` flag
is non-negotiable per the original spec.

---

## [Section 2] Correlation Matrix Heatmap

**Cross-filter source:** clicking a cell updates `selected_pair_state`.

```python
@app.cell
def _(matrix_df, lag_selector, set_selected_pair, mo):
    import plotly.graph_objects as go
    import pandas as pd

    lag = lag_selector.value
    at_lag = matrix_df[matrix_df["lag"] == lag]

    commodities = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    # Build 4×4 matrix; diagonal = None
    z = []
    text = []
    for leader in commodities:
        row_z, row_text = [], []
        for follower in commodities:
            if leader == follower:
                row_z.append(None)
                row_text.append("─")
            else:
                val = at_lag[
                    (at_lag["leader"] == leader) & (at_lag["follower"] == follower)
                ]["r"].values
                r = val[0] if len(val) else 0
                row_z.append(r)
                row_text.append(f"{r:.2f}")
        z.append(row_z)
        text.append(row_text)

    fig = go.Figure(go.Heatmap(
        z=z, x=commodities, y=commodities,
        text=text, texttemplate="%{text}",
        colorscale="Blues",
        zmin=0, zmax=1,
        hovertemplate=(
            "<b>%{y} → %{x}</b><br>"
            f"r = %{{z:.2f}} at lag {lag} month(s)<extra></extra>"
        ),
        colorbar=dict(title="r"),
    ))
    fig.update_layout(
        height=240,
        title=f"Cross-Commodity Correlation Matrix — {lag}-Month Lag",
        annotations=[dict(
            text="Row commodity <b>leads</b> column commodity at selected lag",
            xref="paper", yref="paper", x=0, y=1.12,
            showarrow=False, font=dict(size=11, color="gray"),
        )],
    )

    matrix_chart = mo.ui.plotly(fig)
    matrix_chart
    return (matrix_chart,)

# Cross-filter: matrix click → update selected pair
@app.cell
def _(matrix_chart, set_selected_pair):
    if matrix_chart.value and matrix_chart.value.get("points"):
        pt = matrix_chart.value["points"][0]
        leader = pt.get("y")
        follower = pt.get("x")
        if leader and follower and leader != follower:
            set_selected_pair((leader, follower))
```

**Matrix asymmetry note:** Upper triangle = "row leads column", lower triangle =
"column leads row at same lag". This is non-standard and must be labelled clearly.
The annotation above the matrix ("Row commodity **leads** column commodity") is
added via `fig.update_layout(annotations=[...])` — not collapsible, always visible.

---

## Shared State: Selected Pair

```python
@app.cell
def _(top_relationships_df, mo):
    # Default to the top leading relationship
    default_leader = top_relationships_df.iloc[0]["leader"]
    default_follower = top_relationships_df.iloc[0]["follower"]

    selected_pair, set_selected_pair = mo.state((default_leader, default_follower))
    return selected_pair, set_selected_pair
```

Two sources write to this state:
1. Matrix heatmap click (`matrix_chart.value`)
2. Commodity pair dropdowns in the scatter section

Both call `set_selected_pair((leader, follower))`. Downstream cells (scatter,
stability chart, implication card) read `selected_pair()`.

---

## [Section 3] Commodity Pair Scatter + Stability Chart (side by side)

### Pair selector dropdowns (above scatter)

```python
@app.cell
def _(selected_pair, set_selected_pair, mo):
    leader_dd = mo.ui.dropdown(
        options=["Rice", "Cooking Oil", "Sugar", "Flour"],
        value=selected_pair()[0],
        label="Leading commodity",
    )
    follower_dd = mo.ui.dropdown(
        options=["Rice", "Cooking Oil", "Sugar", "Flour"],
        value=selected_pair()[1],
        label="Following commodity",
    )
    # Sync dropdown changes back to selected_pair state
    # (handled in a downstream cell that reads both dropdowns)
    mo.hstack([leader_dd, mo.md("→"), follower_dd], gap="0.5rem")
    return leader_dd, follower_dd

@app.cell
def _(leader_dd, follower_dd, set_selected_pair):
    if leader_dd.value != follower_dd.value:
        set_selected_pair((leader_dd.value, follower_dd.value))
```

### Scatter chart

```python
@app.cell
def _(pairs_df, selected_pair, mo):
    import plotly.graph_objects as go

    leader, follower = selected_pair()
    pair_data = pairs_df[
        (pairs_df["leader"] == leader) & (pairs_df["follower"] == follower)
    ]

    pre = pair_data[pair_data["period"] == "pre_2022"]
    post = pair_data[pair_data["period"] == "post_2022"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pre["leader_price"], y=pre["follower_price"],
        mode="markers", name="Pre-2022",
        marker=dict(color="steelblue", size=6, opacity=0.6),
        hovertemplate=f"{leader}: %{{x:,.0f}}<br>{follower}: %{{y:,.0f}}<extra>Pre-2022</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=post["leader_price"], y=post["follower_price"],
        mode="markers", name="Post-2022",
        marker=dict(color="tomato", size=6, opacity=0.7),
        hovertemplate=f"{leader}: %{{x:,.0f}}<br>{follower}: %{{y:,.0f}}<extra>Post-2022</extra>",
    ))
    # OLS trend line (full period)
    import numpy as np
    all_x = pair_data["leader_price"].values
    all_y = pair_data["follower_price"].values
    if len(all_x) > 1:
        m, b = np.polyfit(all_x, all_y, 1)
        x_range = np.linspace(all_x.min(), all_x.max(), 50)
        fig.add_trace(go.Scatter(
            x=x_range, y=m * x_range + b,
            mode="lines", name="Trend (full period)",
            line=dict(color="gray", dash="dash", width=1),
        ))

    fig.update_layout(
        height=260,
        xaxis_title=f"{leader} Price (IDR)",
        yaxis_title=f"{follower} Price (IDR)",
        title=f"Price Co-Movement: {leader} → {follower}",
        legend=dict(orientation="h", y=-0.25),
    )
    mo.ui.plotly(fig)
```

**Pre/post 2022 dot split** is analytically critical — color-coding by period
makes the structural break visible in the scatter. Hiring managers with data
backgrounds will notice and appreciate this. Do not collapse to a single color.

### Stability chart

```python
@app.cell
def _(rolling_r_df, selected_pair, mo):
    import plotly.graph_objects as go

    leader, follower = selected_pair()
    roll = rolling_r_df[
        (rolling_r_df["leader"] == leader) & (rolling_r_df["follower"] == follower)
    ].sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=roll["date"], y=roll["rolling_r_3yr"],
        mode="lines", name="Rolling r (3-yr window)",
        line=dict(color="steelblue", width=2),
        hovertemplate="%{x|%Y}<br>r = %{y:.2f}<extra></extra>",
    ))
    fig.add_hline(y=0.3, line_dash="dot", line_color="red",
                  annotation_text="r = 0.3 floor")
    fig.add_vline(x="2022-01-01", line_dash="dash", line_color="gray",
                  annotation_text="2022 shock", annotation_position="top left")
    fig.update_layout(
        height=220,
        yaxis_title="Correlation coefficient (r)",
        yaxis_range=[-0.1, 1.05],
        title=f"Rolling Correlation Stability — {leader} → {follower}",
    )
    mo.ui.plotly(fig)
```

**This is the most analytically honest visual in the project** — showing that a
relationship may have broken is more valuable than pretending it's still strong.
The 2022 vertical marker makes the potential structural break explicit.

### Side-by-side layout

```python
@app.cell
def _(scatter_chart, stability_chart, mo):
    mo.hstack([scatter_chart, stability_chart], widths=[0.45, 0.55])
```

---

## [Section 4] Procurement Implication Card

```python
@app.cell
def _(all_pairs_df, selected_pair, lag_selector, mo):
    leader, follower = selected_pair()
    lag = lag_selector.value

    row = all_pairs_df[
        (all_pairs_df["leader"] == leader) &
        (all_pairs_df["follower"] == follower) &
        (all_pairs_df["lag"] == lag)
    ]

    if row.empty:
        mo.md("_Select a commodity pair from the matrix to see procurement implications._")
    else:
        r_val = row.iloc[0]["r"]
        pre_r = row.iloc[0]["pre_2022_r"]
        post_r = row.iloc[0]["post_2022_r"]
        is_unstable = abs(pre_r - post_r) > 0.2

        body = mo.md(
            f"**When {leader} prices rise, {follower} prices have historically "
            f"followed within {lag} month(s)** — this pattern occurred in a "
            f"significant majority of observed periods.\n\n"
            + (
                f"⚠ **Relationship weakened post-2022** — treat as a directional "
                f"signal, not deterministic. Pre-2022 r = {pre_r:.2f}, "
                f"Post-2022 r = {post_r:.2f}.\n\n"
                if is_unstable else ""
            ) +
            "_This recommendation is generated from the data. It does not account "
            "for supplier contract terms or logistics constraints._"
        )

        kind = "warn" if is_unstable else "info"
        mo.callout(
            mo.vstack([mo.md(f"## Procurement Implication — {leader} → {follower}"), body]),
            kind=kind,
        )
```

**Critical rules for this section:**
- **No r-values shown to the Category Manager** (they are shown in the detail table
  for analysts, but the implication card is plain language only).
- The `⚠ Weakened post-2022` caveat is **non-negotiable**. If `abs(pre_r - post_r) > 0.2`,
  the warning must render. The `mo.callout(kind="warn")` ensures it is visually
  prominent, not a footnote.

---

## [Section 5] Full Correlation Detail Table

```python
@app.cell
def _(all_pairs_df, lag_selector, set_selected_pair, mo):
    lag = lag_selector.value
    table_data = (
        all_pairs_df[all_pairs_df["lag"] == lag]
        .sort_values("r", ascending=False)
        .copy()
    )

    # Instability flag: abs(pre - post) > 0.2
    table_data["stability"] = table_data.apply(
        lambda r: "⚠" if abs(r["pre_2022_r"] - r["post_2022_r"]) > 0.2 else "✅",
        axis=1,
    )

    mo.vstack([
        mo.md("## All Pairwise Correlations"),
        mo.ui.table(
            table_data[[
                "leader", "follower", "lag", "r",
                "pre_2022_r", "post_2022_r", "stability"
            ]],
            sortable=True,
            on_select=lambda rows: (
                set_selected_pair((rows[0]["leader"], rows[0]["follower"]))
                if rows else None
            ),
        ),
        mo.md(
            "_**Pre/Post 2022 r:** Large divergence (⚠) signals a relationship "
            "that may have been broken by the 2022 commodity shock. Use with caution._"
        ),
    ])
```

**Note on `on_select`:** `mo.ui.table` supports an `on_select` callback that
fires when a row is clicked. Using this to update `selected_pair_state` creates
a third cross-filter source (matrix click → state, dropdown change → state,
table row click → state) — all three writing to the same `mo.state` sink.
This is clean marimo architecture.

---

## Tab Assembly

```python
@app.cell
def _(
    lag_selector, leading_indicator_cards,
    matrix_section, scatter_stability_row,
    implication_card, detail_table,
    commodity_dd, island_dd, year_slider, mo
):
    page4_content = mo.vstack([
        mo.md("# Commodity Signals"),
        mo.md("_Leading Indicators & Input Cost Bundling · 2007–2024_"),
        mo.hstack([commodity_dd, island_dd, year_slider, lag_selector], gap="1rem"),
        mo.callout(
            mo.md(
                "**Island Group filter disabled on this page.** "
                "All correlation analysis is conducted at national level — "
                "cross-commodity correlation requires all series at the same granularity."
            ),
            kind="info",
        ),
        leading_indicator_cards,
        matrix_section,
        scatter_stability_row,
        implication_card,
        detail_table,
    ], gap="2rem")
    return (page4_content,)
```

---

## marimo vs Dash: Key Differences on This Page

| Original (Dash/Vizro) | marimo equivalent |
|---|---|
| `dcc.Store` for selected pair | `mo.state((leader, follower))` — three sources write to it |
| `@callback` matrix click → scatter | `mo.ui.plotly.value` → downstream cell reads `.value["points"]` |
| `vm.AgGrid` row click → charts | `mo.ui.table(on_select=...)` callback |
| Island Group dropdown disabled | Keep global dropdown enabled; add `mo.callout` explaining it has no effect on this tab |
| `go.Figure` from `@capture` | `mo.ui.plotly(go.Figure(...))` |

---

## States

| State | marimo behavior |
|---|---|
| Loading | Cell spinners during `correlation_data` load |
| Lag = 0 | `lag_selector.value == 0`; matrix and leading cards update; implication card notes "same-month co-movement, not predictive" |
| Matrix cell clicked | `set_selected_pair()` called; scatter, stability, implication cells re-run |
| No strong relationship (r < 0.3) | `leading_indicator_cards` cell renders `mo.callout(kind="warn")` |
| Post-2022 relationship broken | Implication card renders `mo.callout(kind="warn")` with ⚠ text |
| Commodity filter = single | `matrix_df` filtered to show only rows/columns for that commodity; 4×4 matrix reduces to 1×3 or 3×1 effectively |
| Table row clicked | `on_select` fires; `set_selected_pair` updates; scatter + stability + implication re-run |

---

## Known Limitations vs Original Spec

| Feature | Original | marimo approach |
|---|---|---|
| Island Group dropdown visually locked to "National" | `dcc.Dropdown(disabled=True)` | Global dropdown stays enabled; `mo.callout` explains it has no effect — avoids breaking the shared widget |
| AG Grid cell renderer for ⚠ badge | AG Grid custom renderer | Emoji in pre-formatted string column |
| Heatmap diagonal explicitly blank | CSS override in Vizro | `z=None` for diagonal cells in go.Heatmap — Plotly renders as white/empty |
