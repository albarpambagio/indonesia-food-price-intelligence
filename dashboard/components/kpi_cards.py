"""KPI card row — reusable across Pages 1 and 3."""

import dash_bootstrap_components as dbc
from dash import html


def _fmt_idr(value: float | None) -> str:
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"Rp {value / 1_000_000:,.1f}M"
    if value >= 1_000:
        return f"Rp {value / 1_000:,.0f}K"
    return f"Rp {value:,.0f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"


def _color_for_delta(yoy_pct: float | None) -> str:
    if yoy_pct is None:
        return "secondary"
    return "danger" if yoy_pct > 0 else "success"


def render_kpi_cards(rows: list[dict]) -> dbc.Row:
    """Render a row of 4 KPI cards (one per commodity).

    Each row dict should have: commodity_consolidated, avg_price_idr, yoy_pct.
    """
    cards = []
    for row in rows:
        commodity = row.get("commodity_consolidated", "?")
        price = row.get("avg_price_idr")
        yoy = row.get("yoy_pct")
        color = _color_for_delta(yoy)
        icon = {"Rice": "🍚", "Cooking Oil": "🫒", "Sugar": "🍬", "Flour": "🌾"}.get(
            commodity, "📦"
        )
        cards.append(
            dbc.Col(
                md=3,
                children=dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(f"{icon} {commodity}", className="card-title text-muted mb-1"),
                            html.H3(_fmt_idr(price), className="card-text mb-1"),
                            dbc.Badge(
                                _fmt_pct(yoy),
                                color=color,
                                className="fs-6",
                            ),
                            html.Span(" YoY", className="text-muted ms-1 small"),
                        ]
                    ),
                    className="shadow-sm",
                ),
            )
        )
    return dbc.Row(cards, className="g-3 mb-4")
