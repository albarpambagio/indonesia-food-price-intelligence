"""Shared layout helpers: page header, forecast footnote."""

import dash_bootstrap_components as dbc
from dash import html


def page_header(title: str, subtitle: str = "") -> html.Div:
    """Render a consistent page header with title and optional subtitle."""
    return html.Div(
        className="mb-4",
        children=[
            html.H3(title, className="mb-1"),
            html.P(subtitle, className="text-muted mb-0") if subtitle else None,
        ],
    )


def forecast_footnote() -> dbc.Alert:
    """Render the model limitations footnote (always visible on forecast pages)."""
    return dbc.Alert(
        [
            html.H6("Model Limitations", className="alert-heading"),
            html.Ul(
                className="mb-0 small",
                children=[
                    html.Li("Forecast uses AutoARIMA/AutoETS with 6-month horizon."),
                    html.Li("95% confidence intervals widen significantly at 5-6 months."),
                    html.Li(
                        "Cooking Oil post-2022 structural break reduces forecast reliability. "
                        "A robustness trace (post-2022 only) is available as secondary overlay."
                    ),
                    html.Li(
                        "Forecast uses all price data (including aggregate flags); "
                        "dashboard actual-price charts use only 'actual' flag."
                    ),
                    html.Li("No volume weighting — all markets equal weight."),
                ],
            ),
        ],
        color="info",
        className="mb-4",
    )
