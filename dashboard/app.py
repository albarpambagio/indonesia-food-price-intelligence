# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas",
#     "plotly",
# ]
# ///

import marimo

__generated_with = "0.23.9"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go

    from explainer_loader import load_explainers
    EXPLAINERS, EXPLAINERS_P2, EXPLAINERS_P3, EXPLAINERS_P4 = load_explainers()

    COMMODITIES = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    UNIT_MAP = {"Rice": "/kg", "Cooking Oil": "/L", "Sugar": "/kg", "Flour": "/kg"}
    MONTH_LABELS = [
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
    BUY_SIGNAL_LOWER = 0.98
    BUY_SIGNAL_UPPER = 1.02
    COMMODITY_COLORS = {
        "Rice": "#1f77b4",
        "Cooking Oil": "#ff7f0e",
        "Sugar": "#2ca02c",
        "Flour": "#d62728",
    }

    return (
        BUY_SIGNAL_LOWER,
        BUY_SIGNAL_UPPER,
        COMMODITIES,
        COMMODITY_COLORS,
        MONTH_LABELS,
        EXPLAINERS,
        EXPLAINERS_P2,
        EXPLAINERS_P3,
        EXPLAINERS_P4,
        go,
        mo,
        np,
        pd,
        UNIT_MAP,
    )


@app.cell
def _(mo, pd):
    try:
        from data_static import load_csv, load_json, load_json_envelope
    except ModuleNotFoundError:

        def load_json(filename):
            return []

        def load_json_envelope(filename, key="data"):
            return []

        def load_csv(filename):
            return pd.DataFrame()

    _load_error = None
    try:
        price_national_df = pd.DataFrame(load_json("price_trends_national.json"))
        price_national_df["month"] = pd.to_datetime(price_national_df["month"])

        forecast_raw = load_json_envelope("forecast.json")
        forecast_df = pd.DataFrame(forecast_raw)
        forecast_df["date"] = pd.to_datetime(forecast_df["date"])

        islamic_cal_df = load_csv("islamic_calendar.csv")
        islamic_cal_df["eid_date"] = pd.to_datetime(islamic_cal_df["eid_date"])

        max_month = price_national_df["month"].max()
    except Exception as _exc:
        _load_error = str(_exc)
        price_national_df = pd.DataFrame(
            columns=["month", "commodity_consolidated", "avg_price_idr"]
        )
        price_national_df["month"] = pd.to_datetime(price_national_df["month"])
        forecast_df = pd.DataFrame(
            columns=[
                "date",
                "commodity_consolidated",
                "commodity",
                "forecast_price",
                "lower_95",
                "upper_95",
                "scenario",
                "actual_price",
            ]
        )
        forecast_df["date"] = pd.to_datetime(forecast_df["date"])
        islamic_cal_df = pd.DataFrame(columns=["eid_date", "ramadan_start", "ramadan_end"])
        islamic_cal_df["eid_date"] = pd.to_datetime(islamic_cal_df["eid_date"])
        max_month = pd.Timestamp("2024-01-01")

    data_load_error = (
        mo.callout(
            mo.md(
                f"**Data loading failed:** {_load_error}\n\nEnsure the data files are accessible."
            ),
            kind="danger",
        )
        if _load_error
        else None
    )
    return (
        data_load_error,
        forecast_df,
        islamic_cal_df,
        load_csv,
        load_json,
        load_json_envelope,
        max_month,
        price_national_df,
    )


@app.cell
def _(price_national_df):
    data_min_year = (
        int(price_national_df["month"].dt.year.min()) if not price_national_df.empty else 2007
    )
    data_max_year = (
        int(price_national_df["month"].dt.year.max()) if not price_national_df.empty else 2024
    )
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
def _(data_min_year, data_max_year, show_all_years, year_slider):
    if show_all_years.value:
        yr_lo, yr_hi = data_min_year, data_max_year
    else:
        yr_lo, yr_hi = year_slider.value
    return yr_lo, yr_hi


@app.cell
def _(
    commodity_dd,
    mo,
    price_national_df,
    yr_lo,
    yr_hi,
):
    filtered_df = price_national_df[
        (price_national_df["month"].dt.year >= yr_lo)
        & (price_national_df["month"].dt.year <= yr_hi)
    ].copy()

    if commodity_dd.value != "All":
        filtered_df = filtered_df[filtered_df["commodity_consolidated"] == commodity_dd.value]

    page1_filter_notice = (
        mo.callout(
            mo.md(
                "_No data available for the selected filters. "
                "Try adjusting the year range or commodity._"
            ),
            kind="warn",
        )
        if filtered_df.empty
        else None
    )

    return filtered_df, page1_filter_notice


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
def _(BUY_SIGNAL_LOWER, BUY_SIGNAL_UPPER, forecast_df, price_national_df):
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
    buy_signals_df["ratio"] = buy_signals_df["forecast_price_avg"] / buy_signals_df["actual_price"]
    buy_signals_df["signal"] = buy_signals_df["ratio"].apply(
        lambda r: (
            "BUY NOW" if r < BUY_SIGNAL_LOWER else ("WATCH" if r > BUY_SIGNAL_UPPER else "HOLD")
        )
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
            f"2-mo avg ({r['forecast_price_avg']:,.0f}) "
            f"vs current ({r['actual_price']:,.0f}) \u00b7 "
            f"covers {r['fc_start'].strftime('%b %Y')}\u2013{r['fc_end'].strftime('%b %Y')}"
        ),
        axis=1,
    )

    return (buy_signals_df,)


@app.cell
def _(COMMODITIES, UNIT_MAP, go, latest_prices_df, mo, pd, price_national_df):
    try:
        from charts.kpi_sparklines import sparkline_chart
    except ModuleNotFoundError:

        def sparkline_chart(*a, **kw):
            return go.Figure()

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

    _n = len(cards)
    _per_row = 2
    _rows_kpi = [
        mo.hstack(cards[i : i + _per_row], gap="1rem", widths="equal")
        for i in range(0, _n, _per_row)
    ]
    kpi_cards_output = mo.vstack(_rows_kpi, gap="1rem")
    return (kpi_cards_output,)


@app.cell
def _(COMMODITIES, COMMODITY_COLORS, commodity_dd, filtered_df, forecast_df, go, mo, pd):
    fig = go.Figure()
    commodities = COMMODITIES if commodity_dd.value == "All" else [commodity_dd.value]

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
                hovertemplate=f"%{{x|%b %Y}}<br>Price: Rp %{{y:,.0f}}<extra>{c}</extra>",
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
                    hovertemplate=f"%{{x|%b %Y}}<br>Forecast: Rp %{{y:,.0f}}<extra>{c}</extra>",
                )
            )
            ci_x = pd.concat([fc["date"], fc["date"][::-1]])
            ci_y = pd.concat([fc["upper_95"], fc["lower_95"][::-1]])
            _hex = COMMODITY_COLORS.get(c, "#1f77b4").lstrip("#")
            _ci_fill = f"rgba({int(_hex[0:2], 16)},{int(_hex[2:4], 16)},{int(_hex[4:6], 16)},0.15)"
            fig.add_trace(
                go.Scatter(
                    x=ci_x,
                    y=ci_y,
                    fill="toself",
                    fillcolor=_ci_fill,
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
            ayref="pixel",
            ay=-30,
        )
    fig.update_layout(
        height=560,
        yaxis_title="IDR per kg / L",
        yaxis_tickformat=",d",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.3, yanchor="top"),
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
                f"_{r['reason']}_  \n"
                f"<sub>As of {_month_str}</sub>"
            )
        )

    buy_signal_output = mo.vstack(
        [
            mo.md("## Buy Signal Monitor"),
            *rows,
        ],
        gap="0.5rem",
    )
    return (buy_signal_output,)


@app.cell
def _(COMMODITIES, mo, yoy_df, yr_lo, yr_hi):
    table_data = yoy_df[(yoy_df["year"] >= yr_lo) & (yoy_df["year"] <= yr_hi)].sort_values(
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
    _na = mo.md("_N/A_")
    explainer_card = mo.accordion(
        {
            "KPI Cards \u2014 how to read": EXPLAINERS.get("kpi_cards", _na),
            "Trend Chart \u2014 how to read": EXPLAINERS.get("trend_chart", _na),
            "Buy Signals \u2014 how they work": EXPLAINERS.get("buy_signal", _na),
            "YoY Table \u2014 how to read": EXPLAINERS.get("yoy_table", _na),
            "Forecast Reliability": EXPLAINERS.get("forecast_note", _na),
        },
        multiple=True,
    )
    return (explainer_card,)


# ---------------------------------------------------------------------------
# Page 2: Seasonal Patterns — computation helpers
# ---------------------------------------------------------------------------


@app.cell
def _(islamic_cal_df, pd, price_national_df):
    try:
        from computations.seasonal import compute_seasonal_data
    except ModuleNotFoundError:

        def compute_seasonal_data(*a):
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    heatmap_df, ramadan_df, action_windows_df, summary_df = compute_seasonal_data(
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
def _(action_windows_df, commodity_dd, driver_toggle, mo):
    _driver = driver_toggle.value
    _comm = commodity_dd.value
    _adf = action_windows_df
    if _comm != "All":
        _adf = _adf[_adf["commodity"] == _comm]
    if _driver == "All Drivers":
        _relevant = _adf[_adf["spike_pct"].abs() > 3].sort_values("spike_pct", ascending=False)
    else:
        _relevant = _adf[(_adf["driver"] == _driver) & (_adf["spike_pct"].abs() > 3)].sort_values(
            "spike_pct", ascending=False
        )

    _cards = []
    for _, _row in _relevant.iterrows():
        _arrow = "\u2191" if _row["spike_pct"] > 0 else "\u2193"
        _sign = "+" if _row["spike_pct"] > 0 else ""
        _cards.append(
            mo.stat(
                value=f"{_arrow} {_sign}{_row['spike_pct']:.1f}%",
                label=_row["commodity"],
                caption=(
                    f"{_row['driver']} \u00b7 "
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
def _(MONTH_LABELS, commodity_dd, driver_toggle, heatmap_df, mo, go):
    _driver = driver_toggle.value
    _comm = commodity_dd.value
    _hdf = heatmap_df
    if _comm != "All":
        _hdf = _hdf[_hdf["commodity_consolidated"] == _comm]
    _pivot = _hdf.pivot(
        index="commodity_consolidated", columns="month_of_year", values="premium_pct"
    )

    _highlight_months = {
        "Ramadan / Lebaran": None,
        "Harvest Season": {3, 4, 8, 9},
        "Year-End": {11, 12},
    }.get(_driver)

    _fig = go.Figure(
        go.Heatmap(
            z=_pivot.values,
            x=MONTH_LABELS,
            y=_pivot.index.tolist(),
            colorscale="RdBu_r",
            zmid=0,
            text=[[f"{v:+.1f}%" for v in row] for row in _pivot.values],
            texttemplate="%{text}",
            hovertemplate="<b>%{y}</b><br>%{x}<br>Premium: %{z:+.1f}%<extra></extra>",
            colorbar=dict(title="Premium vs Annual Avg (%)"),
        )
    )
    if _highlight_months is not None:
        for _m in _highlight_months:
            _fig.add_vline(
                x=_m - 1,
                line=dict(color="rgba(0,150,0,0.4)", width=2, dash="dot"),
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
def _(
    COMMODITIES,
    COMMODITY_COLORS,
    MONTH_LABELS,
    commodity_dd,
    driver_toggle,
    go,
    mo,
    np,
    pd,
    price_national_df,
    ramadan_df,
):
    try:
        from computations.seasonal import compute_price_index
    except ModuleNotFoundError:

        def compute_price_index(df):
            return pd.DataFrame(columns=["month_of_year", "price_index"])

    _driver = driver_toggle.value
    _selected_comm = commodity_dd.value

    def _build_ramadan_chart():
        _comms = COMMODITIES if _selected_comm == "All" else [_selected_comm]
        _fig = go.Figure()
        for _c in _comms:
            _sub = ramadan_df[ramadan_df["commodity"] == _c]
            if _sub.empty:
                continue
            _comm_color = COMMODITY_COLORS.get(_c, "#1f77b4")
            for _yr in _sub["year"].unique():
                _yd = _sub[_sub["year"] == _yr].sort_values("month_relative")
                _is_2022 = bool(_yr == 2022)
                _hex = _comm_color.lstrip("#")
                _rgba_base = f"rgba({int(_hex[0:2], 16)},{int(_hex[2:4], 16)},{int(_hex[4:6], 16)}"
                _fig.add_trace(
                    go.Scatter(
                        x=_yd["month_relative"],
                        y=_yd["price_index"],
                        mode="lines",
                        name=f"{_yr} ({_c})",
                        line=dict(
                            width=2.5 if _is_2022 else 0.8,
                            color="red" if _is_2022 else f"{_rgba_base},0.35)",
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
                    line=dict(width=2.5, color=_comm_color),
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
        _comms = COMMODITIES if _selected_comm == "All" else [_selected_comm]
        _df = price_national_df[price_national_df["commodity_consolidated"].isin(_comms)]
        _monthly = compute_price_index(_df)
        _mi = _monthly.groupby("month_of_year")["price_index"].mean()
        _harvest_months = {3, 4, 8, 9}
        _colors = [
            "rgba(34,139,34,0.6)" if m in _harvest_months else "rgba(70,130,180,0.7)"
            for m in range(1, 13)
        ]
        _fig = go.Figure(
            go.Bar(
                x=MONTH_LABELS,
                y=[_mi.get(m, 0) for m in range(1, 13)],
                marker_color=_colors,
                hovertemplate="%{x}<br>Index: %{y:.1f}<extra></extra>",
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
        _comms = COMMODITIES if _selected_comm == "All" else [_selected_comm]
        _df = price_national_df[price_national_df["commodity_consolidated"].isin(_comms)]
        _monthly = compute_price_index(_df)
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
def _(commodity_dd, driver_toggle, mo, summary_df):
    _driver = driver_toggle.value
    _comm = commodity_dd.value
    _sdf = summary_df
    if _comm != "All":
        _sdf = _sdf[_sdf["commodity"] == _comm]
    _table_data = _sdf[
        ["driver", "commodity", "spike_pct", "consistency", "total_years", "lead_months"]
    ].copy()
    if _driver != "All Drivers":
        _table_data = _table_data[_table_data["driver"] == _driver]
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
    _na = mo.md("_N/A_")
    page2_explainer = mo.accordion(
        {
            "Action Cards \u2014 how to read": EXPLAINERS_P2.get("action_cards", _na),
            "Heatmap \u2014 how to read": EXPLAINERS_P2.get("heatmap", _na),
            "Ramadan Overlay \u2014 how to read": EXPLAINERS_P2.get("ramadan", _na),
            "Harvest Chart \u2014 how to read": EXPLAINERS_P2.get("harvest", _na),
            "Year-End Chart \u2014 how to read": EXPLAINERS_P2.get("yearend", _na),
            "Summary Table \u2014 how to read": EXPLAINERS_P2.get("summary", _na),
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
            mo.vstack(
                [
                    mo.md("_Commodity (filters heatmap, driver charts, action cards & table):_"),
                    commodity_dd,
                ],
                gap="0.25rem",
            ),
            mo.vstack(
                [
                    mo.md("_Driver (selects chart type, filters action cards & table):_"),
                    driver_toggle,
                ],
                gap="0.25rem",
            ),
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
            mo.md(
                "_Charts show how prices behave; cards below summarize optimal buying "
                "windows and typical price impacts._"
            ),
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
# Page 3: Geographic Disparity — data load
# ---------------------------------------------------------------------------


@app.cell
def _(load_json, mo, pd):
    _raw = load_json("geographic_disparity.json")
    geo_province_df = pd.DataFrame(_raw)
    geo_province_df["year"] = geo_province_df["year"].astype(int)

    page3_filter_notice = (
        mo.callout(
            mo.md("_No geographic disparity data available._"),
            kind="warn",
        )
        if geo_province_df.empty
        else None
    )

    if not geo_province_df.empty:
        geo_island_df = (
            geo_province_df.groupby("island_group")
            .agg(
                provinces=("admin1", "nunique"),
                avg_price_idr=("avg_price_idr", "mean"),
                avg_index=("price_index_vs_java", "mean"),
            )
            .reset_index()
            .sort_values("avg_index", ascending=True)
        )
    else:
        geo_island_df = pd.DataFrame(
            columns=["island_group", "provinces", "avg_price_idr", "avg_index"]
        )
    return geo_island_df, geo_province_df, page3_filter_notice


# ---------------------------------------------------------------------------
# Page 3: Data notice
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    geo_data_notice = mo.callout(
        mo.md(
            "**Data scope:** Province-level geographic comparison is available for "
            "**Cooking Oil** only \u2014 Rice, Sugar, and Flour have national-level "
            "data only (see **Price Trends** tab). "
            "Data reflects **2024** average prices across 34 provinces."
        ),
        kind="warn",
    )
    return (geo_data_notice,)


# ---------------------------------------------------------------------------
# Page 3: Island KPI cards (cheapest to most expensive)
# ---------------------------------------------------------------------------


@app.cell
def _(geo_island_df, geo_island_dropdown, mo):
    _selected = geo_island_dropdown.value
    _cards = []
    for _i, _row in geo_island_df.iterrows():
        _name = _row["island_group"]
        _premium = _row["avg_index"] - 100
        if _name == "Java":
            _caption = "Baseline"
        else:
            _prefix = "+" if _premium > 0 else ""
            _caption = f"{_prefix}{_premium:.1f}% vs Java"

        _stat = mo.stat(
            value=f"Rp {_row['avg_price_idr']:,.0f}",
            label=_name,
            caption=_caption,
            bordered=True,
        )

        _is_selected = _selected != "All" and _name == _selected
        if _is_selected:
            _stat = mo.callout(_stat, kind="info")
            _cards.insert(0, _stat)
        else:
            _cards.append(_stat)

    geo_island_kpi_cards = mo.hstack(_cards, gap="1rem", widths="equal")
    return (geo_island_kpi_cards,)


# ---------------------------------------------------------------------------
# Page 3: Island group dropdown
# ---------------------------------------------------------------------------


@app.cell
def _(geo_island_df, mo):
    _island_options = ["All"] + geo_island_df["island_group"].tolist()
    geo_island_dropdown = mo.ui.dropdown(
        options=_island_options,
        value="All",
        label="Island Group",
    )
    return (geo_island_dropdown,)


# ---------------------------------------------------------------------------
# Page 3: Bar chart — island group price index vs Java
# ---------------------------------------------------------------------------


@app.cell
def _(commodity_dd, geo_island_df, geo_island_dropdown, go, mo):
    _selected = geo_island_dropdown.value
    _fig = go.Figure()
    if commodity_dd.value != "All" and commodity_dd.value != "Cooking Oil":
        _fig = None
    else:
        _marker_colors = []
        for n in geo_island_df["island_group"]:
            if _selected != "All" and n == _selected:
                _marker_colors.append("#ff7f0e")
            elif n == "Java":
                _marker_colors.append("#b0b0b0")
            elif _selected != "All":
                _marker_colors.append("rgba(31,119,180,0.3)")
            else:
                _marker_colors.append("#1f77b4")

        _fig = go.Figure(
            go.Bar(
                x=geo_island_df["avg_index"],
                y=geo_island_df["island_group"],
                orientation="h",
                marker_color=_marker_colors,
                hovertemplate="<b>%{y}</b><br>Price Index: %{x:.1f}<br>(Java = 100)<extra></extra>",
            )
        )
        _fig.add_vline(x=100, line_dash="dot", line_color="gray")
        _fig.add_annotation(
            x=100,
            y=1.05,
            yref="paper",
            text="Java baseline = 100",
            showarrow=False,
            font=dict(size=11, color="gray"),
        )
        _fig.update_layout(
            height=360,
            xaxis_title="Price Index (Java = 100)",
            yaxis=dict(autorange="reversed"),
            template="plotly_white",
            margin=dict(l=20, r=60, t=40, b=40),
        )

    if _fig is None:
        geo_island_bar_chart = mo.callout(
            mo.md(
                f"**{commodity_dd.value}** has national-level data only \u2014 "
                f"geographic comparison is available for **Cooking Oil** only. "
                f'Select "All" or "Cooking Oil" to view island-level data.'
            ),
            kind="warn",
        )
    else:
        geo_island_bar_chart = mo.ui.plotly(_fig)
    return (geo_island_bar_chart,)


# ---------------------------------------------------------------------------
# Page 3: Province detail table
# ---------------------------------------------------------------------------


@app.cell
def _(commodity_dd, geo_island_dropdown, geo_province_df, mo):
    _island_filter = geo_island_dropdown.value
    _is_cooking_oil = commodity_dd.value in ("All", "Cooking Oil")

    if not _is_cooking_oil:
        geo_province_table = mo.callout(
            mo.md(
                f"**{commodity_dd.value}** has national-level data only. "
                f'Select "All" or "Cooking Oil" for province-level geographic data.'
            ),
            kind="warn",
        )
    else:
        _pdf = geo_province_df.copy()
        if _island_filter != "All":
            _pdf = _pdf[_pdf["island_group"] == _island_filter]
        _pdf = _pdf.sort_values("price_index_vs_java", ascending=False).copy()
        _display = _pdf[
            ["admin1", "island_group", "avg_price_idr", "price_index_vs_java", "months_with_data"]
        ].copy()
        _display.columns = [
            "Province",
            "Island Group",
            "Avg Price (2024)",
            "Index vs Java",
            "Months w/ Data",
        ]

        if _display.empty:
            geo_province_table = mo.callout(
                mo.md("No provinces match the current selection."),
                kind="info",
            )
        else:
            geo_province_table = mo.ui.table(
                _display,
                page_size=10,
            )
    return (geo_province_table,)


# ---------------------------------------------------------------------------
# Page 3: Explainer accordion
# ---------------------------------------------------------------------------


@app.cell
def _(EXPLAINERS_P3, mo):
    _na = mo.md("_N/A_")
    geo_explainer = mo.accordion(
        {
            "Island KPI Cards \u2014 how to read": EXPLAINERS_P3.get("island_cards", _na),
            "Bar Chart \u2014 how to read": EXPLAINERS_P3.get("bar_chart", _na),
            "Province Table \u2014 how to read": EXPLAINERS_P3.get("province_table", _na),
            "Data Scope & Limitations": EXPLAINERS_P3.get("data_scope", _na),
        },
        multiple=True,
    )
    return (geo_explainer,)


# ---------------------------------------------------------------------------
# Page 3: Assembly
# ---------------------------------------------------------------------------


@app.cell
def _(
    commodity_dd,
    geo_data_notice,
    geo_explainer,
    geo_island_bar_chart,
    geo_island_dropdown,
    geo_island_kpi_cards,
    geo_province_table,
    mo,
    page3_filter_notice,
):
    _header = mo.vstack(
        [
            mo.md("# Geographic Disparity"),
            mo.md("**Price comparison across island groups** \u00b7 2024 Cooking Oil prices"),
        ],
        gap="0.25rem",
    )

    _island_controls = mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("_Island group (highlights cards, bar chart, filters province table):_"),
                    geo_island_dropdown,
                ],
                gap="0.25rem",
            ),
        ],
        gap="2rem",
    )

    _island_section = mo.vstack(
        [
            mo.md("## Island Group Comparison"),
            _island_controls,
            geo_island_kpi_cards,
            geo_island_bar_chart,
        ],
        gap="0.75rem",
    )

    _province_section = mo.vstack(
        [
            mo.md("## Province Detail"),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.md("_Commodity (data available for Cooking Oil only):_"),
                            commodity_dd,
                        ],
                        gap="0.25rem",
                    ),
                ],
                gap="2rem",
            ),
            mo.md("_Island Group filter above also applies here._"),
            geo_province_table,
        ],
        gap="0.75rem",
    )

    geo_page_content = mo.vstack(
        [
            _header,
            geo_data_notice,
            *([] if page3_filter_notice is None else [page3_filter_notice]),
            _island_section,
            _province_section,
            geo_explainer,
        ],
        gap="2.5rem",
    )
    return (geo_page_content,)


# ---------------------------------------------------------------------------
# Page 4: Commodity Signals — data load
# ---------------------------------------------------------------------------


@app.cell
def _(load_json, mo, pd):
    # Load correlation summary (pre-computed r values for all pairs x lags)
    _corr_raw = load_json("correlation_summary.json")
    _corr_df = pd.DataFrame(_corr_raw)
    _corr_df[["leader", "follower"]] = _corr_df["commodity_pair"].str.split("-", n=1, expand=True)
    _comm_map = {
        "rice": "Rice",
        "oil": "Cooking Oil",
        "sugar": "Sugar",
        "flour": "Flour",
    }
    _corr_df["leader"] = _corr_df["leader"].map(_comm_map)
    _corr_df["follower"] = _corr_df["follower"].map(_comm_map)
    _corr_df = _corr_df.dropna(subset=["leader", "follower"])

    corr_all_pairs_df = _corr_df.rename(
        columns={
            "lag_months": "lag",
            "pearson_r": "r",
            "pearson_r_pre_2022": "pre_2022_r",
            "pearson_r_post_2022": "post_2022_r",
        }
    ).copy()

    corr_all_pairs_df["stable"] = corr_all_pairs_df.apply(
        lambda r: bool(pd.isna(r["post_2022_r"]) or abs(r["pre_2022_r"] - r["post_2022_r"]) <= 0.2),
        axis=1,
    )

    # Matrix: leader, follower, lag, r
    corr_matrix_df = corr_all_pairs_df[["leader", "follower", "lag", "r"]].copy()

    # Rank-filtered: for each follower, pick the best leader-lag combo by r
    _by_follower = (
        corr_all_pairs_df.sort_values("r", ascending=False)
        .groupby("follower")
        .first()
        .reset_index()
    )
    best_leader_per_follower_df = _by_follower[["follower", "leader", "lag", "r", "stable"]].copy()

    page4_filter_notice = (
        mo.callout(
            mo.md("_No correlation data available._"),
            kind="warn",
        )
        if corr_all_pairs_df.empty
        else None
    )

    # Load monthly price data for scatter + rolling correlation
    _price_raw = load_json("commodity_correlation.json")
    _price_df = pd.DataFrame(_price_raw)
    _price_df["month"] = pd.to_datetime(_price_df["month"])

    _COMMODITIES_ORDER = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    _price_cols = {
        "Rice": "rice_price",
        "Cooking Oil": "oil_price",
        "Sugar": "sugar_price",
        "Flour": "flour_price",
    }

    if not _price_df.empty:
        # Scatter pairs: same-period prices for all 12 ordered pairs
        _rows = []
        for _leader in _COMMODITIES_ORDER:
            for _follower in _COMMODITIES_ORDER:
                if _leader == _follower:
                    continue
                _lcol = _price_cols[_leader]
                _fcol = _price_cols[_follower]
                _sub = _price_df[["month", _lcol, _fcol]].copy()
                _sub.columns = ["date", "leader_price", "follower_price"]
                _sub["leader"] = _leader
                _sub["follower"] = _follower
                _sub["period"] = _sub["date"].apply(
                    lambda d: "pre_2022" if d < pd.Timestamp("2022-01-01") else "post_2022"
                )
                _rows.append(_sub)
        corr_pairs_scatter_df = pd.concat(_rows, ignore_index=True)

        # Rolling 3-year (36-month) correlation for each ordered pair
        _roll_rows = []
        for _leader in _COMMODITIES_ORDER:
            for _follower in _COMMODITIES_ORDER:
                if _leader == _follower:
                    continue
                _lcol = _price_cols[_leader]
                _fcol = _price_cols[_follower]
                _s = _price_df[["month", _lcol, _fcol]].sort_values("month").copy()
                _s.columns = ["date", "leader_price", "follower_price"]
                _s["rolling_r_3yr"] = _s["leader_price"].rolling(36).corr(_s["follower_price"])
                _s = _s.dropna(subset=["rolling_r_3yr"])
                _s["leader"] = _leader
                _s["follower"] = _follower
                _roll_rows.append(_s[["date", "leader", "follower", "rolling_r_3yr"]])
        corr_rolling_r_df = pd.concat(_roll_rows, ignore_index=True)
    else:
        corr_pairs_scatter_df = pd.DataFrame(
            columns=["date", "leader_price", "follower_price", "leader", "follower", "period"]
        )
        corr_rolling_r_df = pd.DataFrame(columns=["date", "leader", "follower", "rolling_r_3yr"])

    return (
        corr_all_pairs_df,
        corr_matrix_df,
        corr_pairs_scatter_df,
        corr_rolling_r_df,
        best_leader_per_follower_df,
        page4_filter_notice,
    )


# ---------------------------------------------------------------------------
# Page 4: Lag selector
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    page4_lag_selector = mo.ui.radio(
        options={"0 months": 0, "1 month": 1, "2 months": 2, "3 months": 3},
        value="1 month",
        label="Lag",
    )
    return (page4_lag_selector,)


# ---------------------------------------------------------------------------
# Page 4: Selected pair state (cross-filter sink)
# ---------------------------------------------------------------------------


@app.cell
def _(corr_all_pairs_df, mo):
    _default = corr_all_pairs_df[corr_all_pairs_df["lag"] == 1].sort_values("r", ascending=False)
    _d_leader = _default.iloc[0]["leader"] if not _default.empty else "Rice"
    _d_follower = _default.iloc[0]["follower"] if not _default.empty else "Flour"

    selected_pair, set_selected_pair = mo.state((_d_leader, _d_follower))
    return selected_pair, set_selected_pair


# ---------------------------------------------------------------------------
# Page 4: Leading indicator callout cards
# ---------------------------------------------------------------------------


@app.cell
def _(best_leader_per_follower_df, commodity_dd, corr_all_pairs_df, mo, page4_lag_selector):
    _comm = commodity_dd.value
    _lag = page4_lag_selector.value

    # Filter by selected lag, then pick best leader per follower at that lag
    _lag_df = corr_all_pairs_df[corr_all_pairs_df["lag"] == _lag]
    if not _lag_df.empty:
        _lag_best = (
            _lag_df.sort_values("r", ascending=False)
            .groupby("follower")
            .first()
            .reset_index()[["follower", "leader", "lag", "r", "stable"]]
        )
    else:
        _lag_best = best_leader_per_follower_df

    # Filter by commodity if not "All"
    _candidates = _lag_best
    if _comm != "All":
        _candidates = _candidates[
            (_candidates["leader"] == _comm) | (_candidates["follower"] == _comm)
        ]

    if _candidates.empty:
        page4_leading_cards = mo.callout(
            mo.md(
                "No strong leading relationship at this lag \u2014 "
                "try a different lag. (Threshold: r \u2265 0.3)"
            ),
            kind="warn",
        )
    else:
        _cards = []
        for _, _row in _candidates.iterrows():
            _flag = "\u2705 Stable post-2022" if _row["stable"] else "\u26a0 Weakened post-2022"
            _r = _row["r"]
            _lag_str = f"{int(_row['lag'])} month(s)" if _row["lag"] != 0 else "same-month"
            _cards.append(
                mo.stat(
                    value=f"r = {_r:.2f}",
                    label=f"{_row['leader']} \u2192 {_row['follower']}",
                    caption=f"Leads by {_lag_str} \u00b7 {_flag}",
                    bordered=True,
                )
            )
        _rows = [
            mo.hstack(_cards[i : i + 2], gap="1rem", widths="equal")
            for i in range(0, len(_cards), 2)
        ]
        page4_leading_cards = mo.vstack(
            [
                mo.md("## Leading Indicators"),
                *_rows,
            ],
            gap="0.5rem",
        )
    return (page4_leading_cards,)


# ---------------------------------------------------------------------------
# Page 4: Correlation matrix heatmap
# ---------------------------------------------------------------------------


@app.cell
def _(corr_matrix_df, go, mo, page4_lag_selector):
    _lag = page4_lag_selector.value
    _at_lag = corr_matrix_df[corr_matrix_df["lag"] == _lag]

    _commodities = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    _z = []
    _text = []
    for _leader in _commodities:
        _row_z, _row_text = [], []
        for _follower in _commodities:
            if _leader == _follower:
                _row_z.append(None)
                _row_text.append("\u2014")
            else:
                _val = _at_lag[(_at_lag["leader"] == _leader) & (_at_lag["follower"] == _follower)][
                    "r"
                ].values
                _r = _val[0] if len(_val) else None
                _row_z.append(_r)
                _row_text.append(f"{_r:.2f}" if _r is not None else "N/A")
        _z.append(_row_z)
        _text.append(_row_text)

    _fig = go.Figure(
        go.Heatmap(
            z=_z,
            x=_commodities,
            y=_commodities,
            text=_text,
            texttemplate="%{text}",
            colorscale="Blues",
            zmin=0,
            zmax=1,
            hovertemplate=(
                "<b>%{y} \u2192 %{x}</b><br>"
                f"r = %{{z:.2f}} at lag {_lag} month(s)<extra></extra>"
            ),
            colorbar=dict(title="r"),
        )
    )
    _fig.update_layout(
        height=240,
        title=f"Cross-Commodity Correlation Matrix \u2014 {_lag}-Month Lag",
        xaxis_title="Following Commodity",
        yaxis_title="Leading Commodity",
        annotations=[
            dict(
                text="Row commodity <b>leads</b> column commodity at selected lag",
                xref="paper",
                yref="paper",
                x=0,
                y=1.12,
                showarrow=False,
                font=dict(size=11, color="gray"),
            )
        ],
    )
    page4_matrix_chart = mo.ui.plotly(_fig)
    return (page4_matrix_chart,)


# ---------------------------------------------------------------------------
# Page 4: Pair selector dropdowns
# ---------------------------------------------------------------------------


@app.cell
def _(mo, selected_pair):
    page4_leader_dd = mo.ui.dropdown(
        options=["Rice", "Cooking Oil", "Sugar", "Flour"],
        value=selected_pair()[0],
        label="Leading commodity",
    )
    page4_follower_dd = mo.ui.dropdown(
        options=["Rice", "Cooking Oil", "Sugar", "Flour"],
        value=selected_pair()[1],
        label="Following commodity",
    )
    return page4_leader_dd, page4_follower_dd


# ---------------------------------------------------------------------------
# Page 4: Selected pair update (matrix click + dropdown sync)
# ---------------------------------------------------------------------------


@app.cell
def _(
    page4_follower_dd,
    page4_leader_dd,
    page4_matrix_chart,
    selected_pair,
    set_selected_pair,
):
    _click_value = page4_matrix_chart.value
    if _click_value and _click_value.get("points"):
        _pt = _click_value["points"][0]
        _leader = _pt.get("y")
        _follower = _pt.get("x")
        if (
            _leader
            and _follower
            and _leader != _follower
            and (_leader, _follower) != selected_pair()
        ):
            set_selected_pair((_leader, _follower))
    else:
        _new_pair = (page4_leader_dd.value, page4_follower_dd.value)
        if _new_pair != selected_pair():
            set_selected_pair(_new_pair)


# ---------------------------------------------------------------------------
# Page 4: Scatter plot (pre/post 2022)
# ---------------------------------------------------------------------------


@app.cell
def _(
    corr_pairs_scatter_df,
    go,
    mo,
    np,
    selected_pair,
    yr_lo,
    yr_hi,
):

    _leader, _follower = selected_pair()
    _pair_data = corr_pairs_scatter_df[
        (corr_pairs_scatter_df["leader"] == _leader)
        & (corr_pairs_scatter_df["follower"] == _follower)
    ]

    if _pair_data.empty:
        page4_scatter_chart = mo.callout(
            mo.md("No price data available for this pair."), kind="warn"
        )
    else:
        _pair_data = _pair_data[_pair_data["date"].dt.year.between(yr_lo, yr_hi)]
        _pre = _pair_data[_pair_data["period"] == "pre_2022"]
        _post = _pair_data[_pair_data["period"] == "post_2022"]

        _fig = go.Figure()
        _fig.add_trace(
            go.Scatter(
                x=_pre["leader_price"],
                y=_pre["follower_price"],
                mode="markers",
                name="Pre-2022",
                marker=dict(color="steelblue", size=6, opacity=0.6),
                hovertemplate=(
                    f"{_leader}: %{{x:,.0f}}<br>{_follower}: %{{y:,.0f}}<extra>Pre-2022</extra>"
                ),
            )
        )
        _fig.add_trace(
            go.Scatter(
                x=_post["leader_price"],
                y=_post["follower_price"],
                mode="markers",
                name="Post-2022",
                marker=dict(color="tomato", size=6, opacity=0.7),
                hovertemplate=(
                    f"{_leader}: %{{x:,.0f}}<br>{_follower}: %{{y:,.0f}}<extra>Post-2022</extra>"
                ),
            )
        )

        _all_x = _pair_data["leader_price"].values
        _all_y = _pair_data["follower_price"].values
        if len(_all_x) > 1:
            _m, _b = np.polyfit(_all_x, _all_y, 1)
            _x_range = np.linspace(_all_x.min(), _all_x.max(), 50)
            _fig.add_trace(
                go.Scatter(
                    x=_x_range,
                    y=_m * _x_range + _b,
                    mode="lines",
                    name="Trend (full period)",
                    line=dict(color="gray", dash="dash", width=1),
                )
            )

        _fig.update_layout(
            height=260,
            xaxis_title=f"{_leader} Price (IDR)",
            yaxis_title=f"{_follower} Price (IDR)",
            title=f"Price Co-Movement: {_leader} \u2192 {_follower}",
            legend=dict(orientation="h", y=-0.25),
            template="plotly_white",
            margin=dict(l=60, r=20, t=40, b=80),
        )
        page4_scatter_chart = mo.ui.plotly(_fig)

    return (page4_scatter_chart,)


# ---------------------------------------------------------------------------
# Page 4: Rolling correlation stability chart
# ---------------------------------------------------------------------------


@app.cell
def _(
    corr_rolling_r_df,
    go,
    mo,
    pd,
    selected_pair,
    yr_lo,
    yr_hi,
):

    _leader, _follower = selected_pair()
    _roll = corr_rolling_r_df[
        (corr_rolling_r_df["leader"] == _leader) & (corr_rolling_r_df["follower"] == _follower)
    ].sort_values("date")
    _roll = _roll[_roll["date"].dt.year.between(yr_lo, yr_hi)]

    if _roll.empty:
        page4_stability_chart = mo.callout(
            mo.md("Insufficient data for rolling correlation."), kind="info"
        )
    else:
        _has_post_2022 = _roll["date"].max() >= pd.Timestamp("2022-01-01")

        _fig = go.Figure()
        _fig.add_trace(
            go.Scatter(
                x=_roll["date"],
                y=_roll["rolling_r_3yr"],
                mode="lines",
                name="Rolling r (3-yr window)",
                line=dict(color="steelblue", width=2),
                hovertemplate="%{x|%Y}<br>r = %{y:.2f}<extra></extra>",
            )
        )
        _fig.add_hline(
            y=0.3,
            line_dash="dot",
            line_color="red",
            annotation_text="r = 0.3 floor",
        )
        if _has_post_2022:
            _fig.add_vline(
                x="2022-01-01",
                line_dash="dash",
                line_color="gray",
                annotation_text="2022 shock",
                annotation_position="top left",
            )
        _fig.update_layout(
            height=220,
            yaxis_title="Correlation (r)",
            yaxis_range=[max(-0.1, _roll["rolling_r_3yr"].min() - 0.05), 1.05],
            title=f"Rolling Correlation Stability \u2014 {_leader} \u2192 {_follower}",
            template="plotly_white",
            margin=dict(l=60, r=20, t=40, b=40),
        )
        page4_stability_chart = mo.ui.plotly(_fig)

    return (page4_stability_chart,)


# ---------------------------------------------------------------------------
# Page 4: Scatter + stability side by side
# ---------------------------------------------------------------------------


@app.cell
def _(mo, page4_scatter_chart, page4_stability_chart):
    page4_scatter_stability_row = mo.hstack(
        [page4_scatter_chart, page4_stability_chart], widths=[0.45, 0.55]
    )
    return (page4_scatter_stability_row,)


# ---------------------------------------------------------------------------
# Page 4: Procurement implication card
# ---------------------------------------------------------------------------


@app.cell
def _(corr_all_pairs_df, mo, pd, page4_lag_selector, selected_pair):
    _leader, _follower = selected_pair()
    _lag = page4_lag_selector.value

    _row = corr_all_pairs_df[
        (corr_all_pairs_df["leader"] == _leader)
        & (corr_all_pairs_df["follower"] == _follower)
        & (corr_all_pairs_df["lag"] == _lag)
    ]

    if _row.empty:
        page4_implication_card = mo.md(
            "_Select a commodity pair from the matrix to see procurement implications._"
        )
    else:
        _r_val = _row.iloc[0]["r"]
        _pre_r = _row.iloc[0]["pre_2022_r"]
        _post_r = _row.iloc[0]["post_2022_r"]
        _is_stable = _row.iloc[0]["stable"]
        _lag_str = "the same month" if _lag == 0 else f"{int(_lag)} month{'s' if _lag != 1 else ''}"

        _r_strength = "weak" if abs(_r_val) < 0.4 else "moderate" if abs(_r_val) < 0.7 else "strong"
        _reliability = (
            "Reliable for procurement planning."
            if _r_strength == "strong"
            else "Directional signal, not a guarantee."
        )
        _body = (
            f"When **{_leader}** prices rise, **{_follower}** prices have "
            f"historically followed within {_lag_str} \u2014 "
            f"this is a **{_r_strength}** correlation (r = {_r_val:.2f}). "
            f"{_reliability}"
        )

        if not _is_stable and pd.notna(_post_r):
            _body += (
                f"\n\n\u26a0 **Relationship weakened post-2022** \u2014 "
                f"treat as a directional signal, not deterministic. "
                f"Pre-2022 r = {_pre_r:.2f}, Post-2022 r = {_post_r:.2f}."
            )

        _body += (
            "\n\n_This recommendation is generated from the data. "
            "It does not account for supplier contract terms or "
            "logistics constraints._"
        )

        _kind = "warn" if (not _is_stable and pd.notna(_post_r)) else "info"

        page4_implication_card = mo.callout(
            mo.vstack(
                [
                    mo.md(f"## Procurement Implication \u2014 {_leader} \u2192 {_follower}"),
                    mo.md(_body),
                ],
                gap="0.5rem",
            ),
            kind=_kind,
        )

    return (page4_implication_card,)


# ---------------------------------------------------------------------------
# Page 4: Full correlation detail table
# ---------------------------------------------------------------------------


@app.cell
def _(
    commodity_dd,
    corr_all_pairs_df,
    mo,
    pd,
    page4_lag_selector,
    selected_pair,
    set_selected_pair,
):
    _lag = page4_lag_selector.value
    _table_data = (
        corr_all_pairs_df[corr_all_pairs_df["lag"] == _lag].sort_values("r", ascending=False).copy()
    )
    _comm = commodity_dd.value
    if _comm != "All":
        _table_data = _table_data[
            (_table_data["leader"] == _comm) | (_table_data["follower"] == _comm)
        ]

    _table_data["stability"] = _table_data.apply(
        lambda r: (
            "\u26a0"
            if (pd.notna(r["post_2022_r"]) and abs(r["pre_2022_r"] - r["post_2022_r"]) > 0.2)
            else "\u2705"
        ),
        axis=1,
    )

    _display = _table_data[
        ["leader", "follower", "r", "pre_2022_r", "post_2022_r", "stability"]
    ].copy()
    _display.columns = [
        "Leader",
        "Follower",
        "r",
        "Pre-2022 r",
        "Post-2022 r",
        "Stability",
    ]

    def _on_table_change(rows):
        if rows:
            _pair = (rows[0]["Leader"], rows[0]["Follower"])
            if _pair != selected_pair():
                set_selected_pair(_pair)

    page4_detail_table = mo.vstack(
        [
            mo.md("## All Pairwise Correlations"),
            mo.ui.table(
                _display,
                page_size=10,
                selection="single",
                on_change=_on_table_change,
            ),
            mo.callout(
                mo.md(
                    "_**Pre/Post 2022 r:** Large divergence (\u26a0) signals a "
                    "relationship that may have been broken by the 2022 commodity "
                    "shock. Use with caution._"
                ),
                kind="neutral",
            ),
        ],
        gap="0.5rem",
    )
    return (page4_detail_table,)


# ---------------------------------------------------------------------------
# Page 4: Data scope callout
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    page4_data_notice = mo.callout(
        mo.md(
            "**Data scope:** Cross-commodity correlation uses national-level monthly "
            "average prices. Rice, Sugar, and Oil data extends through **May 2024**; "
            "Flour data ends **March 2020** (WFP data gap). Pairs involving Flour "
            "have no post-2020 observations, so pre/post-2022 stability comparison "
            "is only meaningful for Rice\u2013Sugar\u2013Oil pairs.\n\n"
            "Correlation measures historical price co-movement and does not imply "
            "causation. Use the stability chart to assess whether relationships "
            "have held over time."
        ),
        kind="info",
    )
    return (page4_data_notice,)


# ---------------------------------------------------------------------------
# Page 4: Explainer accordion
# ---------------------------------------------------------------------------


@app.cell
def _(EXPLAINERS_P4, mo):
    _na = mo.md("_N/A_")
    page4_explainer = mo.accordion(
        {
            "Leading Indicators \u2014 how to read": EXPLAINERS_P4.get("leading_indicators", _na),
            "Correlation Matrix \u2014 how to read": EXPLAINERS_P4.get("correlation_matrix", _na),
            "Scatter Plot \u2014 how to read": EXPLAINERS_P4.get("scatter_plot", _na),
            "Stability Chart \u2014 how to read": EXPLAINERS_P4.get("stability_chart", _na),
            "Implication Card \u2014 how to read": EXPLAINERS_P4.get("implication_card", _na),
        },
        multiple=True,
    )
    return (page4_explainer,)


# ---------------------------------------------------------------------------
# Page 4: Assembly
# ---------------------------------------------------------------------------


@app.cell
def _(
    commodity_dd,
    mo,
    page4_data_notice,
    page4_detail_table,
    page4_explainer,
    page4_filter_notice,
    page4_follower_dd,
    page4_implication_card,
    page4_lag_selector,
    page4_leading_cards,
    page4_leader_dd,
    page4_matrix_chart,
    page4_scatter_stability_row,
    selected_pair,
    show_all_years,
    year_slider,
):
    _header = mo.vstack(
        [
            mo.md("# Commodity Signals"),
            mo.md("_Leading Indicators & Input Cost Bundling \u00b7 2007\u20132024_"),
        ],
        gap="0.25rem",
    )

    _scope_notice = mo.callout(
        mo.md(
            "**Island Group filter disabled on this page.** "
            "All correlation analysis is conducted at national level \u2014 "
            "cross-commodity correlation requires all series at the same granularity. "
            "The **Commodity** filter highlights pairs related to the selected commodity "
            "in the leading indicator cards and detail table. "
            "The **Lag** selector affects the matrix, leading indicator cards, and detail table. "
            "The **Year Range** filter affects the scatter and rolling correlation charts below."
        ),
        kind="info",
    )

    _lead_controls = mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("_Commodity (filters leading indicator cards & table below):_"),
                    commodity_dd,
                ],
                gap="0.25rem",
            ),
        ],
        gap="1rem",
    )

    _lead_section = mo.vstack(
        [
            mo.md("## Leading Indicators"),
            _lead_controls,
            page4_leading_cards,
        ],
        gap="0.75rem",
    )

    _matrix_controls = mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("_Lag (affects matrix, leading cards & detail table below):_"),
                    page4_lag_selector,
                ],
                gap="0.25rem",
            ),
        ],
        gap="1rem",
    )

    _matrix_section = mo.vstack(
        [
            mo.md("## Correlation Matrix"),
            _matrix_controls,
            page4_matrix_chart,
            mo.md("_Click any cell to update the scatter plot and implication card below._"),
        ],
        gap="0.5rem",
    )

    _pair_label = mo.md(f"**Selected pair:** {selected_pair()[0]} \u2192 {selected_pair()[1]}")
    _pair_selector = mo.hstack([page4_leader_dd, mo.md("\u2192"), page4_follower_dd], gap="0.5rem")

    _pair_controls = mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("_Year range (filters scatter & stability charts below):_"),
                    year_slider,
                    show_all_years,
                ],
                gap="0.25rem",
            ),
        ],
        gap="1rem",
    )

    _pair_section = mo.vstack(
        [
            mo.md("## Detailed Pair Analysis"),
            _pair_controls,
            _pair_label,
            _pair_selector,
            page4_scatter_stability_row,
            page4_implication_card,
        ],
        gap="0.75rem",
    )

    _table_section = mo.vstack(
        [
            mo.md("## All Pairwise Correlations"),
            page4_detail_table,
            mo.callout(
                mo.md(
                    "_Table also responds to **Commodity** (above) "
                    "and **Lag** (in Matrix section)._"
                ),
                kind="neutral",
            ),
        ],
        gap="0.5rem",
    )

    page4_content = mo.vstack(
        [
            _header,
            _scope_notice,
            page4_data_notice,
            *([] if page4_filter_notice is None else [page4_filter_notice]),
            _lead_section,
            _matrix_section,
            _pair_section,
            _table_section,
            page4_explainer,
        ],
        gap="1.5rem",
    )
    return (page4_content,)


# ---------------------------------------------------------------------------
# Final assembly: tabs
# ---------------------------------------------------------------------------


@app.cell
def _(
    buy_signal_output,
    commodity_dd,
    data_load_error,
    explainer_card,
    geo_page_content,
    kpi_cards_output,
    max_month,
    mo,
    page1_filter_notice,
    page2_content,
    page4_content,
    show_all_years,
    trend_chart_output,
    year_slider,
    yoy_table_output,
):
    _date_label = max_month.strftime("%b %Y")

    _kpi_section = mo.vstack(
        [
            mo.md("## Latest Prices"),
            kpi_cards_output,
            mo.callout(
                mo.md("Shows **latest available price** per commodity — not affected by filters."),
                kind="info",
            ),
        ],
        gap="0.5rem",
    )

    _trend_section = mo.vstack(
        [
            mo.md("## Price Trends & Forecast"),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.md("_Commodity (filters trend chart below):_"),
                            commodity_dd,
                        ],
                        gap="0.25rem",
                    ),
                    mo.vstack(
                        [
                            mo.md("_Year range (filters trend chart & YoY table):_"),
                            year_slider,
                        ],
                        gap="0.25rem",
                    ),
                    show_all_years,
                ],
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
        ],
        gap="1rem",
    )

    _yoy_section = mo.vstack(
        [
            mo.md("## Annual Price Change"),
            yoy_table_output,
            mo.md("_Year range set above also applies here._"),
        ],
        gap="0.5rem",
    )

    page1_content = mo.vstack(
        [
            mo.md("# Price Trends & Forecast"),
            mo.md(
                f"_Indonesian Staple Commodities \u00b7 "
                f"Jan 2007\u2013{_date_label} + 6-Month Forecast_"
            ),
            *([] if data_load_error is None else [data_load_error]),
            *([] if page1_filter_notice is None else [page1_filter_notice]),
            _kpi_section,
            buy_signal_output,
            _trend_section,
            _yoy_section,
            explainer_card,
        ],
        gap="1.5rem",
    )

    _dashboard_tabs = mo.ui.tabs(
        {
            "Forecast & Signals": page1_content,
            "Seasonal Planning": page2_content,
            "Regional Pricing": geo_page_content,
            "Leading Indicators": page4_content,
        }
    )
    _dashboard_tabs


if __name__ == "__main__":
    app.run()
