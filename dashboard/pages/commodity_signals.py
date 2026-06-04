"""Page 4 — Commodity Signals.

Question: "Which commodities to monitor as early warning indicators?"
Data: mart_correlation_summary + mart_commodity_correlation
"""

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dashboard.components.filters import render_filters
from dashboard.components.layout import page_header
from dashboard.data_access import load_mart

PAIR_COLORS = {
    "rice-oil": "#4C72B0",
    "rice-sugar": "#DD8452",
    "rice-flour": "#55A868",
    "oil-sugar": "#C44E52",
    "oil-flour": "#8172B3",
    "sugar-flour": "#CCB974",
}

dash.register_page(__name__, path="/signals", name="Commodity Signals")


def layout():
    return dbc.Container(
        [
            page_header(
                "Commodity Signals",
                "Cross-commodity correlation and leading indicators for bundled procurement timing",
            ),
            render_filters(),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.RadioItems(
                            id="lag-selector",
                            options=[
                                {"label": " 0 months (contemporaneous)", "value": 0},
                                {"label": " 1 month lag", "value": 1},
                                {"label": " 2 months lag", "value": 2},
                                {"label": " 3 months lag", "value": 3},
                            ],
                            value=1,
                            inline=True,
                            className="mb-3",
                        ),
                        width=12,
                    ),
                ]
            ),
            dcc.Loading(dbc.Row(id="page4-leading-cards"), type="circle"),
            dcc.Loading(dcc.Graph(id="page4-heatmap"), type="circle"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="pair-selector",
                            options=[
                                {"label": p.replace("-", " ↔ ").title(), "value": p}
                                for p in PAIR_COLORS
                            ],
                            value="rice-oil",
                            clearable=False,
                        ),
                        width=4,
                    ),
                ],
                className="mb-3",
            ),
            dcc.Loading(dcc.Graph(id="page4-scatter"), type="circle"),
            dcc.Loading(dcc.Graph(id="page4-rolling"), type="circle"),
            dcc.Loading(
                dbc.Table(id="page4-comparison-table", bordered=True, hover=True, size="sm"),
                type="circle",
            ),
            dcc.Loading(dbc.Card(id="page4-implication-card"), type="circle"),
        ],
        fluid=True,
    )


@callback(
    Output("page4-leading-cards", "children"),
    Output("page4-heatmap", "figure"),
    Output("page4-comparison-table", "children"),
    Output("page4-implication-card", "children"),
    Input("lag-selector", "value"),
)
def update_summary(lag):
    df = load_mart("mart_correlation_summary")
    empty_fig = go.Figure()
    empty_fig.update_layout(
        template="plotly_white", annotations=[dict(text="No data available", showarrow=False)]
    )

    if df.empty:
        return [], empty_fig, [], dbc.Card()

    lag_df = df[df["lag_months"] == lag].copy()
    lag_df["abs_r"] = lag_df["pearson_r"].abs()
    top2 = lag_df.nlargest(2, "abs_r")

    cards = []
    for _, row in top2.iterrows():
        pair = row["commodity_pair"].replace("-", " ↔ ").title()
        r = row["pearson_r"]
        a, b = row["commodity_pair"].split("-")
        direction = f"When {a.title()} rises, {b.title()} typically follows within {lag} month{'s' if lag != 1 else ''}."
        cards.append(
            dbc.Col(
                md=6,
                children=dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(f"r = {r:.3f}", className="text-muted mb-1"),
                            html.H5(pair, className="card-title"),
                            html.P(direction, className="card-text small"),
                        ]
                    ),
                    className="shadow-sm border-primary h-100",
                ),
            )
        )

    matrix_pivot = lag_df.pivot_table(
        index="commodity_pair", columns="lag_months", values="pearson_r"
    )
    if not matrix_pivot.empty:
        heatmap_fig = px.imshow(
            matrix_pivot.values,
            x=[f"Lag {int(c)}" for c in matrix_pivot.columns],
            y=matrix_pivot.index.tolist(),
            color_continuous_scale="RdBu_r",
            aspect="auto",
            text_auto=".3f",
            labels=dict(color="Pearson r"),
        )
        heatmap_fig.update_layout(template="plotly_white", margin=dict(t=30), height=350)
    else:
        heatmap_fig = empty_fig

    comparison_rows = []
    for pair in sorted(df["commodity_pair"].unique()):
        pdf = df[df["commodity_pair"] == pair]
        pre = pdf["pearson_r_pre_2022"].mean()
        post = pdf["pearson_r_post_2022"].mean()
        delta = pre - post if pre and post else None
        delta_color = (
            "text-danger"
            if (delta and delta > 0)
            else "text-success"
            if (delta and delta < 0)
            else ""
        )
        comparison_rows.append(
            html.Tr(
                [
                    html.Td(pair.replace("-", " ↔ ").title()),
                    html.Td(f"{pre:.3f}" if pre else "—"),
                    html.Td(f"{post:.3f}" if post else "—"),
                    html.Td(
                        f"{'+' if delta and delta > 0 else ''}{delta:.3f}" if delta else "—",
                        className=delta_color,
                    ),
                ]
            )
        )
    comparison_table = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Pair"),
                    html.Th("Pre-2022"),
                    html.Th("Post-2022"),
                    html.Th("Δ (weakening)"),
                ]
            )
        ),
        html.Tbody(comparison_rows),
    ]

    strongest = lag_df.nlargest(1, "abs_r").iloc[0] if not lag_df.empty else None
    if strongest:
        a, b = strongest["commodity_pair"].split("-")
        r = strongest["pearson_r"]
        implication = dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Procurement Implication", className="card-title text-muted"),
                    html.P(
                        f"The strongest leading relationship at {lag}-month lag is "
                        f"{a.title()} → {b.title()} (r = {r:.3f}). "
                        f"Procurement teams should monitor {a.title()} price movements as an early "
                        f"warning signal for {b.title()} procurement timing.",
                        className="card-text",
                    ),
                    html.Small(
                        "Note: Pre-2022 correlations are stronger than post-2022 for most pairs. "
                        "The 2022 cooking oil structural break has degraded correlation stability.",
                        className="text-muted",
                    ),
                ]
            ),
            className="shadow-sm",
        )
    else:
        implication = dbc.Card()

    return dbc.Row(cards, className="g-3 mb-4"), heatmap_fig, comparison_table, implication


@callback(
    Output("page4-scatter", "figure"),
    Output("page4-rolling", "figure"),
    Input("pair-selector", "value"),
)
def update_pair_charts(pair):
    df = load_mart("mart_commodity_correlation")
    empty_fig = go.Figure()
    empty_fig.update_layout(
        template="plotly_white", annotations=[dict(text="No data available", showarrow=False)]
    )

    if df.empty or not pair:
        return empty_fig, empty_fig

    a, b = pair.split("-")
    a_col = f"{a}_price"
    b_col = f"{b}_price"

    if a_col not in df.columns or b_col not in df.columns:
        return empty_fig, empty_fig

    scatter_fig = go.Figure()
    pre = df[df["month"] < "2022-01-01"]
    post = df[df["month"] >= "2022-01-01"]

    if not pre.empty:
        scatter_fig.add_trace(
            go.Scatter(
                x=pre[a_col],
                y=pre[b_col],
                name="Pre-2022",
                mode="markers",
                marker=dict(color="#4C72B0", opacity=0.6, size=5),
            )
        )
    if not post.empty:
        scatter_fig.add_trace(
            go.Scatter(
                x=post[a_col],
                y=post[b_col],
                name="Post-2022",
                mode="markers",
                marker=dict(color="#C44E52", opacity=0.6, size=5),
            )
        )
    scatter_fig.update_layout(
        template="plotly_white",
        xaxis_title=f"{a.title()} Price (IDR)",
        yaxis_title=f"{b.title()} Price (IDR)",
        title=f"{a.title()} vs {b.title()} — Pre/Post 2022",
        margin=dict(t=40),
        height=400,
    )

    rolling_fig = go.Figure()
    if len(df) >= 36:
        window = 36
        rolling_r = []
        months = []
        for i in range(window, len(df)):
            chunk = df.iloc[i - window : i]
            r = chunk[a_col].corr(chunk[b_col])
            rolling_r.append(r)
            months.append(chunk["month"].iloc[-1])
        color = PAIR_COLORS.get(pair, "#888")
        rolling_fig.add_trace(
            go.Scatter(
                x=months,
                y=rolling_r,
                mode="lines",
                name=f"{pair} (3yr rolling r)",
                line=dict(color=color, width=2),
            )
        )
        rolling_fig.add_vrect(
            x0="2022-01-01",
            x1="2022-12-31",
            fillcolor="red",
            opacity=0.1,
            layer="below",
            line_width=0,
            annotation_text="2022 shock",
        )
    rolling_fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Pearson r (36-month rolling)",
        title=f"Rolling Correlation Stability — {pair.replace('-', ' ↔ ').title()}",
        margin=dict(t=40),
        height=350,
    )

    return scatter_fig, rolling_fig
