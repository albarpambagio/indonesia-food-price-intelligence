# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "plotly",
# ]
# ///

import marimo

__generated_with = "0.23.7"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.graph_objects as go
    from explainer_copy import EXPLAINERS

    COMMODITIES = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    UNIT_MAP = {"Rice": "/kg", "Cooking Oil": "/L", "Sugar": "/kg", "Flour": "/kg"}

    return COMMODITIES, EXPLAINERS, go, mo, pd, UNIT_MAP


@app.cell
def _(pd):
    from data_static import load_json, load_json_envelope

    price_national_df = pd.DataFrame(load_json("price_trends_national.json"))
    price_national_df["month"] = pd.to_datetime(price_national_df["month"])

    forecast_raw = load_json_envelope("forecast.json")
    forecast_df = pd.DataFrame(forecast_raw)
    forecast_df["date"] = pd.to_datetime(forecast_df["date"])

    return forecast_df, price_national_df


@app.cell
def _(price_national_df):
    data_min_year = int(price_national_df["month"].dt.year.min())
    data_max_year = int(price_national_df["month"].dt.year.max())
    return data_min_year, data_max_year


@app.cell
def _(mo, data_min_year, data_max_year):
    commodity_dd = mo.ui.dropdown(
        options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
        value="All",
        label="Commodity",
    )
    year_slider = mo.ui.range_slider(
        start=data_min_year,
        stop=data_max_year,
        value=[max(2019, data_min_year), data_max_year],
        step=1,
        label="Year range",
    )
    show_all_years = mo.ui.checkbox(
        label=f"Show full history ({data_min_year}\u2013{data_max_year})",
    )
    return commodity_dd, show_all_years, year_slider


@app.cell
def _(
    commodity_dd,
    mo,
    price_national_df,
    show_all_years,
    year_slider,
    data_min_year,
    data_max_year,
):
    if show_all_years.value:
        _yr_lo, _yr_hi = data_min_year, data_max_year
    else:
        _yr_lo, _yr_hi = year_slider.value
    filtered_df = price_national_df[
        (price_national_df["month"].dt.year >= _yr_lo)
        & (price_national_df["month"].dt.year <= _yr_hi)
    ].copy()

    if commodity_dd.value != "All":
        filtered_df = filtered_df[filtered_df["commodity_consolidated"] == commodity_dd.value]

    mo.stop(filtered_df.empty, mo.md("_No data available for the selected filters._"))

    max_month = price_national_df["month"].max()
    return filtered_df, max_month


@app.cell
def _(pd, price_national_df):
    latest_prices_df = (
        price_national_df.sort_values("month")
        .groupby("commodity_consolidated")
        .last()
        .reset_index()[["commodity_consolidated", "month", "avg_price_idr"]]
        .copy()
    )
    latest_prices_df.columns = ["commodity_consolidated", "month", "latest_price"]
    latest_prices_df["prev_month"] = latest_prices_df["month"] - pd.DateOffset(years=1)
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
    return (latest_prices_df,)


@app.cell
def _(price_national_df):
    annual_df = price_national_df.copy()
    annual_df["year"] = annual_df["month"].dt.year
    annual_avg = (
        annual_df.groupby(["year", "commodity_consolidated"])["avg_price_idr"].mean().reset_index()
    )
    annual_avg = annual_avg.sort_values(["commodity_consolidated", "year"])
    annual_avg["yoy_pct"] = (
        annual_avg.groupby("commodity_consolidated")["avg_price_idr"].pct_change() * 100
    )
    yoy_df = annual_avg.pivot(
        index="year", columns="commodity_consolidated", values="yoy_pct"
    ).reset_index()
    yoy_df.columns.name = None
    return (yoy_df,)


@app.cell
def _(forecast_df, price_national_df):
    _is_baseline = forecast_df["scenario"].isna()

    latest_actual = (
        forecast_df[(forecast_df["actual_price"].notna()) & _is_baseline]
        .sort_values("date")
        .groupby("commodity")
        .last()
        .reset_index()
    )
    forecast_only = forecast_df[
        (forecast_df["forecast_price"].notna()) & _is_baseline
    ].copy()

    forecast_avg = (
        forecast_only.sort_values(["commodity", "date"])
        .groupby("commodity")
        .head(2)
        .groupby("commodity")["forecast_price"]
        .mean()
        .reset_index()
    )

    buy_signals_df = latest_actual.merge(forecast_avg, on="commodity", suffixes=("", "_avg"))
    buy_signals_df["ratio"] = buy_signals_df["forecast_price"] / buy_signals_df["actual_price"]
    buy_signals_df["signal"] = buy_signals_df["ratio"].apply(
        lambda r: "BUY NOW" if r < 0.98 else ("WATCH" if r > 1.02 else "HOLD")
    )
    buy_signals_df["color"] = buy_signals_df["signal"].map(
        {"BUY NOW": "#2e7d32", "HOLD": "#757575", "WATCH": "#ed6c02"}
    )
    buy_signals_df["icon"] = buy_signals_df["signal"].map(
        {"BUY NOW": "\u2705", "HOLD": "\u23f8\ufe0f", "WATCH": "\U0001f7e1"}
    )
    fc_ranges = (
        forecast_only.groupby("commodity")
        .agg(fc_start=("date", "min"), fc_end=("date", "max"))
        .reset_index()
    )
    buy_signals_df = buy_signals_df.merge(fc_ranges, on="commodity", how="left")
    buy_signals_df["reason"] = buy_signals_df.apply(
        lambda r: (
            f"2-mo avg ({r['forecast_price']:,.0f}) "
            f"vs current ({r['actual_price']:,.0f}) \u00b7 "
            f"covers {r['fc_start'].strftime('%b %Y')}\u2013{r['fc_end'].strftime('%b %Y')}"
        ),
        axis=1,
    )

    return (buy_signals_df,)


@app.cell
def _(COMMODITIES, UNIT_MAP, latest_prices_df, mo, pd, price_national_df):
    from charts.kpi_sparklines import sparkline_chart

    cards = []
    for _, row in latest_prices_df.iterrows():
        comm = row["commodity_consolidated"]
        price = row["latest_price"]
        yoy = row["yoy_pct"]
        unit = UNIT_MAP.get(comm, "")
        if pd.isna(yoy):
            caption = "No YoY data"
            direction = None
        else:
            sign = "+" if yoy > 0 else ""
            caption = f"{sign}{yoy:.1f}% vs. same month last year"
            direction = "increase" if yoy > 0 else "decrease"

        comm_all = price_national_df[price_national_df["commodity_consolidated"] == comm]
        comm_max = comm_all["month"].max()
        comm_data = comm_all[comm_all["month"] >= comm_max - pd.DateOffset(months=24)]
        spark_fig = sparkline_chart(comm_data["avg_price_idr"])
        spark_widget = mo.ui.plotly(spark_fig)

        stat_kwargs = dict(
            value=f"Rp {price:,.0f} {unit}",
            label=comm,
            caption=caption,
            bordered=True,
            slot=spark_widget,
        )
        if direction is not None:
            stat_kwargs["direction"] = direction
            stat_kwargs["target_direction"] = "decrease"
        card = mo.stat(**stat_kwargs)
        cards.append(card)

    row1 = mo.hstack(cards[:2], gap="1rem", widths="equal")
    row2 = mo.hstack(cards[2:], gap="1rem", widths="equal")
    kpi_cards_output = mo.vstack([row1, row2], gap="1rem")
    return (kpi_cards_output,)


@app.cell
def _(COMMODITIES, commodity_dd, filtered_df, forecast_df, go, mo, pd):
    fig = go.Figure()
    if commodity_dd.value == "All":
        commodities = COMMODITIES
    else:
        commodities = [commodity_dd.value]

    forecast_primary = forecast_df[
        (forecast_df["forecast_price"].notna()) & (forecast_df["scenario"].isna())
    ]

    for _i, c in enumerate(commodities):
        sub = filtered_df[filtered_df["commodity_consolidated"] == c]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["month"],
                y=sub["avg_price_idr"],
                mode="lines",
                name=c,
                hovertemplate=("%{x|%b %Y}<br>Price: Rp %{y:,.0f}<extra>" + c + "</extra>"),
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
                    hovertemplate=("%{x|%b %Y}<br>Forecast: Rp %{y:,.0f}<extra></extra>"),
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
                    showlegend=(_i == 0),
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
                text="Forecast \u2192",
                showarrow=False,
                font=dict(size=11, color="gray"),
                yshift=5,
            )

    if fig.data:
        fig.add_annotation(
            x=pd.Timestamp("2022-04-01"),
            y=0.9,
            yref="paper",
            text="2022 Export Ban",
            showarrow=True,
            arrowhead=2,
            font=dict(size=11),
            ayref="y",
            ay=-30,
        )
    fig.update_layout(
        height=560,
        yaxis_title="IDR per kg / L",
        yaxis_tickformat=",d",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=60, r=20, t=40, b=80),
    )
    trend_chart_output = mo.ui.plotly(fig)
    return (trend_chart_output,)


@app.cell
def _(buy_signals_df, max_month, mo):
    _month_str = max_month.strftime("%B %Y")

    rows = []
    for _, r in buy_signals_df.iterrows():
        rows.append(
            mo.md(
                f"**{r['commodity']}** &nbsp; "
                f"<span style='color:{r['color']}'>{r['icon']} {r['signal']}</span>  \n"
                f"_{r['reason']}_"
            )
        )

    buy_signal_output = mo.vstack(
        [
            mo.md("## Buy Signal Monitor"),
            mo.md(f"_As of {_month_str}_"),
            *rows,
        ],
        gap="0.5rem",
    )
    return (buy_signal_output,)


@app.cell
def _(COMMODITIES, mo, show_all_years, year_slider, yoy_df, data_min_year, data_max_year):
    if show_all_years.value:
        _yr_lo, _yr_hi = data_min_year, data_max_year
    else:
        _yr_lo, _yr_hi = year_slider.value
    table_data = yoy_df[(yoy_df["year"] >= _yr_lo) & (yoy_df["year"] <= _yr_hi)].sort_values(
        "year", ascending=False
    )

    yoy_table_output = mo.vstack(
        [
            mo.md("## Annual Price Change"),
            mo.ui.table(
                table_data[["year", *COMMODITIES]],
                page_size=10,
            ),
        ],
        gap="0.5rem",
    )
    return (yoy_table_output,)


@app.cell
def _(EXPLAINERS, mo):
    explainer_card = mo.accordion(
        {
            "KPI Cards \u2014 how to read": EXPLAINERS["kpi_cards"],
            "Trend Chart \u2014 how to read": EXPLAINERS["trend_chart"],
            "Buy Signals \u2014 how they work": EXPLAINERS["buy_signal"],
            "YoY Table \u2014 how to read": EXPLAINERS["yoy_table"],
            "Forecast Reliability": EXPLAINERS["forecast_note"],
        },
        multiple=True,
    )
    return (explainer_card,)


@app.cell
def _(
    buy_signal_output,
    commodity_dd,
    explainer_card,
    kpi_cards_output,
    max_month,
    mo,
    show_all_years,
    trend_chart_output,
    year_slider,
    yoy_table_output,
):
    _date_label = max_month.strftime("%b %Y")

    page1_content = mo.vstack(
        [
            mo.md("# Price Trends & Forecast"),
            mo.md(
                f"_Indonesian Staple Commodities \u00b7 "
                f"Jan 2007\u2013{_date_label} + 6-Month Forecast_"
            ),
            kpi_cards_output,
            buy_signal_output,
            mo.hstack(
                [commodity_dd, year_slider, show_all_years],
                gap="1rem",
            ),
            mo.md("_Checkbox overrides the year slider._"),
            trend_chart_output,
            mo.callout(
                mo.md(
                    "**Forecast note:** This model describes historical price patterns. "
                    "It cannot anticipate government price controls, import tariff changes, or "
                    "weather events. Confidence intervals widen significantly beyond 3 months. "
                    "1\u20132 month forecasts are more reliable than 5\u20136 month projections."
                ),
                kind="info",
            ),
            yoy_table_output,
            explainer_card,
        ],
        gap="1.5rem",
    )
    page1_content  # noqa: B018 \u2014 marimo renders last expression as cell output


if __name__ == "__main__":
    app.run()
