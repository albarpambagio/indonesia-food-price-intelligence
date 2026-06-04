"""Trend + Forecast chart — Page 1 main analytical element.

Combines 17-year actual prices with 6-month forecast overlay and 95% CI.
"""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

from dashboard.data_access import load_forecast_data

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}


@capture("graph")
def trend_forecast(
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
        sub = data_frame[data_frame["commodity_consolidated"] == commodity_name].sort_values("month")
        color = COMMODITY_COLORS.get(commodity_name, "#888")
        fig.add_trace(
            go.Scatter(
                x=sub["month"],
                y=sub["avg_price_idr"],
                name=commodity_name,
                mode="lines",
                line=dict(color=color, width=2),
            )
        )

    try:
        fdata = load_forecast_data()
        if not fdata.empty:
            show_commodities = sorted(data_frame["commodity_consolidated"].unique())
            for fc in show_commodities:
                fsub = fdata[fdata["commodity"] == fc].sort_values("date")
                if fsub.empty:
                    continue
                color = COMMODITY_COLORS.get(fc, "#888")
                fig.add_trace(
                    go.Scatter(
                        x=fsub["date"],
                        y=fsub["forecast_price"],
                        name=f"{fc} (forecast)",
                        mode="lines",
                        line=dict(color=color, width=2, dash="dash"),
                    )
                )
                if "lower_95" in fsub.columns and "upper_95" in fsub.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=list(fsub["date"]) + list(fsub["date"][::-1]),
                            y=list(fsub["upper_95"]) + list(fsub["lower_95"][::-1]),
                            fill="toself",
                            fillcolor=f"rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},0.1)",
                            line=dict(width=0),
                            name=f"{fc} 95% CI",
                            showlegend=True,
                        )
                    )
    except Exception:
        pass

    fig.add_vline(x="2022-01-01", line_dash="dash", line_color="gray")
    fig.add_annotation(
        x="2022-01-01",
        y=1,
        text="Cooking oil export ban",
        showarrow=False,
        yref="paper",
        yanchor="bottom",
        font=dict(size=10, color="gray"),
    )

    try:
        fdata_vrect = load_forecast_data()
        if not fdata_vrect.empty:
            forecast_dates = sorted(fdata_vrect["date"].unique())
            if forecast_dates:
                actual_end = str(data_frame["month"].max())[:10]
                fig.add_vrect(
                    x0=actual_end,
                    x1=forecast_dates[-1],
                    fillcolor="gray",
                    opacity=0.08,
                    layer="below",
                    line_width=0,
                    annotation_text="Forecast region",
                    annotation_position="top left",
                )
    except Exception:
        pass

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Price (IDR)",
        yaxis_tickformat="~s",
        yaxis_automargin=True,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=50, b=50, autoexpand=True),
        height=450,
    )
    return fig
