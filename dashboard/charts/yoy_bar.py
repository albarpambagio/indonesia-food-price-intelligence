"""YoY Inflation bar chart — Page 1.

Grouped bar chart with reference bands and zero line.
"""

import pandas as pd
import plotly.graph_objects as go

from dashboard.data_access import compute_yoy_delta

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}


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
            height=350,
            margin=dict(t=20, b=20),
        )
        return fig

    df_with_yoy = compute_yoy_delta(data_frame)
    has_any_bar = False

    for commodity_name in sorted(df_with_yoy["commodity_consolidated"].unique()):
        sub = df_with_yoy[df_with_yoy["commodity_consolidated"] == commodity_name].copy()
        sub = sub.sort_values("month")
        sub = sub.dropna(subset=["yoy_pct"])
        if not sub.empty:
            has_any_bar = True
            color = COMMODITY_COLORS.get(commodity_name, "#888")
            fig.add_trace(
                go.Bar(
                    x=sub["month"],
                    y=sub["yoy_pct"],
                    name=commodity_name,
                    marker_color=color,
                    marker_line_color="rgba(0,0,0,0)",
                    hovertemplate="<b>%{fullData.name}</b><br>%{x|%b %Y}<br>YoY: %{y:+.1f}%<extra></extra>",
                )
            )

    if not has_any_bar:
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No YoY data available", showarrow=False)],
            height=350,
            margin=dict(t=20, b=20),
        )
        return fig

    for ref_y in [10, 20, 30, -10, -20, -30]:
        fig.add_hline(y=ref_y, line_dash="dash", line_color="rgba(128,128,128,0.3)", line_width=1)

    fig.add_hline(y=0, line_dash="solid", line_color="rgba(64,64,64,0.8)", line_width=3)
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="YoY Change (%)",
        yaxis_automargin=True,
        showlegend=True,
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(dtick="M12", tickformat="%Y"),
        margin=dict(t=50, b=50, autoexpand=True),
        height=350,
    )
    return fig
