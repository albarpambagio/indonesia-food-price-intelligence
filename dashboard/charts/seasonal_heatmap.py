"""Seasonal heatmap — Page 2. 4x12 matrix of price premiums by commodity x month."""

import pandas as pd
import plotly.express as px
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
    _all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot = pivot.reindex(columns=_all_months)

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
