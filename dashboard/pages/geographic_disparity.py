"""Page 3 — Geographic Disparity.

Question: "Which island group offers the best sourcing price?"
Data: mart_geo_disparity + vendored GeoJSON
"""

import json
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dashboard.components.filters import render_filters
from dashboard.components.layout import page_header
from dashboard.data_access import load_mart

GEOJSON_PATH = Path(__file__).resolve().parent.parent / "assets" / "indonesia_provinces.geojson"

ISLAND_COLORS = {
    "Java": "#4C72B0",
    "Sumatera": "#DD8452",
    "Kalimantan": "#55A868",
    "Sulawesi": "#C44E52",
    "Eastern Indonesia": "#8172B3",
}

dash.register_page(__name__, path="/geographic", name="Geographic Disparity")


def _load_geojson():
    if GEOJSON_PATH.exists():
        with open(GEOJSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    return None


def layout():
    return dbc.Container(
        [
            page_header(
                "Geographic Disparity",
                "Price index vs Java baseline — Cooking Oil only (Rice/Sugar/Flour limited to national aggregate)",
            ),
            render_filters(),
            dbc.Alert(
                "Geographic analysis is limited to Cooking Oil. Rice, Sugar, and Flour have no market-level "
                "actual prices in the WFP dataset — only national averages (market_id=974).",
                color="warning",
                className="mb-4",
            ),
            dcc.Loading(dbc.Row(id="page3-kpi-cards"), type="circle"),
            dcc.Loading(dcc.Graph(id="page3-choropleth"), type="circle"),
            dcc.Loading(dcc.Graph(id="page3-comparison-chart"), type="circle"),
            dcc.Loading(dbc.Table(id="page3-province-table", bordered=True, hover=True, size="sm"), type="circle"),
        ],
        fluid=True,
    )


@callback(
    Output("page3-kpi-cards", "children"),
    Output("page3-choropleth", "figure"),
    Output("page3-comparison-chart", "figure"),
    Output("page3-province-table", "children"),
    Input("global-commodity", "value"),
    Input("global-island", "value"),
    Input("global-year-range", "value"),
)
def update_page3(commodity, island, year_range):
    filters = {}
    if commodity and commodity != "All":
        filters["commodity_consolidated"] = commodity
    if island and island != "All":
        filters["island_group"] = island

    df = load_mart("mart_geo_disparity", **filters)
    empty_fig = go.Figure()
    empty_fig.update_layout(template="plotly_white", annotations=[dict(text="No data available", showarrow=False)])

    if df.empty:
        return [], empty_fig, empty_fig, []

    if year_range:
        df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year]

    kpi_cards = []
    for island_name in ["Java", "Sumatera", "Kalimantan", "Sulawesi", "Eastern Indonesia"]:
        row = latest[latest["island_group"] == island_name]
        if row.empty:
            continue
        idx = row["price_index_vs_java"].mean()
        yoy = row["yoy_change_index"].mean() if "yoy_change_index" in row.columns else None
        color = "danger" if (yoy and yoy > 0) else "success" if (yoy and yoy < 0) else "secondary"
        kpi_cards.append(
            dbc.Col(
                md=2,
                children=dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(island_name, className="card-title text-muted small"),
                            html.H4(f"{idx:.1f}", className="card-text"),
                            html.Small("vs Java (100)", className="text-muted"),
                            html.Br(),
                            dbc.Badge(
                                f"{'+' if yoy and yoy > 0 else ''}{yoy:.1f}" if yoy else "—",
                                color=color,
                                className="mt-1",
                            ) if yoy else None,
                        ]
                    ),
                    className="shadow-sm",
                ),
            )
        )
    kpi_cards.insert(0, dbc.Col(
        md=2,
        children=dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Java (Baseline)", className="card-title text-muted small"),
                    html.H4("100.0", className="card-text"),
                    html.Small("Reference index", className="text-muted"),
                ]
            ),
            className="shadow-sm border-primary",
        ),
    ))

    geojson = _load_geojson()
    choropleth_fig = go.Figure()
    if geojson and "admin1" in latest.columns:
        prov_avg = latest.groupby("admin1")["price_index_vs_java"].mean().reset_index()
        choropleth_fig = go.Figure(
            go.Choropleth(
                geojson=geojson,
                locations=prov_avg["admin1"],
                z=prov_avg["price_index_vs_java"],
                featureidkey="properties.state",
                colorscale="RdYlGn_r",
                colorbar_title="Price Index",
                text=prov_avg["admin1"],
                hoverinfo="text+z",
            )
        )
        choropleth_fig.update_geos(fitbounds="locations", visible=False)
    else:
        choropleth_fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="GeoJSON not available", showarrow=False)],
        )
    choropleth_fig.update_layout(template="plotly_white", margin=dict(t=30), height=500)

    comparison_fig = go.Figure()
    for island_name, color in ISLAND_COLORS.items():
        sub = latest[latest["island_group"] == island_name].sort_values("admin1")
        if sub.empty:
            continue
        comparison_fig.add_trace(
            go.Scatter(
                x=sub["admin1"],
                y=sub["price_index_vs_java"],
                name=island_name,
                mode="markers",
                marker=dict(color=color, size=10),
            )
        )
    comparison_fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Java baseline")
    comparison_fig.update_layout(
        template="plotly_white",
        xaxis_title="Province",
        yaxis_title="Price Index vs Java",
        xaxis_tickangle=45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=100),
        height=400,
    )

    table_rows = []
    for _, row in latest.sort_values("price_index_vs_java").iterrows():
        yoy = row.get("yoy_change_index")
        color = "text-danger" if (yoy and yoy > 0) else "text-success" if (yoy and yoy < 0) else ""
        table_rows.append(
            html.Tr([
                html.Td(row.get("admin1", "—")),
                html.Td(row.get("island_group", "—")),
                html.Td(f"{row.get('price_index_vs_java', 0):.1f}"),
                html.Td(f"{'+' if yoy and yoy > 0 else ''}{yoy:.1f}" if yoy else "—", className=color),
                html.Td(f"{row.get('months_with_data', 0):.0f}"),
            ])
        )
    table = [
        html.Thead(html.Tr([html.Th("Province"), html.Th("Island"), html.Th("Index"), html.Th("YoY Δ"), html.Th("Months")])),
        html.Tbody(table_rows),
    ]

    return dbc.Row(kpi_cards, className="g-2 mb-4"), choropleth_fig, comparison_fig, table
