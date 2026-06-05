"""Geographic disparity charts — Page 3.

Choropleth map, province comparison scatter, and province detail table.
Data source: geographic_disparity.json.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

GEOJSON_PATH = Path(__file__).resolve().parent.parent / "assets" / "indonesia_provinces.geojson"

ISLAND_COLORS = {
    "Java": "#4C72B0",
    "Sumatera": "#DD8452",
    "Kalimantan": "#55A868",
    "Sulawesi": "#C44E52",
    "Eastern Indonesia": "#8172B3",
}


def _load_geojson():
    if GEOJSON_PATH.exists():
        with open(GEOJSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    return None


def geo_choropleth(data_frame: pd.DataFrame) -> go.Figure:
    if data_frame.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
        )
        return fig

    geojson = _load_geojson()
    if geojson is None:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="GeoJSON not available", showarrow=False)],
        )
        return fig

    prov_avg = data_frame.groupby("admin1")["price_index_vs_java"].mean().reset_index()
    fig = go.Figure(
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
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(template="plotly_white", margin=dict(t=30), height=500)
    return fig


def geo_comparison_scatter(data_frame: pd.DataFrame) -> go.Figure:
    if data_frame.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
        )
        return fig

    fig = go.Figure()
    for island_name, color in ISLAND_COLORS.items():
        sub = data_frame[data_frame["island_group"] == island_name].sort_values("admin1")
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["admin1"],
                y=sub["price_index_vs_java"],
                name=island_name,
                mode="markers",
                marker=dict(color=color, size=10),
            )
        )
    fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Java baseline")
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Province",
        yaxis_title="Price Index vs Java",
        xaxis_tickangle=45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=30, b=100),
        height=400,
    )
    return fig


def geo_province_table(data_frame: pd.DataFrame) -> pd.DataFrame:
    if data_frame.empty:
        return pd.DataFrame(columns=["admin1", "island_group", "price_index_vs_java", "yoy_change_index", "months_with_data"])
    return data_frame.sort_values("price_index_vs_java").reset_index(drop=True)
