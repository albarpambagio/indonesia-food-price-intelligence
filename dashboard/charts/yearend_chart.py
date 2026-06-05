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
        height=10,
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
    commodity_avg = yearend.groupby("commodity_consolidated")["premium_pct"].mean().reset_index()

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
