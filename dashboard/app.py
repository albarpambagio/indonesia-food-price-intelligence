"""WFP Food Price Intelligence — Dash application entry point.

Run locally: uv run python dashboard/app.py
HF Spaces: gunicorn app:server --bind 0.0.0.0:7860
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.CERULEAN],
    suppress_callback_exceptions=True,
    title="WFP Food Price Intelligence",
)

server = app.server

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.NavbarSimple(
            brand="WFP Food Price Intelligence",
            brand_href="/",
            color="primary",
            dark=True,
            children=[
                dbc.NavItem(dbc.NavLink("Price Trends", href="/")),
                dbc.NavItem(dbc.NavLink("Seasonal Patterns", href="/seasonal")),
                dbc.NavItem(dbc.NavLink("Geographic Disparity", href="/geographic")),
                dbc.NavItem(dbc.NavLink("Commodity Signals", href="/signals")),
            ],
        ),
        dash.page_container,
    ],
)

if __name__ == "__main__":
    app.run(debug=True, port=7860)
