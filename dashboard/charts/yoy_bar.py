"""YoY Inflation bar chart — Page 1.

Grouped bar chart: year-over-year % price change per commodity.
"""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}


@capture("graph")
def yoy_bar(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
) -> go.Figure:
    if commodity_filter != "All":
        data_frame = data_frame[data_frame["commodity_consolidated"] == commodity_filter]

    fig = go.Figure()

    if data_frame.empty:
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
        )
        return fig

    for commodity_name in sorted(data_frame["commodity_consolidated"].unique()):
        sub = data_frame[data_frame["commodity_consolidated"] == commodity_name].copy()
        sub = sub.sort_values("month")
        if len(sub) > 12:
            sub["yoy_pct"] = sub["avg_price_idr"].pct_change(periods=12) * 100
            color = COMMODITY_COLORS.get(commodity_name, "#888")
            fig.add_trace(
                go.Bar(
                    x=sub["month"],
                    y=sub["yoy_pct"],
                    name=commodity_name,
                    marker_color=color,
                )
            )

    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="YoY Change (%)",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30),
        height=350,
    )
    return fig
