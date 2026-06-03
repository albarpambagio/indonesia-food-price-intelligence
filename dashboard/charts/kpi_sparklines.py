"""KPI Sparklines chart — Page 1.

2x2 subplot grid: one sparkline per commodity with current price + YoY%.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from vizro.models.types import capture

from dashboard.data_access import compute_yoy_delta, get_latest_prices

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}


def _fmt_idr(value):
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"Rp {value / 1_000_000:,.1f}M"
    if value >= 1_000:
        return f"Rp {value / 1_000:,.0f}K"
    return f"Rp {value:,.0f}"


@capture("graph")
def kpi_sparklines(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
) -> go.Figure:
    commodities = ["Rice", "Cooking Oil", "Sugar", "Flour"]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=commodities,
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    if commodity_filter != "All":
        data_frame = data_frame[data_frame["commodity_consolidated"] == commodity_filter]

    latest = get_latest_prices(data_frame)
    yoy_df = compute_yoy_delta(latest)

    for idx, commodity in enumerate(commodities):
        row = idx // 2 + 1
        col = idx % 2 + 1
        color = COMMODITY_COLORS.get(commodity, "#888")

        is_filtered = commodity_filter != "All" and commodity != commodity_filter
        opacity = 0.3 if is_filtered else 1.0

        commodity_row = latest[latest["commodity_consolidated"] == commodity]
        yoy_row = yoy_df[yoy_df["commodity_consolidated"] == commodity]

        if commodity_row.empty:
            fig.add_trace(
                go.Scatter(x=[0], y=[0], mode="lines", line=dict(color="white", width=0), showlegend=False, hoverinfo="skip"),
                row=row, col=col,
            )
            fig.add_annotation(
                text="No data",
                xref=f"x{idx + 1 if idx > 0 else ''} domain",
                yref=f"y{idx + 1 if idx > 0 else ''} domain",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color="gray"),
            )
            continue

        price = commodity_row["avg_price_idr"].iloc[0]
        yoy = yoy_row["yoy_pct"].iloc[0] if not yoy_row.empty and "yoy_pct" in yoy_row.columns else None

        sub = data_frame[data_frame["commodity_consolidated"] == commodity].sort_values("month").tail(24)
        if not sub.empty:
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(sub))),
                    y=sub["avg_price_idr"].values,
                    mode="lines",
                    line=dict(color=color, width=2),
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=row, col=col,
            )

        yoy_str = f"{'↑' if yoy and yoy > 0 else '↓' if yoy and yoy < 0 else ''} {yoy:.1f}%" if yoy else "—"
        yoy_color = "red" if yoy and yoy > 0 else "green" if yoy and yoy < 0 else "gray"

        fig.add_annotation(
            text=f"<b>{_fmt_idr(price)}</b><br><span style='color:{yoy_color}'>{yoy_str} YoY</span>",
            xref=f"x{idx + 1 if idx > 0 else ''} domain",
            yref=f"y{idx + 1 if idx > 0 else ''} domain",
            x=0.5, y=-0.15,
            showarrow=False,
            font=dict(size=11, color=f"rgba(0,0,0,{opacity})"),
        )

    fig.update_layout(
        template="plotly_white",
        height=300,
        margin=dict(t=40, b=30),
        showlegend=False,
    )

    for i in range(1, 5):
        fig.update_xaxes(visible=False, row=(i - 1) // 2 + 1, col=(i - 1) % 2 + 1)
        fig.update_yaxes(visible=False, row=(i - 1) // 2 + 1, col=(i - 1) % 2 + 1)

    return fig
