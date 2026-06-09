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
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    from explainer_copy import EXPLAINERS, EXPLAINERS_P2

    COMMODITIES = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    UNIT_MAP = {"Rice": "/kg", "Cooking Oil": "/L", "Sugar": "/kg", "Flour": "/kg"}

    return COMMODITIES, EXPLAINERS, EXPLAINERS_P2, go, mo, np, pd, UNIT_MAP


@app.cell
def _(pd):
    from data_static import load_csv, load_json, load_json_envelope

    price_national_df = pd.DataFrame(load_json("price_trends_national.json"))
    price_national_df["month"] = pd.to_datetime(price_national_df["month"])

    forecast_raw = load_json_envelope("forecast.json")
    forecast_df = pd.DataFrame(forecast_raw)
    forecast_df["date"] = pd.to_datetime(forecast_df["date"])

    islamic_cal_df = load_csv("islamic_calendar.csv")
    islamic_cal_df["eid_date"] = pd.to_datetime(islamic_cal_df["eid_date"])

    return forecast_df, islamic_cal_df, price_national_df


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
    forecast_only = forecast_df[(forecast_df["forecast_price"].notna()) & _is_baseline].copy()

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


# ---------------------------------------------------------------------------
# Page 2: Seasonal Patterns — computation helpers
# ---------------------------------------------------------------------------


@app.cell
def _(islamic_cal_df, np, pd, price_national_df):
    def _compute_seasonal_data(df, cal):
        """Derive heatmap, Ramadan overlay, action windows, summary from price data."""
        df = df.copy()
        df["year"] = df["month"].dt.year
        df["month_of_year"] = df["month"].dt.month

        annual_avg = (
            df.groupby(["year", "commodity_consolidated"])["avg_price_idr"]
            .mean()
            .reset_index()
            .rename(columns={"avg_price_idr": "ann_avg"})
        )
        df = df.merge(annual_avg, on=["year", "commodity_consolidated"], how="left")
        df["price_index"] = (df["avg_price_idr"] / df["ann_avg"]) * 100

        # Heatmap: mean premium % vs annual avg by commodity × month
        monthly_avg = (
            df.groupby(["commodity_consolidated", "month_of_year"])["avg_price_idr"]
            .mean()
            .reset_index()
        )
        overall_avg = (
            df.groupby("commodity_consolidated")["avg_price_idr"]
            .mean()
            .reset_index()
            .rename(columns={"avg_price_idr": "overall_avg"})
        )
        monthly_avg = monthly_avg.merge(overall_avg, on="commodity_consolidated", how="left")
        monthly_avg["premium_pct"] = (
            (monthly_avg["avg_price_idr"] / monthly_avg["overall_avg"]) - 1
        ) * 100
        heatmap_df = monthly_avg[["commodity_consolidated", "month_of_year", "premium_pct"]]

        # Ramadan overlay: month_relative T-2 to T+1
        cal = cal[["year", "eid_date"]].copy()
        cal["eid_month_num"] = cal["eid_date"].dt.month
        cal["eid_year"] = cal["eid_date"].dt.year
        ramadan_rows = []
        for _, row in cal.iterrows():
            eid_ym = row["eid_year"] * 12 + row["eid_month_num"]
            for comm in df["commodity_consolidated"].unique():
                for mr in [-2, -1, 0, 1]:
                    target_ym = eid_ym + mr
                    target_year = target_ym // 12
                    target_month = target_ym % 12
                    if target_month == 0:
                        target_month = 12
                        target_year -= 1
                    match = df[
                        (df["commodity_consolidated"] == comm)
                        & (df["year"] == target_year)
                        & (df["month_of_year"] == target_month)
                    ]
                    if not match.empty:
                        ramadan_rows.append(
                            {
                                "commodity": comm,
                                "year": row["year"],
                                "month_relative": mr,
                                "price_index": match["price_index"].mean(),
                            }
                        )
        ramadan_df = pd.DataFrame(ramadan_rows)

        # Action windows
        driver_months = {
            "Ramadan / Lebaran": None,  # computed dynamically
            "Harvest Season": [3, 4, 8, 9],
            "Year-End": [11, 12],
        }
        action_rows = []
        for driver_name, months in driver_months.items():
            for comm in df["commodity_consolidated"].unique():
                comm_df = df[df["commodity_consolidated"] == comm]
                if driver_name == "Ramadan / Lebaran":
                    comm_ram = ramadan_df[ramadan_df["commodity"] == comm]
                    if comm_ram.empty:
                        continue
                    yearly_spikes = []
                    for yr in comm_ram["year"].unique():
                        yr_data = comm_ram[comm_ram["year"] == yr]
                        driver_idx = yr_data[yr_data["month_relative"].isin([0, 1])][
                            "price_index"
                        ].mean()
                        non_driver_idx = yr_data[yr_data["month_relative"].isin([-2, -1])][
                            "price_index"
                        ].mean()
                        if pd.notna(driver_idx) and pd.notna(non_driver_idx) and non_driver_idx > 0:
                            yearly_spikes.append((driver_idx / non_driver_idx - 1) * 100)
                    if not yearly_spikes:
                        continue
                    avg_spike = np.mean(yearly_spikes)
                    above = sum(1 for s in yearly_spikes if s > 0)
                    action_rows.append(
                        {
                            "driver": driver_name,
                            "commodity": comm,
                            "spike_pct": round(avg_spike, 1),
                            "consistency": above,
                            "total_years": len(yearly_spikes),
                            "lead_months": "2 months before Eid",
                        }
                    )
                else:
                    driver_data = comm_df[comm_df["month_of_year"].isin(months)]
                    non_driver_data = comm_df[~comm_df["month_of_year"].isin(months)]
                    if driver_data.empty or non_driver_data.empty:
                        continue
                    driver_avg = driver_data.groupby("year")["price_index"].mean()
                    non_driver_avg = non_driver_data.groupby("year")["price_index"].mean()
                    yearly_spikes = []
                    years_with_data = 0
                    for yr in driver_avg.index:
                        if yr in non_driver_avg.index:
                            d_val = driver_avg[yr]
                            nd_val = non_driver_avg[yr]
                            if pd.notna(d_val) and pd.notna(nd_val) and nd_val > 0:
                                yearly_spikes.append((d_val / nd_val - 1) * 100)
                                years_with_data += 1
                    if not yearly_spikes:
                        continue
                    avg_spike = np.mean(yearly_spikes)
                    above = sum(1 for s in yearly_spikes if s > 0)
                    lead = (
                        "Mar\u2013Apr / Aug\u2013Sep"
                        if driver_name == "Harvest Season"
                        else "Nov\u2013Dec"
                    )
                    action_rows.append(
                        {
                            "driver": driver_name,
                            "commodity": comm,
                            "spike_pct": round(avg_spike, 1),
                            "consistency": above,
                            "total_years": len(yearly_spikes),
                            "lead_months": lead,
                        }
                    )
        action_windows_df = pd.DataFrame(action_rows)

        # Summary table
        summary_df = action_windows_df.copy()
        summary_df["data_scope"] = "national"

        return heatmap_df, ramadan_df, action_windows_df, summary_df

    heatmap_df, ramadan_df, action_windows_df, summary_df = _compute_seasonal_data(
        price_national_df, islamic_cal_df
    )
    return heatmap_df, ramadan_df, action_windows_df, summary_df


# ---------------------------------------------------------------------------
# Page 2: Driver toggle
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    driver_toggle = mo.ui.radio(
        options=["All Drivers", "Ramadan / Lebaran", "Harvest Season", "Year-End"],
        value="All Drivers",
        label="Seasonal Driver",
    )
    return (driver_toggle,)


# ---------------------------------------------------------------------------
# Page 2: Action cards
# ---------------------------------------------------------------------------


@app.cell
def _(action_windows_df, driver_toggle, mo):
    _driver = driver_toggle.value
    if _driver == "All Drivers":
        _relevant = action_windows_df[action_windows_df["spike_pct"].abs() > 3].sort_values(
            "spike_pct", ascending=False
        )
    else:
        _relevant = action_windows_df[
            (action_windows_df["driver"] == _driver) & (action_windows_df["spike_pct"].abs() > 3)
        ].sort_values("spike_pct", ascending=False)

    _cards = []
    for _, _row in _relevant.iterrows():
        _arrow = "\u2191" if _row["spike_pct"] > 0 else "\u2193"
        _sign = "+" if _row["spike_pct"] > 0 else ""
        _cards.append(
            mo.stat(
                value=f"{_arrow} {_sign}{_row['spike_pct']:.1f}%",
                label=_row["commodity"],
                caption=(
                    f"{_arrow} {_row['driver']} \u00b7 "
                    f"Lead: {_row['lead_months']} \u00b7 "
                    f"{_row['consistency']}/{_row['total_years']} yrs consistent"
                ),
                bordered=True,
            )
        )

    _label = "All Drivers" if _driver == "All Drivers" else _driver
    _card_grid = (
        mo.vstack(
            [
                mo.hstack(_row, gap="1rem", widths="equal")
                for _row in [_cards[i : i + 4] for i in range(0, len(_cards), 4)]
            ],
            gap="0.5rem",
        )
        if _cards
        else mo.callout(
            mo.md("No statistically meaningful seasonal effect (>3%) for this driver."),
            kind="warn",
        )
    )
    page2_action_cards = mo.vstack(
        [
            mo.md(f"_Filtered to: **{_label}**_"),
            _card_grid,
        ],
        gap="0.75rem",
    )
    return (page2_action_cards,)


# ---------------------------------------------------------------------------
# Page 2: Data availability notice
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    page2_data_notice = mo.callout(
        mo.md(
            "**Data scope:** Rice, Sugar, and Flour national prices end **March 2020** "
            "(WFP data gap). Cooking Oil extends through December 2024. "
            "Seasonal patterns are computed on each commodity's available window."
        ),
        kind="info",
    )
    return (page2_data_notice,)


# ---------------------------------------------------------------------------
# Page 2: Gregorian heatmap (always visible)
# ---------------------------------------------------------------------------


@app.cell
def _(heatmap_df, mo, go):
    _pivot = heatmap_df.pivot(
        index="commodity_consolidated", columns="month_of_year", values="premium_pct"
    )
    _month_labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    _fig = go.Figure(
        go.Heatmap(
            z=_pivot.values,
            x=_month_labels,
            y=_pivot.index.tolist(),
            colorscale="RdBu_r",
            zmid=0,
            text=[[f"{v:+.1f}%" for v in row] for row in _pivot.values],
            texttemplate="%{text}",
            hovertemplate="<b>%{y}</b><br>%{x}<br>Premium: %{z:+.1f}%<extra></extra>",
            colorbar=dict(title="Premium vs Annual Avg (%)"),
        )
    )
    _fig.update_layout(
        height=280,
        margin=dict(l=100, r=20, t=10, b=40),
        template="plotly_white",
        font=dict(family="system-ui, sans-serif", size=12),
        hoverlabel=dict(font_size=13),
    )
    page2_heatmap = mo.ui.plotly(_fig)
    return (page2_heatmap,)


# ---------------------------------------------------------------------------
# Page 2: Driver-specific charts (show all 3 when "All Drivers")
# ---------------------------------------------------------------------------


@app.cell
def _(COMMODITIES, commodity_dd, driver_toggle, go, mo, np, pd, price_national_df, ramadan_df):
    _driver = driver_toggle.value
    _selected_comm = commodity_dd.value

    def _build_ramadan_chart():
        _comms = COMMODITIES if _selected_comm == "All" else [_selected_comm]
        _fig = go.Figure()
        for _c in _comms:
            _sub = ramadan_df[ramadan_df["commodity"] == _c]
            if _sub.empty:
                continue
            for _yr in _sub["year"].unique():
                _yd = _sub[_sub["year"] == _yr].sort_values("month_relative")
                _is_2022 = bool(_yr == 2022)
                _fig.add_trace(
                    go.Scatter(
                        x=_yd["month_relative"],
                        y=_yd["price_index"],
                        mode="lines",
                        name=str(_yr),
                        line=dict(
                            width=2.5 if _is_2022 else 0.8,
                            color="red" if _is_2022 else "rgba(100,100,180,0.4)",
                        ),
                        showlegend=_is_2022,
                        legendgroup=_c,
                        hovertemplate=(
                            f"{_yr} ({_c})<br>Month relative to Eid: %{{x}}"
                            f"<br>Price Index: %{{y:.1f}}<extra></extra>"
                        ),
                    )
                )
            _avg = _sub.groupby("month_relative")["price_index"].mean().reset_index()
            _fig.add_trace(
                go.Scatter(
                    x=_avg["month_relative"],
                    y=_avg["price_index"],
                    mode="lines",
                    name=f"{_c} avg",
                    line=dict(width=2.5, color="darkblue"),
                    legendgroup=_c,
                )
            )
        _fig.add_hline(y=100, line_dash="dot", line_color="gray", annotation_text="Annual avg")
        _fig.update_layout(
            height=320,
            margin=dict(b=100),
            xaxis=dict(
                title="Months relative to Eid al-Fitr",
                tickvals=[-2, -1, 0, 1],
                ticktext=["T\u22122", "T\u22121", "T (Eid)", "T+1"],
            ),
            yaxis_title="Price Index (100 = annual avg)",
            template="plotly_white",
            font=dict(family="system-ui, sans-serif", size=12),
            hoverlabel=dict(font_size=13),
            legend=dict(orientation="h", y=-0.25),
        )
        return _fig

    def _build_harvest_chart():
        _monthly = price_national_df[price_national_df["commodity_consolidated"] == "Rice"].copy()
        _monthly["month_of_year"] = _monthly["month"].dt.month
        _monthly["year"] = _monthly["month"].dt.year
        _month_avg = _monthly.groupby("month_of_year")["avg_price_idr"].mean()
        _annual = _monthly.groupby("year")["avg_price_idr"].mean()
        _monthly = _monthly.merge(
            _annual.reset_index().rename(columns={"avg_price_idr": "yr_avg"}),
            on="year",
            how="left",
        )
        _monthly["price_index"] = (_monthly["avg_price_idr"] / _monthly["yr_avg"]) * 100
        _mi = _monthly.groupby("month_of_year")["price_index"].mean()
        _month_labels = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        _harvest_months = {3, 4, 8, 9}
        _colors = [
            "rgba(34,139,34,0.6)" if m in _harvest_months else "rgba(70,130,180,0.7)"
            for m in range(1, 13)
        ]
        _fig = go.Figure(
            go.Bar(
                x=_month_labels,
                y=[_mi.get(m, 0) for m in range(1, 13)],
                marker_color=_colors,
                hovertemplate="%{x}<br>Rice index: %{y:.1f}<extra></extra>",
            )
        )
        _fig.add_hline(y=100, line_dash="dot", line_color="gray", annotation_text="Annual avg")
        _fig.update_layout(
            height=280,
            yaxis_title="Price Index (100 = ann. avg)",
            template="plotly_white",
            font=dict(family="system-ui, sans-serif", size=12),
            hoverlabel=dict(font_size=13),
        )
        return _fig

    def _build_yearend_chart():
        _monthly = price_national_df.copy()
        _monthly["month_of_year"] = _monthly["month"].dt.month
        _monthly["year"] = _monthly["month"].dt.year
        _annual = (
            _monthly.groupby(["year", "commodity_consolidated"])["avg_price_idr"]
            .mean()
            .reset_index()
            .rename(columns={"avg_price_idr": "ann_avg"})
        )
        _monthly = _monthly.merge(_annual, on=["year", "commodity_consolidated"], how="left")
        _monthly["price_index"] = (_monthly["avg_price_idr"] / _monthly["ann_avg"]) * 100
        _nov_dec = _monthly[_monthly["month_of_year"].isin([11, 12])]
        _rest = _monthly[~_monthly["month_of_year"].isin([11, 12])]
        _nd_avg = (
            _nov_dec.groupby("commodity_consolidated")["price_index"]
            .mean()
            .reset_index()
            .rename(columns={"price_index": "nd_avg"})
        )
        _rest_avg = (
            _rest.groupby("commodity_consolidated")["price_index"]
            .mean()
            .reset_index()
            .rename(columns={"price_index": "rest_avg"})
        )
        _ye = _nd_avg.merge(_rest_avg, on="commodity_consolidated", how="inner")
        _ye["premium_pct"] = _ye["nd_avg"] - _ye["rest_avg"]
        _ye = _ye.sort_values("premium_pct", ascending=False)
        _fig = go.Figure(
            go.Bar(
                x=_ye["commodity_consolidated"],
                y=_ye["premium_pct"],
                marker_color="rgba(70,130,180,0.8)",
                hovertemplate="<b>%{x}</b><br>Nov\u2013Dec premium: %{y:+.1f}%<extra></extra>",
            )
        )
        _fig.update_layout(
            height=280,
            yaxis_title="Index points above/below annual avg",
            template="plotly_white",
            font=dict(family="system-ui, sans-serif", size=12),
            hoverlabel=dict(font_size=13),
        )
        return _fig

    if _driver == "All Drivers":
        _charts = mo.vstack(
            [
                mo.md("### Ramadan / Lebaran"),
                mo.ui.plotly(_build_ramadan_chart()),
                mo.md("### Harvest Season"),
                mo.ui.plotly(_build_harvest_chart()),
                mo.md("### Year-End"),
                mo.ui.plotly(_build_yearend_chart()),
            ],
            gap="1.5rem",
        )
    elif _driver == "Ramadan / Lebaran":
        _charts = mo.ui.plotly(_build_ramadan_chart())
    elif _driver == "Harvest Season":
        _charts = mo.ui.plotly(_build_harvest_chart())
    else:
        _charts = mo.ui.plotly(_build_yearend_chart())

    page2_driver_chart = _charts
    return (page2_driver_chart,)


# ---------------------------------------------------------------------------
# Page 2: Summary table
# ---------------------------------------------------------------------------


@app.cell
def _(mo, summary_df):
    _table_data = summary_df[
        ["driver", "commodity", "spike_pct", "consistency", "total_years", "lead_months"]
    ].copy()
    _table_data = _table_data.sort_values("spike_pct", key=abs, ascending=False)
    _table_data.columns = [
        "Driver",
        "Commodity",
        "Spike %",
        "Consistent (yrs)",
        "Total yrs",
        "Lead Time",
    ]

    page2_summary_table = mo.vstack(
        [
            mo.ui.table(_table_data, page_size=10),
            mo.callout(
                mo.md(
                    "_**Spike %** = avg premium (or discount) during seasonal window "
                    "vs rest of year. **Lead Time** = how far in advance to act._"
                ),
                kind="neutral",
            ),
        ],
        gap="1rem",
    )
    return (page2_summary_table,)


# ---------------------------------------------------------------------------
# Page 2: Explainer accordion
# ---------------------------------------------------------------------------


@app.cell
def _(EXPLAINERS_P2, mo):
    page2_explainer = mo.accordion(
        {
            "Action Cards \u2014 how to read": EXPLAINERS_P2["action_cards"],
            "Heatmap \u2014 how to read": EXPLAINERS_P2["heatmap"],
            "Ramadan Overlay \u2014 how to read": EXPLAINERS_P2["ramadan"],
            "Harvest Chart \u2014 how to read": EXPLAINERS_P2["harvest"],
            "Year-End Chart \u2014 how to read": EXPLAINERS_P2["yearend"],
            "Summary Table \u2014 how to read": EXPLAINERS_P2["summary"],
        },
        multiple=True,
    )
    return (page2_explainer,)


# ---------------------------------------------------------------------------
# Page 2: Assembly
# ---------------------------------------------------------------------------


@app.cell
def _(
    commodity_dd,
    driver_toggle,
    mo,
    page2_action_cards,
    page2_data_notice,
    page2_driver_chart,
    page2_explainer,
    page2_heatmap,
    page2_summary_table,
):
    _header = mo.vstack(
        [
            mo.md("# Seasonal Patterns"),
            mo.md("**Price premiums by season** \u00b7 2007\u20132024 historical average"),
        ],
        gap="0.25rem",
    )

    _controls = mo.hstack(
        [
            mo.vstack([mo.md("_Filter by commodity:_"), commodity_dd], gap="0.25rem"),
            mo.vstack([mo.md("_Show driver:_"), driver_toggle], gap="0.25rem"),
        ],
        gap="2rem",
    )

    _heatmap_section = mo.vstack(
        [
            mo.md("## Monthly Price Heatmap"),
            page2_heatmap,
            mo.callout(
                mo.md(
                    "**Calendar note:** Ramadan months shift each year. The heatmap uses "
                    "Gregorian months \u2014 the Ramadan overlay below adjusts for the "
                    "Islamic calendar."
                ),
                kind="info",
            ),
            page2_data_notice,
        ],
        gap="0.75rem",
    )

    _drivers_section = mo.vstack(
        [
            mo.md("## Seasonal Driver Analysis"),
            page2_driver_chart,
        ],
        gap="0.75rem",
    )

    _cards_section = mo.vstack(
        [
            mo.md("## Action Windows"),
            page2_action_cards,
        ],
        gap="0.75rem",
    )

    _summary_section = mo.vstack(
        [
            mo.md("## Reference Table"),
            page2_summary_table,
        ],
        gap="0.75rem",
    )

    page2_content = mo.vstack(
        [
            _header,
            _controls,
            _heatmap_section,
            _drivers_section,
            _cards_section,
            _summary_section,
            page2_explainer,
        ],
        gap="2.5rem",
    )
    return (page2_content,)


# ---------------------------------------------------------------------------
# Final assembly: tabs
# ---------------------------------------------------------------------------


@app.cell
def _(
    buy_signal_output,
    commodity_dd,
    explainer_card,
    kpi_cards_output,
    max_month,
    mo,
    page2_content,
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

    mo.ui.tabs(
        {
            "Price Trends": page1_content,
            "Seasonal Patterns": page2_content,
        }
    )


if __name__ == "__main__":
    app.run()
