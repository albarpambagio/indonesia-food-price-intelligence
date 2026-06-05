"""Dynamic action cards — Page 2.

3-panel procurement recommendation cards driven by compute_action_windows().
Cards: Action Now / Upcoming Spikes / Safe to Lock.
"""

import pandas as pd
import plotly.graph_objects as go

from dashboard.data_access import compute_action_windows

DRIVER_LABELS = {
    "Ramadan": "Ramadan",
    "Harvest": "Harvest",
    "Year-End": "Year-End",
}


def action_cards(
    data_frame: pd.DataFrame,
    islamic_cal: pd.DataFrame,
    commodity_filter: str = "All",
    driver: str = "All",
) -> go.Figure:
    if driver == "All":
        drivers = ["Ramadan", "Harvest", "Year-End"]
    else:
        drivers = [driver]

    all_windows = []
    for d in drivers:
        w = compute_action_windows(data_frame, d, islamic_cal)
        if not w.empty:
            w["driver"] = d
            all_windows.append(w)

    if not all_windows:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=180,
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[
                dict(
                    text="Select a seasonal driver to see procurement recommendations",
                    x=0.5, y=0.5, xref="paper", yref="paper",
                    showarrow=False, font=dict(size=14, color="gray"),
                )
            ],
            xaxis=dict(visible=False), yaxis=dict(visible=False),
        )
        return fig

    result = pd.concat(all_windows, ignore_index=True)
    if commodity_filter != "All":
        result = result[result["commodity"] == commodity_filter]

    if result.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            height=180,
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[
                dict(
                    text="No data available for the selected filters",
                    x=0.5, y=0.5, xref="paper", yref="paper",
                    showarrow=False, font=dict(size=14, color="gray"),
                )
            ],
            xaxis=dict(visible=False), yaxis=dict(visible=False),
        )
        return fig

    positive = result[result["spike_pct"] > 1].sort_values("spike_pct", ascending=False)
    negative = result[result["spike_pct"] <= 1].sort_values("spike_pct")

    if not positive.empty:
        top = positive.iloc[0]
        action_now = _format_card(
            title="Action Now",
            commodity=top["commodity"],
            pct=top["spike_pct"],
            consistency=top["consistency_score"],
            lead=top["lead_months"],
            driver_label=DRIVER_LABELS.get(top.get("driver", driver), str(top.get("driver", driver))),
            color="#dc3545",
        )
    else:
        action_now = _empty_card("Action Now", "No actionable spikes", "gray")

    remaining = positive.iloc[1:] if len(positive) > 1 else pd.DataFrame()
    upcoming_commodities = []
    if not remaining.empty:
        for _, r in remaining.iterrows():
            upcoming_commodities.append(
                f"<b>{r['commodity']}</b>: +{r['spike_pct']:.1f}% ({r['consistency_score']} yrs)"
            )
    if not negative.empty and len(negative) > 0:
        for _, r in negative.iterrows():
            upcoming_commodities.append(
                f"<b>{r['commodity']}</b>: {r['spike_pct']:+.1f}% ({r['consistency_score']} yrs)"
            )

    if upcoming_commodities:
        upcoming_text = "<br>".join(upcoming_commodities[:5])
        upcoming_spikes = _format_upcoming("Upcoming Spikes", upcoming_text, "#856404")
    else:
        upcoming_spikes = _empty_card("Upcoming Spikes", "No significant signals", "gray")

    if not negative.empty:

        def _parse_consistency(cs):
            parts = str(cs).split("/")
            if len(parts) == 2 and int(parts[1]) > 0:
                return int(parts[0]) / int(parts[1])
            return 0

        negative_sorted = negative.copy()
        negative_sorted["_consistency_ratio"] = negative_sorted["consistency_score"].apply(
            _parse_consistency
        )
        safe = negative_sorted.sort_values(["spike_pct", "_consistency_ratio"])
        safest = safe.iloc[0]
        safe_to_lock = _format_card(
            title="Safe to Lock",
            commodity=safest["commodity"],
            pct=safest["spike_pct"],
            consistency=safest["consistency_score"],
            lead=safest["lead_months"],
            driver_label=DRIVER_LABELS.get(safest.get("driver", driver), str(safest.get("driver", driver))),
            color="#28a745",
        )
    else:
        if not positive.empty:
            safest_positive = positive.iloc[-1]
            safe_to_lock = _format_card(
                title="Safe to Lock (least risky)",
                commodity=safest_positive["commodity"],
                pct=safest_positive["spike_pct"],
                consistency=safest_positive["consistency_score"],
                lead=safest_positive["lead_months"],
                driver_label=DRIVER_LABELS.get(driver, driver),
                color="#6c757d",
            )
        else:
            safe_to_lock = _empty_card("Safe to Lock", "No data", "gray")

    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    fig.add_annotation(
        x=0.17, y=0.85, xref="paper", yref="paper",
        text=action_now, showarrow=False,
        font=dict(size=11), align="center",
        bgcolor="#f8d7da", bordercolor="#dc3545", borderwidth=1,
    )
    fig.add_annotation(
        x=0.5, y=0.85, xref="paper", yref="paper",
        text=upcoming_spikes, showarrow=False,
        font=dict(size=11), align="center",
        bgcolor="#fff3cd", bordercolor="#ffc107", borderwidth=1,
    )
    fig.add_annotation(
        x=0.83, y=0.85, xref="paper", yref="paper",
        text=safe_to_lock, showarrow=False,
        font=dict(size=11), align="center",
        bgcolor="#d4edda", bordercolor="#28a745", borderwidth=1,
    )

    return fig


def _format_card(title: str, commodity: str, pct: float, consistency: str, lead: str, driver_label: str, color: str) -> str:
    arrow = "↑" if pct > 0 else "↓"
    direction = "increase" if pct > 0 else "decrease"
    return (
        f"<b style='font-size:13px;color:{color}'>{title}</b><br>"
        f"<b>{commodity}</b><br>"
        f"<span style='font-size:20px;color:{color}'>{arrow} {abs(pct):.1f}%</span><br>"
        f"<span style='font-size:10px;color:gray'>Historical {direction} during {driver_label}</span><br>"
        f"<span style='font-size:10px;color:gray'>Consistency: {consistency} | Lead: {lead}</span>"
    )


def _format_upcoming(title: str, items_text: str, color: str) -> str:
    return (
        f"<b style='font-size:13px;color:{color}'>{title}</b><br>"
        f"<span style='font-size:10px'>{items_text}</span>"
    )


def _empty_card(title: str, msg: str, color: str) -> str:
    return (
        f"<b style='font-size:13px;color:{color}'>{title}</b><br>"
        f"<span style='font-size:11px;color:gray'>{msg}</span>"
    )
