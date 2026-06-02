"""Global filter bar shared across all 4 pages."""

import dash_bootstrap_components as dbc
from dash import dcc

COMMODITY_OPTIONS = [
    {"label": "All Commodities", "value": "All"},
    {"label": "Rice", "value": "Rice"},
    {"label": "Cooking Oil", "value": "Cooking Oil"},
    {"label": "Sugar", "value": "Sugar"},
    {"label": "Flour", "value": "Flour"},
]

ISLAND_OPTIONS = [
    {"label": "All Island Groups", "value": "All"},
    {"label": "Java", "value": "Java"},
    {"label": "Sumatera", "value": "Sumatera"},
    {"label": "Kalimantan", "value": "Kalimantan"},
    {"label": "Sulawesi", "value": "Sulawesi"},
    {"label": "Eastern Indonesia", "value": "Eastern Indonesia"},
]


def render_filters() -> dbc.Row:
    """Render the global filter bar with commodity, island group, and year range."""
    return dbc.Row(
        className="bg-light p-3 mb-4 rounded",
        children=[
            dbc.Col(
                width=3,
                children=[
                    dbc.Label("Commodity", className="fw-bold small"),
                    dcc.Dropdown(
                        id="global-commodity",
                        options=COMMODITY_OPTIONS,
                        value="All",
                        clearable=False,
                    ),
                ],
            ),
            dbc.Col(
                width=3,
                children=[
                    dbc.Label("Island Group", className="fw-bold small"),
                    dcc.Dropdown(
                        id="global-island",
                        options=ISLAND_OPTIONS,
                        value="All",
                        clearable=False,
                    ),
                ],
            ),
            dbc.Col(
                width=6,
                children=[
                    dbc.Label("Year Range", className="fw-bold small"),
                    dcc.RangeSlider(
                        id="global-year-range",
                        min=2007,
                        max=2024,
                        step=1,
                        value=[2007, 2024],
                        marks={y: str(y) for y in range(2007, 2025, 3)},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ],
            ),
        ],
    )
