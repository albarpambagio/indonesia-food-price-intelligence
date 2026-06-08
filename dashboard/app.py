# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "plotly",
#     "numpy",
# ]
# ///

import marimo

__generated_with = "0.23.7"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    from pathlib import Path

    import marimo as mo
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    return go, json, mo, np, pd, px, Path


@app.cell
def _(mo, pd):
    from data_static import load_csv, load_json, load_json_envelope

    price_trends_df = pd.DataFrame(load_json("price_trends.json"))
    price_trends_df["month"] = pd.to_datetime(price_trends_df["month"])

    price_national_df = pd.DataFrame(load_json("price_trends_national.json"))
    price_national_df["month"] = pd.to_datetime(price_national_df["month"])

    forecast_raw = load_json_envelope("forecast.json")
    forecast_df = pd.DataFrame(forecast_raw)
    forecast_df["date"] = pd.to_datetime(forecast_df["date"])

    seasonal_patterns_df = pd.DataFrame(load_json("seasonal_patterns.json"))
    geographic_disparity_df = pd.DataFrame(load_json("geographic_disparity.json"))
    commodity_correlation_df = pd.DataFrame(load_json("commodity_correlation.json"))
    correlation_summary_df = pd.DataFrame(load_json("correlation_summary.json"))
    islamic_calendar_df = load_csv("islamic_calendar.csv")

    return (
        commodity_correlation_df,
        correlation_summary_df,
        forecast_df,
        geographic_disparity_df,
        islamic_calendar_df,
        price_national_df,
        price_trends_df,
        seasonal_patterns_df,
    )


@app.cell
def _(mo):
    commodity_dd = mo.ui.dropdown(
        options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
        value="All",
        label="Commodity",
    )
    island_dd = mo.ui.dropdown(
        options=[
            "All",
            "Java",
            "Sumatera",
            "Kalimantan",
            "Sulawesi",
            "Eastern Indonesia",
        ],
        value="All",
        label="Island Group",
    )
    year_slider = mo.ui.range_slider(
        start=2007,
        stop=2024,
        value=[2007, 2024],
        step=1,
        label="Year Range",
    )
    return commodity_dd, island_dd, year_slider


@app.cell
def _(commodity_dd, forecast_df, pd, price_national_df, year_slider):
    _yr_lo, _yr_hi = year_slider.value
    filtered_df = price_national_df[
        (price_national_df["month"].dt.year >= _yr_lo)
        & (price_national_df["month"].dt.year <= _yr_hi)
    ].copy()

    if commodity_dd.value != "All":
        filtered_df = filtered_df[
            filtered_df["commodity_consolidated"] == commodity_dd.value
        ]

    latest_prices_df = (
        price_national_df.sort_values("month")
        .groupby("commodity_consolidated")
        .last()
        .reset_index()[["commodity_consolidated", "month", "avg_price_idr"]]
        .copy()
    )
    latest_prices_df.columns = ["commodity_consolidated", "month", "latest_price"]
    latest_prices_df["prev_month"] = (
        latest_prices_df["month"] - pd.DateOffset(years=1)
    )
    prev_prices = price_national_df[["commodity_consolidated", "month", "avg_price_idr"]].copy()
    prev_prices.columns = ["commodity_consolidated", "prev_month", "prev_price"]
    latest_prices_df = latest_prices_df.merge(
        prev_prices, on=["commodity_consolidated", "prev_month"], how="left"
    )
    latest_prices_df["yoy_pct"] = (
        (latest_prices_df["latest_price"] - latest_prices_df["prev_price"])
        / latest_prices_df["prev_price"]
        * 100
    )

    annual_df = price_national_df.copy()
    annual_df["year"] = annual_df["month"].dt.year
    annual_avg = (
        annual_df.groupby(["year", "commodity_consolidated"])["avg_price_idr"]
        .mean()
        .reset_index()
    )
    annual_avg = annual_avg.sort_values(["commodity_consolidated", "year"])
    annual_avg["yoy_pct"] = (
        annual_avg.groupby("commodity_consolidated")["avg_price_idr"].pct_change()
        * 100
    )
    yoy_df = annual_avg.pivot(
        index="year", columns="commodity_consolidated", values="yoy_pct"
    ).reset_index()
    yoy_df.columns.name = None

    def _fmt(v):
        if pd.isna(v):
            return "—"
        sign = "🔴" if v > 0 else "🟢"
        return f"{sign} {v:+.1f}%"

    for col in ["Rice", "Cooking Oil", "Sugar", "Flour"]:
        if col in yoy_df.columns:
            yoy_df[col] = yoy_df[col].apply(_fmt)

    latest_actual = (
        forecast_df[forecast_df["actual_price"].notna()]
        .sort_values("date")
        .groupby("commodity")
        .last()
        .reset_index()
    )
    forecast_only = forecast_df[
        (forecast_df["forecast_price"].notna()) & (forecast_df["scenario"].isna())
    ].copy()
    forecast_avg = (
        forecast_only.groupby("commodity")["forecast_price"].mean().reset_index()
    )
    buy_signals_df = latest_actual.merge(
        forecast_avg, on="commodity", suffixes=("", "_avg")
    )
    buy_signals_df["ratio"] = (
        buy_signals_df["forecast_price"] / buy_signals_df["actual_price"]
    )
    buy_signals_df["signal"] = buy_signals_df["ratio"].apply(
        lambda r: "BUY NOW" if r < 0.98 else ("WATCH" if r > 1.02 else "HOLD")
    )
    buy_signals_df["color"] = buy_signals_df["signal"].map(
        {"BUY NOW": "green", "HOLD": "gray", "WATCH": "orange"}
    )
    fc_ranges = forecast_only.groupby("commodity").agg(
        fc_start=("date", "min"), fc_end=("date", "max")
    ).reset_index()
    buy_signals_df = buy_signals_df.merge(fc_ranges, on="commodity", how="left")
    buy_signals_df["reason"] = buy_signals_df.apply(
        lambda r: (
            f"Forecast avg ({r['forecast_price']:,.0f}) "
            f"vs current ({r['actual_price']:,.0f}) · "
            f"covers {r['fc_start'].strftime('%b %Y')}–{r['fc_end'].strftime('%b %Y')}"
        ),
        axis=1,
    )

    max_month = price_national_df["month"].max()
    sparkline_df = price_national_df[
        price_national_df["month"] >= max_month - pd.DateOffset(months=24)
    ].copy()

    return (
        buy_signals_df,
        filtered_df,
        latest_prices_df,
        sparkline_df,
        yoy_df,
    )


@app.cell
def _(latest_prices_df, mo, pd, sparkline_df):
    from charts.kpi_sparklines import sparkline_chart

    cards = []
    for _, row in latest_prices_df.iterrows():
        comm = row["commodity_consolidated"]
        price = row["latest_price"]
        yoy = row["yoy_pct"]
        if pd.isna(yoy):
            caption = "No YoY data"
        else:
            arrow = "↑" if yoy > 0 else "↓"
            color = "#d32f2f" if yoy > 0 else "#2e7d32"
            caption = f"<span style='color:{color}'>{arrow} {yoy:+.1f}% YoY</span>"

        comm_data = sparkline_df[
            sparkline_df["commodity_consolidated"] == comm
        ]
        spark_fig = sparkline_chart(comm_data["avg_price_idr"])
        spark_widget = mo.ui.plotly(spark_fig)

        card = mo.stat(
            value=f"Rp {price:,.0f}",
            label=comm,
            caption=caption,
            bordered=True,
            slot=spark_widget,
        )
        cards.append(card)

    kpi_cards_output = mo.hstack(cards, gap="0.5rem")
    return kpi_cards_output,


@app.cell
def _(mo):
    chart_commodity_radio = mo.ui.radio(
        options=["Rice", "Cooking Oil", "Sugar", "Flour", "All"],
        value="All",
        label="Show commodity",
    )
    return chart_commodity_radio,


@app.cell
def _(chart_commodity_radio, filtered_df, forecast_df, go, mo, pd):
    fig = go.Figure()
    commodities = (
        ["Rice", "Cooking Oil", "Sugar", "Flour"]
        if chart_commodity_radio.value == "All"
        else [chart_commodity_radio.value]
    )

    forecast_primary = forecast_df[
        (forecast_df["forecast_price"].notna()) & (forecast_df["scenario"].isna())
    ]

    for c in commodities:
        sub = filtered_df[filtered_df["commodity_consolidated"] == c]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["month"],
                y=sub["avg_price_idr"],
                mode="lines",
                name=c,
                hovertemplate=(
                    "%{x|%b %Y}<br>Price: Rp %{y:,.0f}<extra>" + c + "</extra>"
                ),
            )
        )

        fc = forecast_primary[forecast_primary["commodity"] == c]
        if not fc.empty:
            fig.add_trace(
                go.Scatter(
                    x=fc["date"],
                    y=fc["forecast_price"],
                    mode="lines",
                    name=f"{c} (forecast)",
                    line=dict(dash="dash"),
                    hovertemplate=(
                        "%{x|%b %Y}<br>Forecast: Rp %{y:,.0f}<extra></extra>"
                    ),
                )
            )
            ci_x = pd.concat([fc["date"], fc["date"][::-1]])
            ci_y = pd.concat([fc["upper_95"], fc["lower_95"][::-1]])
            fig.add_trace(
                go.Scatter(
                    x=ci_x,
                    y=ci_y,
                    fill="toself",
                    fillcolor="rgba(100,100,200,0.15)",
                    line=dict(color="rgba(0,0,0,0)"),
                    name="95% CI",
                    showlegend=(c == commodities[0]),
                )
            )

    if not forecast_primary.empty:
        first_fc = forecast_primary.groupby("commodity")["date"].min()
        vis = [c for c in commodities if c in first_fc.index]
        if vis:
            sep_date = first_fc[vis].min()
            fig.add_shape(
                type="line",
                x0=sep_date,
                x1=sep_date,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(dash="dash", color="gray", width=1.5),
            )
            fig.add_annotation(
                x=sep_date,
                y=1,
                yref="paper",
                text="Forecast →",
                showarrow=False,
                font=dict(size=11, color="gray"),
                yshift=5,
            )

    if fig.data:
        fig.add_annotation(
            x=pd.Timestamp("2022-04-01"),
            y=fig.data[0].y.max() * 0.9,
            text="2022 Export Ban",
            showarrow=True,
            arrowhead=2,
            font=dict(size=11),
        )
    fig.update_layout(
        height=360,
        yaxis_title="IDR per KG / L",
        yaxis_tickformat=",d",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=60, r=20, t=40, b=80),
    )
    trend_chart_output = mo.ui.plotly(fig)
    return trend_chart_output,


@app.cell
def _(buy_signals_df, mo):
    rows = []
    for _, r in buy_signals_df.iterrows():
        rows.append(
            mo.md(
                f"**{r['commodity']}** &nbsp; "
                f"<span style='color:{r['color']}'>● {r['signal']}</span>  \n"
                f"_{r['reason']}_"
            )
        )

    buy_signal_output = mo.vstack(
        [mo.md("## Buy Signal Monitor"), *rows], gap="0.5rem"
    )
    return buy_signal_output,


@app.cell
def _(mo, year_slider, yoy_df):
    _yr_lo, _yr_hi = year_slider.value
    table_data = yoy_df[
        (yoy_df["year"] >= _yr_lo) & (yoy_df["year"] <= _yr_hi)
    ].sort_values("year", ascending=False)

    yoy_table_output = mo.vstack(
        [
            mo.md("## Annual Price Change"),
            mo.ui.table(
                table_data[
                    ["year", "Rice", "Cooking Oil", "Sugar", "Flour"]
                ],
                page_size=10,
            ),
        ],
        gap="0.5rem",
    )
    return yoy_table_output,


@app.cell
def _(mo):
    footnote_output = mo.callout(
        mo.md(
            "**Forecast limitations:** This model describes historical price patterns. "
            "It cannot anticipate government price controls, import tariff changes, or "
            "weather events. Confidence intervals widen significantly beyond 3 months. "
            "1–2 month forecasts are more reliable than 5–6 month projections."
        ),
        kind="info",
    )
    return footnote_output,


@app.cell
def _(
    buy_signal_output,
    chart_commodity_radio,
    commodity_dd,
    footnote_output,
    island_dd,
    kpi_cards_output,
    mo,
    trend_chart_output,
    year_slider,
    yoy_table_output,
):
    island_note = mo.callout(
        mo.md(
            "**Note:** Island Group filter has no effect on this page. "
            "Price trends and forecasts are at the national level for all commodities."
        ),
        kind="info",
    )

    page1_content = mo.vstack(
        [
            mo.md("# Price Trends & Forecast"),
            mo.md(
                "_Indonesian Staple Commodities · "
                "Jan 2007 – May 2024 + 6-Month Forecast_"
            ),
            mo.hstack(
                [commodity_dd, island_dd, year_slider, island_note],
                gap="1rem",
            ),
            kpi_cards_output,
            chart_commodity_radio,
            trend_chart_output,
            mo.hstack(
                [buy_signal_output, yoy_table_output],
                gap="2rem",
            ),
            footnote_output,
        ],
        gap="1.5rem",
    )
    return page1_content,


@app.cell
def _(mo):
    page2_content = mo.vstack(
        [
            mo.md("## Seasonal Patterns"),
            mo.md("_Coming soon — Page 2_"),
        ],
        gap="1rem",
    )
    return page2_content,


@app.cell
def _(mo):
    page3_content = mo.vstack(
        [
            mo.md("## Geographic Disparity"),
            mo.md("_Coming soon — Page 3_"),
        ],
        gap="1rem",
    )
    return page3_content,


@app.cell
def _(mo):
    page4_content = mo.vstack(
        [
            mo.md("## Commodity Signals"),
            mo.md("_Coming soon — Page 4_"),
        ],
        gap="1rem",
    )
    return page4_content,


@app.cell
def _(mo, page1_content, page2_content, page3_content, page4_content):
    mo.ui.tabs(
        {
            "Price Trends": page1_content,
            "Seasonal": page2_content,
            "Geographic": page3_content,
            "Commodity Signals": page4_content,
        }
    )


if __name__ == "__main__":
    app.run()
