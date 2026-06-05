"""Harvest season chart — Page 2. Rice price index by month with harvest windows."""

import pandas as pd
import plotly.graph_objects as go

from dashboard.data_access import compute_heatmap_matrix

MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

HARVEST_MONTHS = {3, 4, 8, 9}


def _empty_collapsed_fig() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        height=10,
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def harvest_chart(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
    driver: str = "All",
) -> go.Figure:
    if driver != "Harvest":
        return _empty_collapsed_fig()

    if commodity_filter != "All" and commodity_filter != "Rice":
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="Harvest cycle analysis is Rice-specific", showarrow=False)],
            height=250,
        )
        return fig

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
            categoryarray=[
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
        ),
    )
    return fig
