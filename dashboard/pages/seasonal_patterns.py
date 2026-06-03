"""Page 2 — Seasonal Patterns.

Question: "When should we increase stock for each commodity?"
Data: mart_seasonal_patterns
"""

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dashboard.components.filters import render_filters
from dashboard.components.layout import page_header
from dashboard.data_access import load_mart

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

DRIVER_FLAGS = {
    "All": None,
    "Ramadan": ["flag_ramadan_t_minus_3", "flag_ramadan_t_minus_2", "flag_ramadan_t_minus_1", "flag_ramadan_eid_month", "flag_ramadan_t_plus_1"],
    "Harvest": ["flag_harvest_mar_apr", "flag_harvest_aug_sep"],
    "Year-End": ["flag_year_end"],
}

dash.register_page(__name__, path="/seasonal", name="Seasonal Patterns")


def layout():
    return dbc.Container(
        [
            page_header(
                "Seasonal Patterns",
                "Monthly price index vs annual average — Ramadan, harvest, and year-end effects",
            ),
            render_filters(),
            dbc.Row(
                dbc.Col(
                    dcc.RadioItems(
                        id="seasonal-driver",
                        options=[{"label": f" {k}", "value": k} for k in DRIVER_FLAGS],
                        value="All",
                        inline=True,
                        className="mb-3",
                    ),
                    width=12,
                )
            ),
            dcc.Loading(dcc.Graph(id="page2-heatmap"), type="circle"),
            dcc.Loading(dcc.Graph(id="page2-line-chart"), type="circle"),
            dcc.Loading(dcc.Graph(id="page2-ramadan-chart"), type="circle"),
            dcc.Loading(dbc.Table(id="page2-summary-table", bordered=True, hover=True, size="sm"), type="circle"),
        ],
        fluid=True,
    )


@callback(
    Output("page2-heatmap", "figure"),
    Output("page2-line-chart", "figure"),
    Output("page2-ramadan-chart", "figure"),
    Output("page2-summary-table", "children"),
    Input("global-commodity", "value"),
    Input("global-island", "value"),
    Input("global-year-range", "value"),
    Input("seasonal-driver", "value"),
)
def update_page2(commodity, island, year_range, driver):
    filters = {}
    if commodity and commodity != "All":
        filters["commodity_consolidated"] = commodity
    if island and island != "All":
        filters["island_group"] = island

    df = load_mart("mart_seasonal_patterns", **filters)
    empty_fig = go.Figure()
    empty_fig.update_layout(template="plotly_white", annotations=[dict(text="No data available", showarrow=False)])

    if df.empty:
        return empty_fig, empty_fig, empty_fig, []

    if year_range:
        df = df[(df["month"] >= f"{year_range[0]}-01-01") & (df["month"] <= f"{year_range[1]}-12-31")]

    df["month_of_year"] = df["month"].astype(str).str[5:7].astype(int)

    pivot = df.groupby(["commodity_consolidated", "month_of_year"])["price_index"].mean().reset_index()
    matrix = pivot.pivot(index="commodity_consolidated", columns="month_of_year", values="price_index")

    heatmap_fig = px.imshow(
        matrix,
        labels=dict(x="Month", y="Commodity", color="Price Index"),
        x=[MONTH_NAMES.get(m, str(m)) for m in sorted(matrix.columns)],
        y=matrix.index.tolist(),
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        text_auto=".0f",
    )
    heatmap_fig.update_layout(template="plotly_white", margin=dict(t=30), height=250)

    line_fig = go.Figure()
    for commodity_name in sorted(df["commodity_consolidated"].unique()):
        sub = df[df["commodity_consolidated"] == commodity_name]
        monthly = sub.groupby("month_of_year")["price_index"].mean().reindex(range(1, 13))
        color = COMMODITY_COLORS.get(commodity_name, "#888")
        line_fig.add_trace(
            go.Scatter(
                x=[MONTH_NAMES.get(m, str(m)) for m in range(1, 13)],
                y=monthly.values,
                name=commodity_name,
                mode="lines+markers",
                line=dict(color=color, width=2),
            )
        )
    line_fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Annual Avg = 100")

    if driver and driver != "All":
        flags = DRIVER_FLAGS.get(driver, [])
        for flag in flags:
            if flag in df.columns:
                highlighted = df[df[flag] == True]
                if not highlighted.empty:
                    hmonthly = highlighted.groupby("month_of_year")["price_index"].mean()
                    for commodity_name in highlighted["commodity_consolidated"].unique():
                        cm = hmonthly if commodity_name not in hmonthly.index else hmonthly
                        color = COMMODITY_COLORS.get(commodity_name, "#888")
                        line_fig.add_vrect(
                            x0=MONTH_NAMES.get(int(hmonthly.index.min()), ""),
                            x1=MONTH_NAMES.get(int(hmonthly.index.max()), ""),
                            fillcolor=color,
                            opacity=0.1,
                            layer="below",
                            line_width=0,
                        )
        line_fig.update_layout(title=f"Seasonal Pattern — {driver} Highlighted")

    line_fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Price Index (100 = Annual Avg)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30),
        height=400,
    )

    ramadan_df = df[
        (df.get("flag_ramadan_t_minus_3", False) == True)
        | (df.get("flag_ramadan_t_minus_2", False) == True)
        | (df.get("flag_ramadan_t_minus_1", False) == True)
        | (df.get("flag_ramadan_eid_month", False) == True)
        | (df.get("flag_ramadan_t_plus_1", False) == True)
    ] if any(
        f in df.columns for f in ["flag_ramadan_t_minus_3", "flag_ramadan_eid_month"]
    ) else df.iloc[0:0]

    ramadan_fig = go.Figure()
    if not ramadan_df.empty:
        for commodity_name in sorted(ramadan_df["commodity_consolidated"].unique()):
            sub = ramadan_df[ramadan_df["commodity_consolidated"] == commodity_name]
            color = COMMODITY_COLORS.get(commodity_name, "#888")
            ramadan_fig.add_trace(
                go.Scatter(
                    x=sub["month"],
                    y=sub["price_index"],
                    name=commodity_name,
                    mode="lines+markers",
                    line=dict(color=color, width=2),
                )
            )
    ramadan_fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Annual Avg = 100")
    ramadan_fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Price Index",
        title="Ramadan Period Price Index",
        margin=dict(t=40),
        height=350,
    )

    summary_rows = []
    for commodity_name in sorted(df["commodity_consolidated"].unique()):
        sub = df[df["commodity_consolidated"] == commodity_name]
        avg_price = sub["price_index"].mean()
        peak_month = sub.groupby("month_of_year")["price_index"].mean().idxmax()
        trough_month = sub.groupby("month_of_year")["price_index"].mean().idxmin()

        ramadan_mask = sub.get("flag_ramadan_eid_month", False) == True
        non_ramadan_mask = ~ramadan_mask
        ramadan_avg = sub[ramadan_mask]["price_index"].mean() if ramadan_mask.any() else None
        non_ramadan_avg = sub[non_ramadan_mask]["price_index"].mean() if non_ramadan_mask.any() else None
        premium = (
            round((ramadan_avg - non_ramadan_avg) / non_ramadan_avg * 100, 1)
            if ramadan_avg and non_ramadan_avg and non_ramadan_avg > 0
            else None
        )

        summary_rows.append(
            html.Tr([
                html.Td(commodity_name),
                html.Td(f"{avg_price:.1f}"),
                html.Td(MONTH_NAMES.get(peak_month, str(peak_month))),
                html.Td(MONTH_NAMES.get(trough_month, str(trough_month))),
                html.Td(f"+{premium}%" if premium else "—"),
            ])
        )

    summary_table = [
        html.Thead(html.Tr([html.Th("Commodity"), html.Th("Avg Index"), html.Th("Peak Month"), html.Th("Trough Month"), html.Th("Ramadan Premium")])),
        html.Tbody(summary_rows),
    ]

    return heatmap_fig, line_fig, ramadan_fig, summary_table
