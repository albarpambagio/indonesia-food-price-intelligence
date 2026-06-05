"""Commodity correlation charts — Page 4.

Correlation heatmap, pair scatter, rolling correlation, and pre/post comparison.
Data source: commodity_correlation.json, correlation_summary.json.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PAIR_COLORS = {
    "rice-oil": "#4C72B0",
    "rice-sugar": "#DD8452",
    "rice-flour": "#55A868",
    "oil-sugar": "#C44E52",
    "oil-flour": "#8172B3",
    "sugar-flour": "#CCB974",
}


def correlation_heatmap(summary_df: pd.DataFrame, lag: int = 1) -> go.Figure:
    if summary_df.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
            height=350,
        )
        return fig

    lag_df = summary_df[summary_df["lag_months"] == lag].copy()
    if lag_df.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data for selected lag", showarrow=False)],
            height=350,
        )
        return fig

    matrix_pivot = lag_df.pivot_table(
        index="commodity_pair", columns="lag_months", values="pearson_r"
    )
    if matrix_pivot.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
            height=350,
        )
        return fig

    fig = px.imshow(
        matrix_pivot.values,
        x=[f"Lag {int(c)}" for c in matrix_pivot.columns],
        y=matrix_pivot.index.tolist(),
        color_continuous_scale="RdBu_r",
        aspect="auto",
        text_auto=".3f",
        labels=dict(color="Pearson r"),
    )
    fig.update_layout(template="plotly_white", margin=dict(t=30), height=350)
    return fig


def pair_scatter(corr_df: pd.DataFrame, pair: str) -> go.Figure:
    if corr_df.empty or not pair:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
            height=400,
        )
        return fig

    a, b = pair.split("-")
    a_col = f"{a}_price"
    b_col = f"{b}_price"

    if a_col not in corr_df.columns or b_col not in corr_df.columns:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="Price columns not found", showarrow=False)],
            height=400,
        )
        return fig

    fig = go.Figure()
    pre = corr_df[corr_df["month"] < "2022-01-01"]
    post = corr_df[corr_df["month"] >= "2022-01-01"]

    if not pre.empty:
        fig.add_trace(
            go.Scatter(
                x=pre[a_col],
                y=pre[b_col],
                name="Pre-2022",
                mode="markers",
                marker=dict(color="#4C72B0", opacity=0.6, size=5),
            )
        )
    if not post.empty:
        fig.add_trace(
            go.Scatter(
                x=post[a_col],
                y=post[b_col],
                name="Post-2022",
                mode="markers",
                marker=dict(color="#C44E52", opacity=0.6, size=5),
            )
        )
    fig.update_layout(
        template="plotly_white",
        xaxis_title=f"{a.title()} Price (IDR)",
        yaxis_title=f"{b.title()} Price (IDR)",
        title=f"{a.title()} vs {b.title()} \u2014 Pre/Post 2022",
        margin=dict(t=40),
        height=400,
    )
    return fig


def rolling_correlation(corr_df: pd.DataFrame, pair: str) -> go.Figure:
    if corr_df.empty or not pair:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_white",
            annotations=[dict(text="No data available", showarrow=False)],
            height=350,
        )
        return fig

    a, b = pair.split("-")
    a_col = f"{a}_price"
    b_col = f"{b}_price"

    fig = go.Figure()
    if len(corr_df) >= 36:
        window = 36
        rolling_r = []
        months = []
        for i in range(window, len(corr_df)):
            chunk = corr_df.iloc[i - window : i]
            r = chunk[a_col].corr(chunk[b_col])
            rolling_r.append(r)
            months.append(chunk["month"].iloc[-1])
        color = PAIR_COLORS.get(pair, "#888")
        fig.add_trace(
            go.Scatter(
                x=months,
                y=rolling_r,
                mode="lines",
                name=f"{pair} (3yr rolling r)",
                line=dict(color=color, width=2),
            )
        )
        fig.add_vrect(
            x0="2022-01-01",
            x1="2022-12-31",
            fillcolor="red",
            opacity=0.1,
            layer="below",
            line_width=0,
            annotation_text="2022 shock",
        )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Pearson r (36-month rolling)",
        title=f"Rolling Correlation Stability \u2014 {pair.replace('-', ' \u2194 ').title()}",
        margin=dict(t=40),
        height=350,
    )
    return fig


def pre_post_comparison_table(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame(columns=["commodity_pair", "pearson_r_pre_2022", "pearson_r_post_2022", "delta"])

    rows = []
    for pair in sorted(summary_df["commodity_pair"].unique()):
        pdf = summary_df[summary_df["commodity_pair"] == pair]
        pre = pdf["pearson_r_pre_2022"].mean()
        post = pdf["pearson_r_post_2022"].mean()
        delta = pre - post if pre and post else None
        rows.append({
            "commodity_pair": pair.replace("-", " \u2194 ").title(),
            "pearson_r_pre_2022": round(pre, 3) if pre else None,
            "pearson_r_post_2022": round(post, 3) if post else None,
            "delta": round(delta, 3) if delta else None,
        })

    return pd.DataFrame(rows)
