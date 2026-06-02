"""Page 1 — Price Trends & Forecast.

Question: "Is now a good time to lock in bulk purchase contracts?"
Data: mart_price_trends_national + forecast.json
"""

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc

from dashboard.components.filters import render_filters
from dashboard.components.kpi_cards import render_kpi_cards
from dashboard.components.layout import forecast_footnote, page_header
from dashboard.data_access import (
    compute_yoy_delta,
    get_latest_prices,
    load_forecast_data,
    load_forecast_metadata,
    load_mart,
)

COMMODITY_COLORS = {
    "Rice": "#4C72B0",
    "Cooking Oil": "#DD8452",
    "Sugar": "#55A868",
    "Flour": "#C44E52",
}

dash.register_page(__name__, path="/", name="Price Trends")


def layout():
    return dbc.Container(
        [
            page_header(
                "Price Trends & Forecast",
                "17-year national price history with 6-month forecast overlay",
            ),
            render_filters(),
            dcc.Loading(dbc.Row(id="page1-kpi-cards"), type="circle"),
            dcc.Loading(dcc.Graph(id="page1-trend-chart"), type="circle"),
            dcc.Loading(dcc.Graph(id="page1-yoy-chart"), type="circle"),
            dbc.Row(
                [
                    dbc.Col(dcc.Loading(dbc.Card(id="page1-signal-card"), type="circle"), md=6),
                    dbc.Col(dcc.Loading(dbc.Card(id="page1-model-card"), type="circle"), type="circle", md=6),
                ],
                className="mb-4",
            ),
            forecast_footnote(),
        ],
        fluid=True,
    )


@callback(
    Output("page1-kpi-cards", "children"),
    Output("page1-trend-chart", "figure"),
    Output("page1-yoy-chart", "figure"),
    Output("page1-signal-card", "children"),
    Output("page1-model-card", "children"),
    Input("global-commodity", "value"),
    Input("global-island", "value"),
    Input("global-year-range", "value"),
)
def update_page1(commodity, island, year_range):
    filters = {}
    if commodity and commodity != "All":
        filters["commodity_consolidated"] = commodity
    if island and island != "All":
        filters["island_group"] = island

    df = load_mart("mart_price_trends_national", **filters)

    if df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(template="plotly_white", annotations=[dict(text="No data available", showarrow=False)])
        return [], empty_fig, empty_fig, dbc.Card(), dbc.Card()

    if year_range:
        df = df[(df["month"] >= f"{year_range[0]}-01-01") & (df["month"] <= f"{year_range[1]}-12-31")]

    latest = get_latest_prices(df)
    yoy_df = compute_yoy_delta(latest)
    kpi_rows = yoy_df.to_dict(orient="records")

    fig = go.Figure()
    for commodity_name in sorted(df["commodity_consolidated"].unique()):
        sub = df[df["commodity_consolidated"] == commodity_name].sort_values("month")
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
        fmeta = load_forecast_metadata()
        if not fdata.empty:
            forecast_commodities = fdata["commodity"].unique()
            show_commodities = [commodity] if commodity and commodity != "All" else forecast_commodities
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

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Price (IDR)",
        yaxis_tickformat="~s",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30),
        height=450,
    )

    yoy_fig = go.Figure()
    for commodity_name in sorted(df["commodity_consolidated"].unique()):
        sub = df[df["commodity_consolidated"] == commodity_name].copy()
        sub["_month_dt"] = sub["month"].astype(str).str[:7]
        sub = sub.sort_values("month")
        if len(sub) > 12:
            sub["yoy_pct"] = sub["avg_price_idr"].pct_change(periods=12) * 100
            color = COMMODITY_COLORS.get(commodity_name, "#888")
            yoy_fig.add_trace(
                go.Bar(
                    x=sub["month"],
                    y=sub["yoy_pct"],
                    name=commodity_name,
                    marker_color=color,
                )
            )
    yoy_fig.add_hline(y=0, line_dash="dash", line_color="gray")
    yoy_fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="YoY Change (%)",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30),
        height=350,
    )

    signal_children = _build_signal_card(yoy_df)
    model_children = _build_model_card()

    return render_kpi_cards(kpi_rows), fig, yoy_fig, signal_children, model_children


def _build_signal_card(yoy_df):
    cards = []
    for _, row in yoy_df.iterrows():
        commodity = row.get("commodity_consolidated", "?")
        yoy = row.get("yoy_pct")
        if yoy is not None:
            if yoy < -2:
                signal, color, label = "BUY", "success", "Price trending down — favorable for bulk purchase"
            elif yoy > 2:
                signal, color, label = "WATCH", "danger", "Price trending up — consider locking contracts soon"
            else:
                signal, color, label = "HOLD", "secondary", "Price stable — no urgency"
        else:
            signal, color, label = "N/A", "secondary", "Insufficient data"
        cards.append(
            dbc.Badge(
                f"{commodity}: {signal}",
                color=color,
                className="me-2 mb-2 fs-6",
                title=label,
            )
        )
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6("Procurement Action Zone", className="card-title text-muted"),
                html.Div(cards),
                html.Small(
                    "BUY = forecast avg < current -2% | HOLD = within ±2% | WATCH = forecast avg > current +2%",
                    className="text-muted",
                ),
            ]
        ),
        className="shadow-sm h-100",
    )


def _build_model_card():
    try:
        meta = load_forecast_metadata()
        models = meta.get("models", {})
        rows = []
        for commodity, info in models.items():
            selected = info.get("selected", "—")
            mae = info.get("holdout_mae", "—")
            rows.append(
                html.Tr(
                    [
                        html.Td(commodity),
                        html.Td(selected),
                        html.Td(f"{mae:,.0f}" if isinstance(mae, (int, float)) else mae),
                    ]
                )
            )
        return dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Model Selection (Holdout MAE)", className="card-title text-muted"),
                    dbc.Table(
                        [
                            html.Thead(html.Tr([html.Th("Commodity"), html.Th("Model"), html.Th("MAE (IDR)")])),
                            html.Tbody(rows),
                        ],
                        bordered=False,
                        size="sm",
                        className="mb-0",
                    ),
                ]
            ),
            className="shadow-sm h-100",
        )
    except Exception:
        return dbc.Card(dbc.CardBody("Forecast metadata not available"))
