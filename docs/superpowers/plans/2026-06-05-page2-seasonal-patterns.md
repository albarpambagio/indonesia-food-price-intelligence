# Page 2 (Seasonal Patterns) Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Vizro Page 2 (Seasonal Patterns) with heatmap, Ramadan overlay, harvest chart, year-end chart, summary table, and action cards — all driven by `mart_price_trends_national`.

**Architecture:** Extend `data_access.py` with 3 computation helpers (action windows, heatmap matrix, Ramadan overlay). Create 5 chart files using `@capture("graph")` and `@capture("ag_grid")` decorators. Build page config with Pattern A conditional visibility (empty-figure swap). Register in `app.py`.

**Tech Stack:** Python, Vizro 0.1.x, Plotly, pandas, DuckDB, `@capture` decorator pattern.

---

## Chunk 1: Data Access Helpers

### Task 1: Extend `dashboard/data_access.py` — 3 new helpers + Islamic calendar loader

**Files:**
- Modify: `dashboard/data_access.py` (append 3 functions + 1 loader)

**Step 1: Add `load_islamic_calendar()` function**

Append to `dashboard/data_access.py` after `compute_yoy_delta`:

```python
@functools.lru_cache(maxsize=8)
def load_islamic_calendar() -> pd.DataFrame:
    """Load Islamic calendar from DuckDB int_islamic_calendar model."""
    conn = _connect()
    try:
        df = conn.execute(
            "SELECT year, eid_date, eid_month FROM wfp_intermediate.int_islamic_calendar ORDER BY year"
        ).fetchdf()
    finally:
        conn.close()
    if not df.empty:
        df["eid_date"] = pd.to_datetime(df["eid_date"])
    return df
```

**Step 2: Add `compute_heatmap_matrix()` function**

```python
def compute_heatmap_matrix(df_national: pd.DataFrame) -> pd.DataFrame:
    """Compute 4×12 matrix: commodity × month_of_year, values = mean premium % vs annual avg.

    Returns DataFrame with columns: commodity_consolidated, month_num (1-12), premium_pct.
    """
    if df_national.empty:
        return pd.DataFrame(columns=["commodity_consolidated", "month_num", "premium_pct"])

    df = df_national.copy()
    df["_year"] = pd.to_datetime(df["month"]).dt.year
    df["_month_num"] = pd.to_datetime(df["month"]).dt.month

    annual_avg = df.groupby(["commodity_consolidated", "_year"])["avg_price_idr"].mean().reset_index()
    annual_avg.columns = ["commodity_consolidated", "_year", "_annual_avg"]

    df = df.merge(annual_avg, on=["commodity_consolidated", "_year"], how="left")
    df["price_index"] = (df["avg_price_idr"] / df["_annual_avg"]) * 100

    result = (
        df.groupby(["commodity_consolidated", "_month_num"])["price_index"]
        .mean()
        .reset_index()
    )
    result.columns = ["commodity_consolidated", "month_num", "premium_pct"]
    result["premium_pct"] = result["premium_pct"] - 100  # convert index to premium %
    return result
```

**Step 3: Add `compute_ramadan_overlay()` function**

```python
def compute_ramadan_overlay(
    df_national: pd.DataFrame,
    commodity: str,
    islamic_cal: pd.DataFrame,
) -> pd.DataFrame:
    """Compute price index relative to Eid al-Fitr for one commodity.

    Returns DataFrame with columns: year, month_relative, price_index.
    month_relative ranges from -2 to +1 (months relative to Eid).
    """
    if df_national.empty or islamic_cal.empty:
        return pd.DataFrame(columns=["year", "month_relative", "price_index"])

    commodity_df = df_national[df_national["commodity_consolidated"] == commodity].copy()
    if commodity_df.empty:
        return pd.DataFrame(columns=["year", "month_relative", "price_index"])

    commodity_df["_month_dt"] = pd.to_datetime(commodity_df["month"])
    commodity_df["_year"] = commodity_df["_month_dt"].dt.year

    annual_avg = commodity_df.groupby("_year")["avg_price_idr"].mean().reset_index()
    annual_avg.columns = ["_year", "_annual_avg"]
    commodity_df = commodity_df.merge(annual_avg, on="_year", how="left")
    commodity_df["price_index"] = (commodity_df["avg_price_idr"] / commodity_df["_annual_avg"]) * 100

    cal = islamic_cal[["year", "eid_date"]].copy()
    cal["eid_month_num"] = cal["eid_date"].dt.month
    cal["eid_year"] = cal["eid_date"].dt.year

    merged = commodity_df.merge(
        cal[["year", "eid_year", "eid_month_num"]],
        left_on="_year",
        right_on="year",
        how="inner",
    )
    merged["month_relative"] = (
        (merged["_year"] - merged["eid_year"]) * 12
        + (merged["_month_num"] - merged["eid_month_num"])
    )

    result = merged[merged["month_relative"].between(-2, 1)][
        ["year", "month_relative", "price_index"]
    ].copy()
    result["year"] = result["year"].astype(int)
    return result.sort_values(["year", "month_relative"]).reset_index(drop=True)
```

**Step 4: Add `compute_action_windows()` function**

```python
def compute_action_windows(
    df_national: pd.DataFrame,
    driver: str,
    islamic_cal: pd.DataFrame,
) -> pd.DataFrame:
    """Compute per-commodity action window stats for a given seasonal driver.

    Returns DataFrame with columns:
    commodity, spike_pct, consistency_score, total_years, lead_months, data_scope.
    """
    if df_national.empty:
        return pd.DataFrame(
            columns=["commodity", "spike_pct", "consistency_score", "total_years", "lead_months", "data_scope"]
        )

    driver_months_map = {
        "Ramadan": None,  # computed dynamically from islamic_cal
        "Harvest": [3, 4, 8, 9],  # Mar-Apr, Aug-Sep
        "Year-End": [11, 12],  # Nov-Dec
    }

    df = df_national.copy()
    df["_month_dt"] = pd.to_datetime(df["month"])
    df["_year"] = df["_month_dt"].dt.year
    df["_month_num"] = df["_month_dt"].dt.month

    annual_avg = df.groupby(["commodity_consolidated", "_year"])["avg_price_idr"].mean().reset_index()
    annual_avg.columns = ["commodity_consolidated", "_year", "_annual_avg"]
    df = df.merge(annual_avg, on=["commodity_consolidated", "_year"], how="left")
    df["price_index"] = (df["avg_price_idr"] / df["_annual_avg"]) * 100

    results = []
    for commodity in sorted(df["commodity_consolidated"].unique()):
        commodity_df = df[df["commodity_consolidated"] == commodity].copy()

        if driver == "Ramadan":
            if islamic_cal.empty:
                continue
            cal = islamic_cal[["year", "eid_date"]].copy()
            cal["eid_month_num"] = cal["eid_date"].dt.month
            cal["eid_year"] = cal["eid_date"].dt.year
            merged = commodity_df.merge(
                cal[["year", "eid_year", "eid_month_num"]],
                left_on="_year",
                right_on="year",
                how="inner",
            )
            merged["month_relative"] = (
                (merged["_year"] - merged["eid_year"]) * 12
                + (merged["_month_num"] - merged["eid_month_num"])
            )
            driver_mask = merged["month_relative"].between(-2, 0)
            non_driver_mask = ~driver_mask
            driver_data = merged[driver_mask]
            non_driver_data = merged[non_driver_mask]
        elif driver in driver_months_map:
            driver_mask = commodity_df["_month_num"].isin(driver_months_map[driver])
            non_driver_mask = ~driver_mask
            driver_data = commodity_df[driver_mask]
            non_driver_data = commodity_df[non_driver_mask]
        else:
            continue

        if driver_data.empty or non_driver_data.empty:
            continue

        driver_avg = driver_data["price_index"].mean()
        non_driver_avg = non_driver_data["price_index"].mean()

        if non_driver_avg == 0:
            continue

        spike_pct = round((driver_avg - non_driver_avg) / non_driver_avg * 100, 1)

        yearly_driver = driver_data.groupby("_year")["price_index"].mean()
        yearly_annual = commodity_df.groupby("_year")["price_index"].mean()
        years_with_spike = sum(
            1 for y in yearly_driver.index
            if y in yearly_annual.index and yearly_driver[y] > yearly_annual[y]
        )
        total_years = len(yearly_driver)
        consistency_score = f"{years_with_spike}/{total_years}" if total_years > 0 else "0/0"

        lead_months_map = {
            "Ramadan": "2 months before Eid",
            "Harvest": "Mar-Apr or Aug-Sep",
            "Year-End": "Nov-Dec",
        }

        results.append({
            "commodity": commodity,
            "spike_pct": spike_pct,
            "consistency_score": consistency_score,
            "total_years": total_years,
            "lead_months": lead_months_map.get(driver, ""),
            "data_scope": "national",
        })

    result_df = pd.DataFrame(results)
    if not result_df.empty:
        result_df = result_df[result_df["spike_pct"].abs() > 3]
        result_df = result_df.sort_values("spike_pct", ascending=False).reset_index(drop=True)
    return result_df
```

**Step 5: Verify imports don't break existing code**

Run: `uv run python -c "from dashboard.data_access import load_mart, load_islamic_calendar, compute_heatmap_matrix, compute_ramadan_overlay, compute_action_windows; print('All imports OK')"`

**Step 6: Commit**

```bash
git add dashboard/data_access.py
git commit -m "feat: add Page 2 data access helpers (heatmap, ramadan, action windows)"
```

---

## Chunk 2: Chart Files

### Task 2: Create `dashboard/charts/seasonal_heatmap.py`

**Files:**
- Create: `dashboard/charts/seasonal_heatmap.py`

**Step 1: Create the heatmap chart file**

```python
"""Seasonal heatmap — Page 2. 4×12 matrix of price premiums by commodity × month."""

import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture

from dashboard.data_access import compute_heatmap_matrix

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


@capture("graph")
def seasonal_heatmap(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
) -> go.Figure:
    matrix = compute_heatmap_matrix(data_frame)

    if matrix.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
            height=250,
        )
        return fig

    pivot = matrix.pivot(
        index="commodity_consolidated",
        columns="month_num",
        values="premium_pct",
    )
    pivot.columns = [MONTH_NAMES.get(c, str(c)) for c in pivot.columns]
    pivot = pivot[["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]

    if commodity_filter != "All":
        pivot = pivot[pivot.index == commodity_filter]

    fig = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale="RdBu_r",
        aspect="auto",
        template="plotly_white",
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="",
        coloraxis_colorbar_title="Premium %",
        height=max(200, 80 * len(pivot) + 80),
        margin=dict(t=30, b=50, autoexpand=True),
    )
    return fig
```

**Step 2: Verify import**

Run: `uv run python -c "from dashboard.charts.seasonal_heatmap import seasonal_heatmap; print('seasonal_heatmap OK')"`

**Step 3: Commit**

```bash
git add dashboard/charts/seasonal_heatmap.py
git commit -m "feat: add seasonal heatmap chart (4x12 px.imshow)"
```

---

### Task 3: Create `dashboard/charts/ramadan_overlay.py`

**Files:**
- Create: `dashboard/charts/ramadan_overlay.py`

**Step 1: Create the Ramadan overlay chart file**

```python
"""Ramadan overlay chart — Page 2. Multi-year price index lines relative to Eid al-Fitr."""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

from dashboard.data_access import compute_ramadan_overlay, load_islamic_calendar

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}


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


@capture("graph")
def ramadan_overlay(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
    driver: str = "All",
) -> go.Figure:
    if driver != "Ramadan":
        return _empty_collapsed_fig()

    islamic_cal = load_islamic_calendar()
    commodities = (
        [commodity_filter]
        if commodity_filter != "All"
        else sorted(data_frame["commodity_consolidated"].unique())
    )

    fig = go.Figure()

    for commodity in commodities:
        overlay = compute_ramadan_overlay(data_frame, commodity, islamic_cal)
        if overlay.empty:
            continue

        color = COMMODITY_COLORS.get(commodity, "#888")

        for year in sorted(overlay["year"].unique()):
            year_data = overlay[overlay["year"] == year]
            is_outlier = year == 2022 and commodity == "Cooking Oil"
            fig.add_trace(
                go.Scatter(
                    x=year_data["month_relative"],
                    y=year_data["price_index"],
                    name=f"{commodity} {year}",
                    mode="lines",
                    line=dict(
                        color=color,
                        width=3 if is_outlier else 1,
                        dash="solid" if is_outlier else "dot",
                    ),
                    opacity=1.0 if is_outlier else 0.3,
                    showlegend=is_outlier,
                    hovertemplate=f"{commodity} {year}<br>T%{{x}}<br>Index: %{{y:.0f}}<extra></extra>",
                )
            )

        avg = overlay.groupby("month_relative")["price_index"].mean().reset_index()
        fig.add_trace(
            go.Scatter(
                x=avg["month_relative"],
                y=avg["price_index"],
                name=f"{commodity} avg",
                mode="lines",
                line=dict(color=color, width=3),
                showlegend=True,
                hovertemplate=f"{commodity} avg<br>T%{{x}}<br>Index: %{{y:.0f}}<extra></extra>",
            )
        )

    fig.add_hline(y=100, line_dash="dash", line_color="rgba(128,128,128,0.5)")

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Months relative to Eid al-Fitr",
        yaxis_title="Price Index (100 = annual avg)",
        xaxis=dict(
            tickvals=[-2, -1, 0, 1],
            ticktext=["T-2 (2 mo before)", "T-1 (1 mo before)", "T (Eid month)", "T+1 (1 mo after)"],
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=350,
        margin=dict(t=50, b=50, autoexpand=True),
    )
    return fig
```

**Step 2: Verify import**

Run: `uv run python -c "from dashboard.charts.ramadan_overlay import ramadan_overlay; print('ramadan_overlay OK')"`

**Step 3: Commit**

```bash
git add dashboard/charts/ramadan_overlay.py
git commit -m "feat: add Ramadan overlay chart (multi-year month_relative)"
```

---

### Task 4: Create `dashboard/charts/harvest_chart.py`

**Files:**
- Create: `dashboard/charts/harvest_chart.py`

**Step 1: Create the harvest chart file**

```python
"""Harvest season chart — Page 2. Rice price index by month with harvest windows."""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

from dashboard.data_access import compute_heatmap_matrix

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

HARVEST_MONTHS = {3, 4, 8, 9}  # Mar-Apr, Aug-Sep


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


@capture("graph")
def harvest_chart(
    data_frame: pd.DataFrame,
    driver: str = "All",
) -> go.Figure:
    if driver != "Harvest":
        return _empty_collapsed_fig()

    rice_df = data_frame[data_frame["commodity_consolidated"] == "Rice"].copy()
    if rice_df.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No Rice data available", showarrow=False)],
            height=250,
        )
        return fig

    matrix = compute_heatmap_matrix(rice_df)
    if matrix.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
            height=250,
        )
        return fig

    rice_matrix = matrix[matrix["commodity_consolidated"] == "Rice"].copy()
    rice_matrix["month_name"] = rice_matrix["month_num"].map(MONTH_NAMES)
    rice_matrix["is_harvest"] = rice_matrix["month_num"].isin(HARVEST_MONTHS)

    colors = ["#55A868" if h else "#4C72B0" for h in rice_matrix["is_harvest"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=rice_matrix["month_name"],
            y=rice_matrix["premium_pct"],
            marker_color=colors,
            hovertemplate="Month: %{x}<br>Premium: %{y:+.1f}%<extra></extra>",
        )
    )

    fig.add_hline(y=0, line_dash="solid", line_color="rgba(64,64,64,0.8)", line_width=2)

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Premium vs Annual Avg (%)",
        yaxis_automargin=True,
        showlegend=False,
        height=250,
        margin=dict(t=30, b=50, autoexpand=True),
        xaxis=dict(
            categoryorder="array",
            categoryarray=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        ),
    )
    return fig
```

**Step 2: Verify import**

Run: `uv run python -c "from dashboard.charts.harvest_chart import harvest_chart; print('harvest_chart OK')"`

**Step 3: Commit**

```bash
git add dashboard/charts/harvest_chart.py
git commit -m "feat: add harvest season chart (Rice deviation bars + harvest shading)"
```

---

### Task 5: Create `dashboard/charts/yearend_chart.py`

**Files:**
- Create: `dashboard/charts/yearend_chart.py`

**Step 1: Create the year-end chart file**

```python
"""Year-end price premium chart — Page 2. Nov-Dec premium by commodity."""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

from dashboard.data_access import compute_heatmap_matrix

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}


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


@capture("graph")
def yearend_chart(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
    driver: str = "All",
) -> go.Figure:
    if driver != "Year-End":
        return _empty_collapsed_fig()

    matrix = compute_heatmap_matrix(data_frame)
    if matrix.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
            height=250,
        )
        return fig

    yearend = matrix[matrix["month_num"].isin([11, 12])].copy()
    commodity_avg = (
        yearend.groupby("commodity_consolidated")["premium_pct"]
        .mean()
        .reset_index()
    )

    if commodity_filter != "All":
        commodity_avg = commodity_avg[commodity_avg["commodity_consolidated"] == commodity_filter]

    commodity_avg = commodity_avg.sort_values("premium_pct", ascending=False)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=commodity_avg["commodity_consolidated"],
            y=commodity_avg["premium_pct"],
            marker_color=[
                COMMODITY_COLORS.get(c, "#888") for c in commodity_avg["commodity_consolidated"]
            ],
            hovertemplate="Commodity: %{x}<br>Premium: %{y:+.1f}%<extra></extra>",
        )
    )

    fig.add_hline(y=0, line_dash="solid", line_color="rgba(64,64,64,0.8)", line_width=2)

    fig.update_layout(
        template="plotly_white",
        xaxis_title="",
        yaxis_title="Nov-Dec Premium (%)",
        yaxis_automargin=True,
        showlegend=False,
        height=250,
        margin=dict(t=30, b=50, autoexpand=True),
    )
    return fig
```

**Step 2: Verify import**

Run: `uv run python -c "from dashboard.charts.yearend_chart import yearend_chart; print('yearend_chart OK')"`

**Step 3: Commit**

```bash
git add dashboard/charts/yearend_chart.py
git commit -m "feat: add year-end premium chart (4-commodity Nov-Dec bars)"
```

---

### Task 6: Create `dashboard/charts/seasonal_summary_table.py`

**Files:**
- Create: `dashboard/charts/seasonal_summary_table.py`

**Step 1: Create the summary table file**

```python
"""Seasonal summary table — Page 2. Action windows across all drivers."""

import pandas as pd
from vizro.models.types import capture

from dashboard.data_access import compute_action_windows, load_islamic_calendar


@capture("ag_grid")
def seasonal_summary_table(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
) -> pd.DataFrame:
    islamic_cal = load_islamic_calendar()

    all_windows = []
    for driver in ["Ramadan", "Harvest", "Year-End"]:
        windows = compute_action_windows(data_frame, driver, islamic_cal)
        if not windows.empty:
            windows["driver"] = driver
            all_windows.append(windows)

    if not all_windows:
        return pd.DataFrame(
            columns=["Driver", "Commodity", "Spike %", "Consistency", "Lead Time", "Data Scope"]
        )

    result = pd.concat(all_windows, ignore_index=True)
    result = result.rename(columns={
        "driver": "Driver",
        "commodity": "Commodity",
        "spike_pct": "Spike %",
        "consistency_score": "Consistency",
        "lead_months": "Lead Time",
        "data_scope": "Data Scope",
    })

    if commodity_filter != "All":
        result = result[result["Commodity"] == commodity_filter]

    result = result.sort_values("Spike %", ascending=False).reset_index(drop=True)
    return result[["Driver", "Commodity", "Spike %", "Consistency", "Lead Time", "Data Scope"]]
```

**Step 2: Verify import**

Run: `uv run python -c "from dashboard.charts.seasonal_summary_table import seasonal_summary_table; print('seasonal_summary_table OK')"`

**Step 3: Commit**

```bash
git add dashboard/charts/seasonal_summary_table.py
git commit -m "feat: add seasonal summary table (ag_grid, all drivers)"
```

---

## Chunk 3: Page Config + Registration

### Task 7: Create `dashboard/pages/seasonal_patterns.py`

**Files:**
- Overwrite: `dashboard/pages/seasonal_patterns.py` (old Dash code → Vizro config)

**Step 1: Create the page config file**

```python
"""Page 2 — Seasonal Patterns (Vizro).

Question: "When should we increase stock for each commodity?"
Data: mart_price_trends_national + int_islamic_calendar
"""

import vizro.models as vm

from dashboard.charts.harvest_chart import harvest_chart
from dashboard.charts.ramadan_overlay import ramadan_overlay
from dashboard.charts.seasonal_heatmap import seasonal_heatmap
from dashboard.charts.seasonal_summary_table import seasonal_summary_table
from dashboard.charts.yearend_chart import yearend_chart


def _build_action_cards() -> vm.Card:
    return vm.Card(
        text="""
### Action Window — Seasonal Driver

Select a seasonal driver above to see procurement timing recommendations.

- **Ramadan**: Stock up 2 months before Eid al-Fitr
- **Harvest**: Rice discounts during Mar-Apr and Aug-Sep
- **Year-End**: Watch Nov-Dec price premiums

Cards update when the driver toggle changes.
        """,
    )


def _build_data_availability_notice() -> vm.Card:
    return vm.Card(
        text="""
> ℹ️ Seasonal analysis uses national-level data for Rice, Sugar, Flour.
> Island-level breakdown available for Cooking Oil only.
> Rice/Sugar/Flour data ends March 2020 (WFP data gap).
        """,
    )


seasonal_patterns_page = vm.Page(
    title="Seasonal Patterns",
    description="Price premiums by season — 2007-2024 historical average",
    components=[
        vm.Container(
            components=[
                _build_action_cards(),
                _build_data_availability_notice(),
                vm.Graph(
                    id="seasonal_heatmap",
                    figure=seasonal_heatmap(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.Graph(
                    id="ramadan_overlay",
                    figure=ramadan_overlay(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.Graph(
                    id="harvest_chart",
                    figure=harvest_chart(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.Graph(
                    id="yearend_chart",
                    figure=yearend_chart(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.AgGrid(
                    id="seasonal_summary_table",
                    figure=seasonal_summary_table(
                        data_frame="mart_price_trends_national",
                    ),
                ),
            ],
            layout=vm.Flex(direction="column", gap="20px"),
        ),
    ],
    controls=[
        vm.Parameter(
            id="param-commodity",
            targets=[
                "seasonal_heatmap.commodity_filter",
                "ramadan_overlay.commodity_filter",
                "yearend_chart.commodity_filter",
                "seasonal_summary_table.commodity_filter",
            ],
            selector=vm.Dropdown(
                options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
                value="All",
                multi=False,
            ),
        ),
        vm.Parameter(
            id="param-driver",
            targets=[
                "ramadan_overlay.driver",
                "harvest_chart.driver",
                "yearend_chart.driver",
            ],
            selector=vm.RadioItems(
                options=["All", "Ramadan", "Harvest", "Year-End"],
                value="All",
            ),
        ),
    ],
)
```

**Step 2: Verify page import**

Run: `uv run python -c "from dashboard.pages.seasonal_patterns import seasonal_patterns_page; print(f'Page title: {seasonal_patterns_page.title}')"`

**Step 3: Commit**

```bash
git add dashboard/pages/seasonal_patterns.py
git commit -m "feat: add Page 2 seasonal patterns (Vizro config, Pattern A)"
```

---

### Task 8: Register Page 2 in `dashboard/app.py`

**Files:**
- Modify: `dashboard/app.py:16-19`

**Step 1: Add import and register in pages list**

Edit `dashboard/app.py`:

```python
from dashboard.pages.price_trends import price_trends_page
from dashboard.pages.seasonal_patterns import seasonal_patterns_page

dashboard = vm.Dashboard(
    pages=[price_trends_page, seasonal_patterns_page],
)
```

**Step 2: Verify registration**

Run: `uv run python -c "from dashboard.app import dashboard; print(f'Pages: {len(dashboard.pages)}'); print([p.title for p in dashboard.pages])"`

Expected output: `Pages: 2` and `['Price Trends & Forecast', 'Seasonal Patterns']`

**Step 3: Commit**

```bash
git add dashboard/app.py
git commit -m "feat: register Page 2 (Seasonal Patterns) in dashboard"
```

---

## Chunk 4: Verification

### Task 9: Smoke tests + Lint

**Files:** None (verification only)

**Step 1: Run all smoke tests**

```bash
# Test 1: Vizro picks up Page 2
uv run python -c "from dashboard.app import dashboard; print(f'Pages: {len(dashboard.pages)}')"

# Test 2: Page titles
uv run python -c "from dashboard.app import dashboard; print([p.title for p in dashboard.pages])"

# Test 3: Heatmap renders
uv run python -c "
from dashboard.charts.seasonal_heatmap import seasonal_heatmap
from dashboard.data_access import load_mart
fig = seasonal_heatmap(load_mart('mart_price_trends_national'))
print('heatmap traces:', len(fig.data))
"

# Test 4: Ramadan overlay renders
uv run python -c "
from dashboard.charts.ramadan_overlay import ramadan_overlay
from dashboard.data_access import load_mart
fig = ramadan_overlay(load_mart('mart_price_trends_national'), driver='Ramadan')
print('ramadan traces:', len(fig.data))
"

# Test 5: Action windows compute
uv run python -c "
from dashboard.data_access import load_mart, compute_action_windows, load_islamic_calendar
cal = load_islamic_calendar()
df = load_mart('mart_price_trends_national')
result = compute_action_windows(df, 'Ramadan', cal)
print(result[['commodity', 'spike_pct', 'consistency_score']].to_string())
"
```

**Step 2: Run lint and format**

```bash
ruff check .
ruff format --check .
```

**Step 3: Commit any lint fixes**

```bash
git add -A
git commit -m "fix: lint and format fixes for Page 2"
```

---

## Key Constraints Summary

| # | Constraint | Source |
|---|-----------|--------|
| 1 | Primary source = `mart_price_trends_national` (639 rows, all 4), NOT `mart_seasonal_patterns` (35 rows, Cooking Oil only) | LEARNINGS §99 |
| 2 | Rice/Sugar/Flour national prices end 2020-03 — must disclose | DuckDB query |
| 3 | `month_relative` T-2 to T+1 (monthly grain, not weekly) | LEARNINGS §100 |
| 4 | `COMMODITY_COLORS` must match Page 1: `#4C72B0`, `#DD8452`, `#55A868`, `#C44E52` | Page 1 charts |
| 5 | Never pass literal default args in `vm.Graph(figure=fn(...))` | LEARNINGS §98 |
| 6 | `vm.Parameter` not `vm.Filter` for dropdowns containing "All" | LEARNINGS §97 |
| 7 | `vm.AgGrid` requires `@capture("ag_grid")`, not `@capture("graph")` | Vizro 0.1.53 API |
| 8 | Island filter only applies to Cooking Oil — silently ignore for other commodities | Handoff §6 |

## Files NOT to Modify

| File | Reason |
|------|--------|
| `dashboard/data_access.py` (existing functions) | Extend only; don't change signatures |
| `dashboard/data_manager.py` | Already correct, all 6 marts registered |
| `transform/` (any dbt model) | Complete, 77 tests pass |
| `dashboard/charts/*.py` for Page 1 | Working code |
| `dashboard/pages/price_trends.py` | Working code |
| `docs/wireframes/*` | Reference only |

## Reference Artifacts

| What | Path |
|------|------|
| Page 2 full handoff | `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` |
| Phase C handoff | `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md` |
| Implementation plan §6.C.2 | `docs/implementation-plan.md` (lines 470–484) |
| Vizro learnings §87–100 | `docs/LEARNINGS.md` |
| Page 1 reference code | `dashboard/pages/price_trends.py` + `dashboard/charts/*.py` |
| Wireframe spec | `docs/wireframes/wfp-wireframe-page2-seasonal-patterns.md` |
| Spike reference (px.imshow) | `dashboard/spike/custom_charts.py` |
