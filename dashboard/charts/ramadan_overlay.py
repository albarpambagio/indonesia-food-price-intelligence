"""Ramadan overlay chart — Page 2. Multi-year price index lines relative to Eid al-Fitr."""

import pandas as pd
import plotly.graph_objects as go

from dashboard.data_access import compute_ramadan_overlay

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


def ramadan_overlay(
    data_frame: pd.DataFrame,
    islamic_cal: pd.DataFrame,
    commodity_filter: str = "All",
    driver: str = "All",
) -> go.Figure:
    if driver != "Ramadan":
        return _empty_collapsed_fig()
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
            is_outlier = bool(year == 2022 and commodity == "Cooking Oil")
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
            ticktext=[
                "T-2 (2 mo before)",
                "T-1 (1 mo before)",
                "T (Eid month)",
                "T+1 (1 mo after)",
            ],
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=350,
        margin=dict(t=50, b=50, autoexpand=True),
    )
    return fig
