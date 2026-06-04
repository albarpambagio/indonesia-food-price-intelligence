"""Procurement signal badges — Page 1.

BUY/HOLD/WATCH badges based on forecast vs current price comparison.
"""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

from dashboard.data_access import (
    compute_yoy_delta,
    get_latest_prices,
    load_forecast_data,
)


@capture("graph")
def signal_badges(
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
            height=200,
        )
        return fig

    latest = get_latest_prices(data_frame)
    yoy_df = compute_yoy_delta(latest)

    try:
        fdata = load_forecast_data()
        has_forecast = not fdata.empty
    except Exception:
        has_forecast = False
        fdata = None

    signals = []
    for _, row in latest.iterrows():
        commodity = row.get("commodity_consolidated", "?")
        current_price = row.get("avg_price_idr")

        if has_forecast and current_price and current_price > 0:
            fsub = fdata[fdata["commodity"] == commodity]
            if not fsub.empty and "forecast_price" in fsub.columns:
                forecast_avg = fsub["forecast_price"].mean()
                pct_change = (forecast_avg - current_price) / current_price * 100
                if pct_change < -2:
                    signal, color = "BUY", "#28a745"
                    reason = f"Forecast avg {pct_change:+.1f}% below current"
                elif pct_change > 2:
                    signal, color = "WATCH", "#dc3545"
                    reason = f"Forecast avg {pct_change:+.1f}% above current"
                else:
                    signal, color = "HOLD", "#6c757d"
                    reason = f"Forecast avg {pct_change:+.1f}% vs current"
                signals.append((commodity, signal, color, reason))
                continue

        yoy_row = yoy_df[yoy_df["commodity_consolidated"] == commodity]
        yoy = (
            yoy_row["yoy_pct"].iloc[0]
            if not yoy_row.empty and "yoy_pct" in yoy_row.columns
            else None
        )
        if yoy is not None:
            if yoy < -2:
                signal, color = "BUY", "#28a745"
                reason = "YoY trending down"
            elif yoy > 2:
                signal, color = "WATCH", "#dc3545"
                reason = "YoY trending up"
            else:
                signal, color = "HOLD", "#6c757d"
                reason = "Price stable"
        else:
            signal, color, reason = "N/A", "#6c757d", "Insufficient data"
        signals.append((commodity, signal, color, reason))

    for i, (commodity, signal, color, reason) in enumerate(signals):
        x_pos = 0.125 + i * 0.25
        fig.add_annotation(
            x=x_pos,
            y=0.7,
            xref="paper",
            yref="paper",
            text=f"<b>{commodity}</b><br><span style='color:{color};font-size:16px'>{signal}</span><br><span style='font-size:10px;color:gray'>{reason}</span>",
            showarrow=False,
            font=dict(size=12),
            align="center",
        )

    fig.update_layout(
        template="plotly_white",
        height=200,
        margin=dict(t=10, b=10, l=10, r=10, autoexpand=True),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig
