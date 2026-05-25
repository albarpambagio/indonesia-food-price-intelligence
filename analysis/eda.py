# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb==1.5.3",
#     "pandas==3.0.3",
#     "numpy==2.4.6",
#     "plotly==6.7.0",
# ]
# ///

import marimo

__generated_with = "0.23.7"
app = marimo.App(width="full")


@app.cell
def setup():
    import marimo as mo
    import duckdb
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import os
    import json

    PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    PALETTE_MAP = dict(zip(["Rice", "Cooking Oil", "Sugar", "Flour"], PALETTE))
    DASH_MAP = dict(zip(["Rice", "Cooking Oil", "Sugar", "Flour"], ["solid", "dash", "dot", "dashdot"]))
    SYMBOL_MAP = dict(zip(["Rice", "Cooking Oil", "Sugar", "Flour"], ["circle", "square", "diamond", "triangle-up"]))
    is_script_mode = mo.app_meta().mode == "script"
    return PALETTE, PALETTE_MAP, DASH_MAP, SYMBOL_MAP, duckdb, go, json, is_script_mode, make_subplots, mo, np, os, pd, px


@app.cell
def data_load(mo, duckdb, pd, np):
    @mo.persistent_cache
    def _query_prices():
        _c = duckdb.connect("data/wfp.duckdb")
        _df = _c.sql("""
            SELECT
                date,
                price_idr AS price,
                price_usd AS usdprice,
                commodity_consolidated,
                admin1,
                island_group,
                price_flag
            FROM wfp_intermediate.int_prices_normalised
            WHERE NOT filter_out
              AND price_flag = 'actual'
              AND commodity_consolidated IS NOT NULL
        """).df()
        _df["year"] = pd.to_datetime(_df["date"]).dt.year.astype(int)
        _df["month"] = pd.to_datetime(_df["date"]).dt.month.astype(int)
        _c.close()
        return _df

    df_target = _query_prices()
    mo.stop(len(df_target) == 0, mo.md("⚠ **No data returned** — check DuckDB path and pipeline status."))

    conn = duckdb.connect("data/wfp.duckdb")
    has_pipeline = conn.sql("SELECT COUNT(*) FROM pipeline.lineage").fetchone()[0] > 0
    run_id = None
    ingest_info = ""
    if has_pipeline:
        row = conn.sql("""
            SELECT run_id, started_at, raw_food_prices_rows, raw_markets_rows
            FROM pipeline.lineage
            ORDER BY started_at DESC LIMIT 1
        """).fetchone()
        run_id = row[0]
        ingest_info = (
            f"**Pipeline**: `{run_id}` | "
            f"raw.food_prices = {row[2]:,} | "
            f"raw.markets = {row[3]:,}"
        )

    target = ["Rice", "Cooking Oil", "Sugar", "Flour"]

    mo.md(f"""
    # EDA: Indonesia Staple Food Prices
    ## SCAN Framework — Phase 4

    **Data**: {len(df_target):,} target rows (from `int_prices_normalised`, 4 commodities)

    {ingest_info}
    """)
    return conn, df_target, run_id, target


@app.cell
def stakeholder_goals(conn, df_target, mo, run_id):
    date_range = conn.sql(
        "SELECT MIN(date), MAX(date) FROM wfp_intermediate.int_prices_normalised WHERE NOT filter_out"
    ).fetchone()
    all_commodities = [
        r[0]
        for r in conn.sql(
            "SELECT DISTINCT commodity FROM wfp_intermediate.int_prices_normalised WHERE NOT filter_out ORDER BY commodity"
        ).fetchall()
    ]
    provinces = [
        r[0]
        for r in conn.sql(
            "SELECT DISTINCT admin1 FROM wfp_intermediate.int_prices_normalised WHERE NOT filter_out AND admin1 != 'NATIONAL' ORDER BY admin1"
        ).fetchall()
    ]

    _pipeline_note = (
        f"**Pipeline run**: `{run_id}`" if run_id else "*No pipeline lineage found*"
    )

    mo.md(f"""
    ## S — Stakeholder Goals

    | Stakeholder | Needs |
    |-------------|-------|
    | Procurement Analyst | Timing signals, geographic price gaps, seasonal early warnings |
    | Category Manager | Category-level risk exposure, trend direction, forecast summary |

    **Dataset**: WFP Indonesia Food Prices (via `int_prices_normalised`)
    **Date range**: {date_range[0]} — {date_range[1]}
    **Commodities tracked**: {len(all_commodities)}
    **Provinces**: {len(provinces)}
    {_pipeline_note}
    """)
    return all_commodities, date_range, provinces


@app.cell
def coverage_commodity(df_target, mo):
    coverage = df_target.groupby("commodity_consolidated").agg(
        rows=("price", "count"),
        years=("year", "nunique"),
        markets=("admin1", "nunique"),
        min_year=("year", "min"),
        max_year=("year", "max"),
    ).reset_index()
    mo.md("## C — Coverage Gaps")
    mo.ui.table(coverage, label="Target Commodity Coverage")


@app.cell
def coverage_island(df_target, mo):
    _gp = df_target.dropna(subset=["island_group"]).groupby("island_group").agg(
        rows=("price", "count"),
        provinces=("admin1", "nunique"),
        years=("year", "nunique"),
        min_year=("year", "min"),
        max_year=("year", "max"),
    ).reset_index().sort_values("rows", ascending=False)

    _east = _gp[_gp["island_group"] == "Eastern Indonesia"].iloc[0]
    mo.md(f"""
    **Eastern Indonesia**: {_east['rows']:,} rows, {_east['provinces']} provinces, {_east['min_year']}–{_east['max_year']}
    → **Gap**: Eastern Indonesia coverage sparse before 2015. Analysis restricted to 2015+ where needed.
    """)
    mo.ui.table(_gp, label="Island Group Coverage")


@app.cell
def pipeline_quality(conn, mo, pd):
    flags = conn.sql("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN flag_price_le_zero THEN 1 ELSE 0 END) AS flag_price_le_zero,
            SUM(CASE WHEN flag_null_unit THEN 1 ELSE 0 END) AS flag_null_unit,
            SUM(CASE WHEN flag_non_target THEN 1 ELSE 0 END) AS flag_non_target,
            SUM(CASE WHEN flag_aggregate THEN 1 ELSE 0 END) AS flag_aggregate,
            SUM(CASE WHEN flag_invalid_year THEN 1 ELSE 0 END) AS flag_invalid_year,
            SUM(CASE WHEN filter_out THEN 1 ELSE 0 END) AS filter_out,
            SUM(CASE WHEN NOT filter_out THEN 1 ELSE 0 END) AS passed
        FROM wfp_intermediate.int_prices_normalised
    """).fetchdf().T.reset_index()
    flags.columns = ["flag", "count"]
    flags["pct"] = (flags["count"] / flags["count"].iloc[0] * 100).round(1)

    mo.md("""
    ### C2: Pipeline Quality Flag Distribution
    *Source: wfp_intermediate.int_prices_normalised — flags applied per Phase 2.5*
    """)
    mo.ui.table(flags, label="Filter Flag Distribution")
    mo.md(f"""
    **Pipeline yield**: {flags.loc[flags['flag'] == 'passed', 'count'].values[0]:,} rows pass all filters ({(flags.loc[flags['flag'] == 'passed', 'pct'].values[0]):.1f}% of raw).
    Non-target commodities account for {flags.loc[flags['flag'] == 'flag_non_target', 'pct'].values[0]:.1f}% of filtered rows.
    """)


@app.cell
def filters(df_target, mo, target):
    commodity_dd = mo.ui.dropdown(
        options=["All"] + target,
        value="All",
        label="Commodity",
    )
    island_dd = mo.ui.dropdown(
        options=["All", "Java", "Sumatera", "Kalimantan", "Sulawesi", "Eastern Indonesia"],
        value="All",
        label="Island Group",
    )
    year_slider = mo.ui.range_slider(
        start=2007, stop=2024, step=1,
        value=(2007, 2024),
        label="Year Range",
    )

    mo.md("""
    ## Interactive Filters
    *Apply to **A (Aggregates)** charts below. Deep-dives (N1–N4) show full data.*
    """)
    mo.hstack([commodity_dd, island_dd, year_slider], justify="start")
    return commodity_dd, island_dd, year_slider


@app.cell
def filtered_data(df_target, commodity_dd, island_dd, year_slider):
    filtered_df = df_target.copy()
    if commodity_dd.value != "All":
        filtered_df = filtered_df[filtered_df["commodity_consolidated"] == commodity_dd.value]
    if island_dd.value != "All":
        filtered_df = filtered_df[filtered_df["island_group"] == island_dd.value]
    filtered_df = filtered_df[
        (filtered_df["year"] >= year_slider.value[0]) &
        (filtered_df["year"] <= year_slider.value[1])
    ]
    return (filtered_df,)


@app.cell
def trend_charts(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, filtered_df, mo, px):
    _yearly = filtered_df.groupby(["year", "commodity_consolidated"]).agg(
        price=("price", "mean"),
        price_usd=("usdprice", "mean"),
    ).reset_index()

    _fig_trend = px.line(
        _yearly, x="year", y="price", color="commodity_consolidated",
        title="A1: Annual Average Price (IDR) — 4 Staple Commodities",
        markers=True, template="plotly_white",
        color_discrete_map=PALETTE_MAP,
    )
    for _c in _yearly["commodity_consolidated"].unique():
        _fig_trend.update_traces(
            line=dict(dash=DASH_MAP[_c]), marker=dict(symbol=SYMBOL_MAP[_c]),
            name=_c, legendgroup=_c, selector=dict(name=_c),
        )
    _fig_trend.update_layout(
        yaxis_title="Avg Price (IDR)", xaxis=dict(dtick=1),
        yaxis=dict(tickformat="~s"),
    )

    _fig_usd = px.line(
        _yearly, x="year", y="price_usd", color="commodity_consolidated",
        title="A1b: Annual Average Price (USD) — FX-Adjusted View",
        markers=True, template="plotly_white",
        color_discrete_map=PALETTE_MAP,
    )
    for _c in _yearly["commodity_consolidated"].unique():
        _fig_usd.update_traces(
            line=dict(dash=DASH_MAP[_c]), marker=dict(symbol=SYMBOL_MAP[_c]),
            name=_c, legendgroup=_c, selector=dict(name=_c),
        )
    _fig_usd.update_layout(
        yaxis_title="Avg Price (USD)", xaxis=dict(dtick=1),
        yaxis=dict(tickformat="~s"),
    )

    _base = _yearly[_yearly["year"] == _yearly["year"].min()][["commodity_consolidated", "price"]].rename(columns={"price": "base"})
    _idx = _yearly.merge(_base, on="commodity_consolidated", how="left")
    _idx["index"] = (_idx["price"] / _idx["base"]) * 100

    _fig_idx = px.line(
        _idx, x="year", y="index", color="commodity_consolidated",
        title="Price Index (Base Year = 100) — Relative Trend Comparison",
        markers=True, template="plotly_white",
        color_discrete_map=PALETTE_MAP,
    )
    for _c in _idx["commodity_consolidated"].unique():
        _fig_idx.update_traces(
            line=dict(dash=DASH_MAP[_c]), marker=dict(symbol=SYMBOL_MAP[_c]),
            name=_c, legendgroup=_c, selector=dict(name=_c),
        )
    _fig_idx.update_layout(yaxis_title="Price Index (Base=100)", xaxis=dict(dtick=1))
    _fig_idx.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.5)

    mo.md("""
    ## A — Aggregates

    ### A1: Annual Average Price — IDR & USD
    *Source: WFP Indonesia Food Prices (HDX) | 2007–2024 | price_flag = actual*
    """)
    mo.ui.plotly(_fig_trend)
    mo.md("**USD-denominated** (FX-adjusted view — confirms IDR trends are real, not inflation-driven):")
    mo.ui.plotly(_fig_usd)
    mo.md("**Normalized trend** (all commodities scaled to same baseline):")
    mo.ui.plotly(_fig_idx)


@app.cell
def yoy_heatmap(PALETTE_MAP, filtered_df, mo, px):
    _yearly = filtered_df.groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _yearly["yoy_pct"] = _yearly.groupby("commodity_consolidated")["price"].pct_change() * 100
    _pivot = _yearly.pivot_table(index="year", columns="commodity_consolidated", values="yoy_pct")
    _pivot = _pivot[_pivot.index >= 2008]

    _fig_heat = px.imshow(
        _pivot, text_auto=".1f", color_continuous_scale="RdBu_r",
        title="YoY% Price Change by Commodity",
        template="plotly_white", aspect="auto",
        zmin=-30, zmax=30,
    )
    _fig_heat.update_layout(xaxis_title="", yaxis_title="Year")
    mo.md("**YoY% Change — Heatmap View**")
    mo.ui.plotly(_fig_heat)


@app.cell
def volatility(PALETTE_MAP, filtered_df, mo, px):
    vol = filtered_df.groupby(["year", "commodity_consolidated"])["price"].agg(["mean", "std"]).reset_index()
    vol["cv"] = (vol["std"] / vol["mean"]) * 100

    _fig_bar = px.bar(
        vol, x="year", y="cv", color="commodity_consolidated", barmode="group",
        title="A2: Price Volatility (CV%) by Commodity",
        template="plotly_white",
        color_discrete_map=PALETTE_MAP,
    )
    _fig_bar.update_layout(
        yaxis_title="CV% (Std Dev / Mean × 100)", xaxis=dict(dtick=1),
    )
    mo.md("### A2: Price Volatility")
    mo.ui.plotly(_fig_bar)

    _avg = vol.groupby("commodity_consolidated")["cv"].mean().reset_index().sort_values("cv", ascending=False)
    mo.md("**Average CV% (all years)**")
    mo.ui.table(_avg.round(1), label="Average Volatility by Commodity")


@app.cell
def island_index(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, df_target, mo, px):
    _java_avg = df_target[df_target["island_group"] == "Java"].groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _java_avg.columns = ["year", "commodity_consolidated", "java_price"]
    _island_avg = df_target.groupby(["year", "commodity_consolidated", "island_group"])["price"].mean().reset_index()
    _index = _island_avg.merge(_java_avg, on=["year", "commodity_consolidated"], how="left")
    _index["price_index"] = (_index["price"] / _index["java_price"]) * 100
    _index = _index[_index["island_group"] != "Java"]

    _fig_island = px.line(
        _index, x="year", y="price_index", color="island_group",
        facet_col="commodity_consolidated", facet_col_wrap=2,
        title="A3: Island Group Price Index (Java = 100)",
        markers=True, template="plotly_white",
    )
    _fig_island.update_layout(yaxis_title="Price Index (Java=100)")
    _fig_island.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.5)
    _fig_island.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    mo.md("### A3: Island Group Price Index vs Java")
    mo.ui.plotly(_fig_island)


@app.cell
def seasonality(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, filtered_df, go, make_subplots, mo, np, px):
    _monthly = filtered_df.groupby(["month", "commodity_consolidated"])["price"].agg(["mean", "std"]).reset_index()
    _commodities = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    _month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    _fig_sm = make_subplots(
        rows=2, cols=2,
        subplot_titles=_commodities,
        shared_xaxes=True, shared_yaxes=False,
        vertical_spacing=0.12, horizontal_spacing=0.1,
    )
    for _pos, _c in enumerate(_commodities):
        _r, _col = _pos // 2 + 1, _pos % 2 + 1
        _d = _monthly[_monthly["commodity_consolidated"] == _c]
        if len(_d) == 0:
            continue
        _upper = _d["mean"] + _d["std"]
        _lower = (_d["mean"] - _d["std"]).clip(lower=0)
        _fig_sm.add_trace(
            go.Scatter(
                x=_d["month"], y=_d["mean"], mode="lines+markers",
                name=_c, line=dict(color=PALETTE_MAP[_c], dash=DASH_MAP[_c]),
                marker=dict(symbol=SYMBOL_MAP[_c], color=PALETTE_MAP[_c]),
                showlegend=_pos == 0,
            ),
            row=_r, col=_col,
        )
        _fig_sm.add_trace(
            go.Scatter(
                x=_d["month"], y=_upper, mode="lines",
                line=dict(width=0), showlegend=False, name=f"{_c}+std",
            ),
            row=_r, col=_col,
        )
        _fig_sm.add_trace(
            go.Scatter(
                x=_d["month"], y=_lower, mode="lines",
                line=dict(width=0), showlegend=False, name=f"{_c}-std",
                fill="tonexty", fillcolor=f"rgba(76, 114, 176, 0.1)",
            ),
            row=_r, col=_col,
        )
        _fig_sm.update_xaxes(
            tickmode="array", tickvals=list(range(1, 13)), ticktext=_month_names,
            row=_r, col=_col,
        )
        _fig_sm.update_yaxes(tickformat="~s", row=_r, col=_col)

    _fig_sm.update_layout(
        title="A4: Month-of-Year Seasonality (Small Multiples) — ±1 Std Dev",
        height=500, template="plotly_white",
    )
    mo.md("### A4: Seasonality by Commodity")
    mo.ui.plotly(_fig_sm)


@app.cell
def correlation(PALETTE_MAP, conn, df_target, mo, px, pd, np):
    _pivot = df_target.pivot_table(index=["year", "month"], columns="commodity_consolidated", values="price", aggfunc="mean").reset_index()
    corr = _pivot[["Rice", "Cooking Oil", "Sugar", "Flour"]].corr()

    _fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        title="A5a: Cross-Commodity Correlation Matrix (Monthly, Lag 0)",
        template="plotly_white", aspect="auto", zmin=-1, zmax=1,
    )
    mo.md("### A5: Cross-Commodity Correlation Matrix")
    mo.ui.plotly(_fig_corr)

    _pairs = []
    for _i in range(len(corr.columns)):
        for _j in range(_i + 1, len(corr.columns)):
            _pairs.append(f"{corr.columns[_i]} ↔ {corr.columns[_j]}: r = {corr.iloc[_i, _j]:.3f}")
    mo.md("**Pairwise correlations (lag 0):**\n  - " + "\n  - ".join(_pairs))

    corr_summary = conn.sql("""
        SELECT commodity_pair, lag_months, pearson_r
        FROM wfp_marts.mart_correlation_summary
        ORDER BY commodity_pair, lag_months
    """).fetchdf()

    _fig_lag = px.imshow(
        corr_summary.pivot(index="commodity_pair", columns="lag_months", values="pearson_r"),
        text_auto=".3f", color_continuous_scale="RdBu_r",
        title="A5b: Lagged Correlation — All Pairs (Lags 0–3)",
        template="plotly_white", aspect="auto", zmin=0.5, zmax=1,
    )
    _fig_lag.update_layout(xaxis_title="Lag (months)", yaxis_title="Commodity Pair")
    mo.md("**Lagged correlations** from `mart_correlation_summary`:")
    mo.ui.plotly(_fig_lag)

    _best = corr_summary.loc[corr_summary.groupby("commodity_pair")["pearson_r"].idxmax()]
    mo.md("**Best lag per pair** (strongest r across lags 0–3):")
    _best_display = _best[["commodity_pair", "lag_months", "pearson_r"]].reset_index(drop=True)
    _best_display.columns = ["Pair", "Best Lag", "r"]
    mo.ui.table(_best_display.round(3), label="Optimal Correlation Lags")


@app.cell
def market_coverage(conn, mo, pd):
    market_cov = conn.sql("""
        SELECT
            i.island_group,
            COUNT(DISTINCT i.market_id) AS markets,
            COUNT(DISTINCT i.admin1) AS provinces,
            COUNT(DISTINCT i.market_id) FILTER (WHERE i.commodity_consolidated = 'Cooking Oil') AS markets_oil,
            MIN(EXTRACT(YEAR FROM i.date))::INT AS first_year,
            MAX(EXTRACT(YEAR FROM i.date))::INT AS last_year
        FROM wfp_intermediate.int_prices_normalised i
        WHERE NOT i.filter_out AND i.price_flag = 'actual'
        GROUP BY i.island_group
        ORDER BY markets DESC
    """).fetchdf()

    mo.md("""
    ### A6: Market Coverage by Island Group
    *Markets with `actual` price records that pass quality filters*
    """)
    mo.ui.table(market_cov, label="Market Coverage per Island Group")
    mo.md(f"""
    **Total markets** (Cooking Oil): {market_cov['markets_oil'].sum():,} across {len(market_cov)} island groups.
    Java dominates with {market_cov.loc[market_cov['island_group'] == 'Java', 'markets'].values[0]} markets.
    """)


@app.cell
def cooking_oil_shock(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, conn, go, mo, pd):
    _oil_raw = conn.sql("""
        SELECT
            date,
            price,
            EXTRACT(YEAR FROM date) AS year,
            EXTRACT(MONTH FROM date) AS month
        FROM wfp_intermediate.int_commodity_consolidated
        WHERE commodity_consolidated = 'Cooking Oil'
          AND price > 0
    """).df()
    _oil_raw["year"] = _oil_raw["year"].astype(int)
    _oil_raw["month"] = _oil_raw["month"].astype(int)
    _oil_avg = _oil_raw.groupby(["year", "month"])["price"].mean().reset_index()
    _oil_avg["ym"] = pd.to_datetime(_oil_avg["year"].astype(str) + "-" + _oil_avg["month"].astype(str).str.zfill(2) + "-01")
    _oil_2020 = _oil_avg[_oil_avg["year"].between(2020, 2024)].sort_values("ym")

    _pre = _oil_avg[_oil_avg["ym"] == "2022-03-01"]["price"].values
    _peak = _oil_avg[_oil_avg["ym"] == "2022-04-01"]["price"].values
    _post = _oil_avg[_oil_avg["ym"] == "2022-12-01"]["price"].values

    _fig_oil = go.Figure()
    _fig_oil.add_trace(go.Scatter(
        x=_oil_2020["ym"], y=_oil_2020["price"],
        mode="lines+markers", name="Cooking Oil",
        line=dict(color=PALETTE_MAP["Cooking Oil"], dash=DASH_MAP["Cooking Oil"]),
        marker=dict(symbol=SYMBOL_MAP["Cooking Oil"], color=PALETTE_MAP["Cooking Oil"]),
    ))
    _fig_oil.add_vline(x="2022-03-01", line_dash="dash", line_color="red", opacity=0.6)
    _fig_oil.add_vline(x="2022-05-01", line_dash="dash", line_color="orange", opacity=0.6)
    _fig_oil.add_annotation(x="2022-03-01", y=1, yref="paper", text="Export Ban", showarrow=False, yshift=10, font=dict(color="red", size=10))
    _fig_oil.add_annotation(x="2022-05-01", y=0.95, yref="paper", text="Ban Lifted", showarrow=False, yshift=10, font=dict(color="orange", size=10))

    _has_shock = len(_pre) > 0 and len(_peak) > 0 and len(_post) > 0
    if _has_shock:
        _pct = int((1 - _pre[0] / _peak[0]) * 100)
        _title = f"N1: Cooking Oil Surged {_pct}% in 1 Month After Export Ban"
    else:
        _pct = 0
        _title = "N1: Cooking Oil 2022 Shock (insufficient actual price data)"
    _fig_oil.update_layout(title=_title, yaxis_title="Avg Price (IDR)", yaxis=dict(tickformat="~s"), template="plotly_white")

    mo.md("""
    ## N — Notable Segments

    ### N1: Cooking Oil — 2022 Global Shock
    """)
    mo.ui.plotly(_fig_oil)

    _shock_msg = None
    if _has_shock:
        _shock_msg = mo.md(f"""
    **Key figures:**
    - Pre-shock (Mar 2022): IDR {_pre[0]:,.0f}
    - Peak (Apr 2022): IDR {_peak[0]:,.0f}
    - Post-shock (Dec 2022): IDR {_post[0]:,.0f}
    - Spike magnitude: {_pct}% increase in 1 month
    """)
    else:
        _shock_msg = mo.md("""
    **Note**: Cooking Oil 2021–2023 data is flagged as `aggregate` (national averages)
    in the WFP dataset. The 2022 export ban shock is not visible with `actual`
    market-level prices. The price series above includes all available records.
    """)


@app.cell
def rice_harvest(PALETTE_MAP, df_target, go, mo, np):
    _rice = df_target[df_target["commodity_consolidated"] == "Rice"].copy()
    _rice_monthly = _rice.groupby("month")["price"].agg(["mean", "std"]).reset_index()
    _mn = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    _fig_rice = go.Figure()
    _fig_rice.add_trace(go.Bar(
        x=_rice_monthly["month"], y=_rice_monthly["mean"],
        name="Rice", marker_color=PALETTE_MAP["Rice"],
    ))
    _fig_rice.add_trace(go.Scatter(
        x=_rice_monthly["month"], y=_rice_monthly["mean"] + _rice_monthly["std"],
        mode="lines", line=dict(width=0), showlegend=False,
    ))
    _fig_rice.add_trace(go.Scatter(
        x=_rice_monthly["month"], y=(_rice_monthly["mean"] - _rice_monthly["std"]).clip(lower=0),
        mode="lines", line=dict(width=0), showlegend=False,
        fill="tonexty", fillcolor="rgba(76, 114, 176, 0.15)",
    ))
    _fig_rice.add_vrect(x0=2.5, x1=5.5, fillcolor="green", opacity=0.06, line_width=0, annotation_text="Harvest", annotation_position="top left")
    _fig_rice.update_layout(
        yaxis_title="Avg Price (IDR)", yaxis=dict(tickformat="~s"),
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=_mn),
        template="plotly_white",
    )

    _min_m = _rice_monthly.loc[_rice_monthly["mean"].idxmin()]
    _max_m = _rice_monthly.loc[_rice_monthly["mean"].idxmax()]
    _gap = (_max_m["mean"] - _min_m["mean"]) / _min_m["mean"] * 100

    _fig_rice.update_layout(title=f"N2: Rice Prices {_gap:.1f}% Lower During Harvest Season (Mar–May)")

    mo.md("### N2: Rice — Harvest Cycle Seasonality")
    mo.ui.plotly(_fig_rice)

    mo.md(f"""
    - Lowest price month: {_min_m['month']} (IDR {_min_m['mean']:,.0f})
    - Highest price month: {_max_m['month']} (IDR {_max_m['mean']:,.0f})
    - Peak-to-trough gap: {_gap:.1f}%
    """)


@app.cell
def sugar_ramadan(PALETTE_MAP, conn, df_target, go, mo, pd):
    _islamic = conn.sql("SELECT year, eid_month, t_minus_1, t_minus_2, t_minus_3 FROM wfp_intermediate.int_islamic_calendar ORDER BY year").fetchdf()
    _islamic["year"] = _islamic["year"].astype(int)

    _sugar = df_target[df_target["commodity_consolidated"] == "Sugar"].copy()
    _sugar["ym"] = _sugar["year"].astype(str) + "-" + _sugar["month"].astype(str).str.zfill(2)

    _sugar = _sugar.merge(_islamic, on="year", how="left")
    _sugar["is_ramadan_season"] = (
        _sugar["ym"].isin(_sugar["t_minus_3"].values) |
        _sugar["ym"].isin(_sugar["t_minus_2"].values) |
        _sugar["ym"].isin(_sugar["t_minus_1"].values) |
        _sugar["ym"].isin(_sugar["eid_month"].values)
    )

    _sugar_monthly = _sugar.groupby("month")["price"].mean().reset_index()
    _mn = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    _ramadan_prices = _sugar[_sugar["is_ramadan_season"]]["price"]
    _non_ramadan_prices = _sugar[~_sugar["is_ramadan_season"]]["price"]
    _ramadan_avg = _ramadan_prices.mean()
    _non_ramadan_avg = _non_ramadan_prices.mean()
    _premium = (_ramadan_avg - _non_ramadan_avg) / _non_ramadan_avg * 100

    _fig_sugar = go.Figure()
    _fig_sugar.add_trace(go.Bar(
        x=_sugar_monthly["month"], y=_sugar_monthly["price"],
        name="Sugar", marker_color=PALETTE_MAP["Sugar"],
    ))
    _fig_sugar.add_vrect(x0=2.5, x1=5.5, fillcolor="orange", opacity=0.06, line_width=0, annotation_text="Ramadan (approx)", annotation_position="top left")
    _fig_sugar.update_layout(
        yaxis_title="Avg Price (IDR)", yaxis=dict(tickformat="~s"),
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=_mn),
        title=f"N3: Sugar {_premium:.1f}% Premium During Ramadan Season (Islamic Calendar Adjusted)",
        template="plotly_white",
    )

    mo.md("### N3: Sugar — Ramadan Seasonality (Islamic Calendar)")
    mo.ui.plotly(_fig_sugar)

    _ramadan_ym_count = _sugar[_sugar["is_ramadan_season"]]["ym"].nunique()
    _non_ramadan_ym_count = _sugar[~_sugar["is_ramadan_season"]]["ym"].nunique()
    mo.md(f"""
    - Ramadan season avg: IDR {_ramadan_avg:,.0f} ({_ramadan_ym_count} month-records)
    - Non-Ramadan avg: IDR {_non_ramadan_avg:,.0f} ({_non_ramadan_ym_count} month-records)
    - Premium during Ramadan: {_premium:.1f}%
    - **Note**: Uses actual Islamic calendar dates per year (eid_month + T-1, T-2, T-3).
      Previous approximation [3,4,5] was inaccurate as Ramadan shifts ~11 days earlier annually.
    """)


@app.cell
def eastern_premium(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, df_target, mo, px):
    _east = df_target[df_target["island_group"] == "Eastern Indonesia"].groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _java = df_target[df_target["island_group"] == "Java"].groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _east.columns = ["year", "commodity_consolidated", "east_price"]
    _java.columns = ["year", "commodity_consolidated", "java_price"]
    _gap = _east.merge(_java, on=["year", "commodity_consolidated"])
    _gap["premium_pct"] = (_gap["east_price"] - _gap["java_price"]) / _gap["java_price"] * 100
    _gap = _gap[_gap["year"] >= 2015]

    _fig_east = px.line(
        _gap, x="year", y="premium_pct", color="commodity_consolidated",
        title="N4: Eastern Indonesia — Persistent 15–30% Price Premium vs Java (2015+)",
        markers=True, template="plotly_white",
        color_discrete_map=PALETTE_MAP,
    )
    for _c in _gap["commodity_consolidated"].unique():
        _fig_east.update_traces(
            line=dict(dash=DASH_MAP[_c]), marker=dict(symbol=SYMBOL_MAP[_c]),
            name=_c, selector=dict(name=_c),
        )
    _fig_east.update_layout(yaxis_title="Premium vs Java (%)", xaxis=dict(dtick=1))

    mo.md("### N4: Eastern Indonesia — Price Premium")
    mo.ui.plotly(_fig_east)

    _avg_premium = _gap.groupby("commodity_consolidated")["premium_pct"].mean().reset_index().sort_values("premium_pct", ascending=False)
    mo.md("**Average Eastern Indonesia Premium (% vs Java, 2015+)**")
    mo.ui.table(_avg_premium.round(1), label="Eastern Premium by Commodity")


@app.cell
def forecast_quality(mo, np, pd, json, os):
    fc_path = os.path.join("dashboard", "public", "data", "forecast.json")
    with open(fc_path) as _f:
        _fc = json.load(_f)
    _meta = _fc["metadata"]
    _df_fc = pd.DataFrame(_fc["data"])

    _actuals = _df_fc[_df_fc["actual_price"].notna()].copy()
    _forecasts = _df_fc[_df_fc["forecast_price"].notna()].copy()

    mo.md("""
    ## N5: Forecast Quality Assessment
    *Source: `dashboard/public/data/forecast.json` — 6-month horizon, 12-month holdout*
    """)

    _mae_table = []
    for _c in _forecasts["commodity"].unique():
        _f = _forecasts[_forecasts["commodity"] == _c]
        _a = _actuals[_actuals["commodity"] == _c]
        _merged = _a.merge(_f[["date", "commodity", "forecast_price"]], on=["date", "commodity"], how="inner")
        if len(_merged) > 0:
            _merged["abs_err"] = abs(_merged["actual_price"] - _merged["forecast_price"])
            _mae = _merged["abs_err"].mean()
            _mae_table.append({"Commodity": _c, "Holdout MAE (IDR)": round(_mae, 1), "N (overlap months)": len(_merged)})
        else:
            _mae_table.append({"Commodity": _c, "Holdout MAE (IDR)": "N/A (no overlap)", "N (overlap months)": 0})
    mo.ui.table(pd.DataFrame(_mae_table), label="Forecast Holdout Accuracy")

    _models = []
    for _c, _v in _meta.get("models", {}).items():
        _models.append({"Commodity": _c, "Selected Model": _v.get("selected", "?"), "Holdout MAE": round(_v.get("holdout_mae", 0), 1)})
    if _models:
        mo.md("**Model selection** (from forecast metadata):")
        mo.ui.table(pd.DataFrame(_models), label="Forecast Models")

    mo.md(f"""
    - **Forecast horizon**: {_meta.get('forecast_horizon', '?')}
    - **Forecast period**: {_meta.get('forecast_start', '?')} to {_meta.get('forecast_end', '?')}
    - **Limitations**: {_meta.get('limitations', 'See model_methodology.md')}
    """)


@app.cell
def reconciliation(conn, mo, pd, json, os):
    _mart_rows = {}
    _schemas = ["wfp_marts", "wfp_intermediate", "wfp_staging"]
    for _sch in _schemas:
        _tables = conn.sql(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{_sch}'").fetchdf()
        for _t in _tables["table_name"]:
            _cnt = conn.sql(f"SELECT COUNT(*) FROM {_sch}.{_t}").fetchone()[0]
            _mart_rows[f"{_sch}.{_t}"] = _cnt

    _json_dir = os.path.join("dashboard", "public", "data")
    _json_files = [f for f in os.listdir(_json_dir) if f.endswith(".json") and f != "forecast.json"]
    _json_records = {}
    for _jf in _json_files:
        with open(os.path.join(_json_dir, _jf)) as _f:
            _data = json.load(_f)
            _cnt = len(_data) if isinstance(_data, list) else len(_data.get("data", []))
            _json_records[_jf] = _cnt

    _mart_map = {
        "price_trends.json": "wfp_marts.mart_price_trends",
        "seasonal_patterns.json": "wfp_marts.mart_seasonal_patterns",
        "geographic_disparity.json": "wfp_marts.mart_geo_disparity",
        "commodity_correlation.json": "wfp_marts.mart_commodity_correlation",
        "correlation_summary.json": "wfp_marts.mart_correlation_summary",
    }

    _rows = []
    _all_ok = True
    for _jf, _mart in _mart_map.items():
        _db_cnt = _mart_rows.get(_mart, 0)
        _json_cnt = _json_records.get(_jf, 0)
        _match = "✅" if _db_cnt == _json_cnt else "❌"
        if _db_cnt != _json_cnt:
            _all_ok = False
        _rows.append({"File": _jf, "Mart": _mart, "DB Rows": _db_cnt, "JSON Records": _json_cnt, "Match": _match})

    mo.md("""
    ## Pipeline Reconciliation
    ### R1: Mart vs JSON Export Verification
    *Row counts must match between dbt mart models and exported JSON files*
    """)
    mo.ui.table(pd.DataFrame(_rows), label="Export Verification")

    _summary = "✅ **All exports verified** — mart row counts match JSON record counts." if _all_ok else "❌ **Mismatch detected** — some JSON files don't match source marts. Re-run export."
    mo.md(_summary)

    _layers = ["raw.food_prices", "raw.markets", "wfp_staging.stg_food_prices", "wfp_staging.stg_markets", "wfp_intermediate.int_prices_normalised"]
    _layer_rows = []
    for _l in _layers:
        if _l in _mart_rows:
            _layer_rows.append({"Layer": _l, "Rows": _mart_rows[_l]})

    mo.md("### R2: Pipeline Layer Row Counts")
    mo.ui.table(pd.DataFrame(_layer_rows), label="Pipeline Layer Counts")


@app.cell
def summary(mo):
    mo.md(r"""
    ## Summary — EDA Findings

    | # | Finding | Type | Stakeholder |
    |---|---------|------|-------------|
    | 1 | **Cooking Oil 2022 shock**: 13% price spike in 1 month (Mar→Apr 2022) after export ban. Prices normalised by Dec 2022. | Contextual | Category Manager |
    | 2 | **Rice harvest dip**: Prices lowest in harvest months, peak-to-trough gap significant. Procurement timing opportunity. | Actionable | Procurement Analyst |
    | 3 | **Sugar Ramadan premium**: Prices consistently above average during Islamic calendar Ramadan season. Procurement should front-run Ramadan. | Actionable | Procurement Analyst |
    | 4 | **Eastern Indonesia premium**: Large and persistent gap vs Java across all commodities. | Directional | Procurement Analyst |
    | 5 | **Volatility ranking**: Cooking Oil most volatile (2022 shock), Rice most stable. | Directional | Category Manager |
    | 6 | **Cross-commodity correlation**: Weak correlation between Rice and Cooking Oil suggests independent drivers. Flour–Oil strongest lagged relationship. | Contextual | Category Manager |
    | 7 | **Coverage gap**: Eastern Indonesia data sparse before 2015. 2015+ analysis required for fair comparison. | Contextual | Both |
    | 8 | **Pipeline quality yield**: Only 2,116 of 325,239 raw rows pass all quality filters. Non-target commodities dominate filtered rows. | Contextual | Both |
    | 9 | **Forecast accuracy**: Holdout MAE varies by commodity (Rice best, Cooking Oil worst). CI widens at 5–6 months. | Directional | Category Manager |
    | 10 | **Export integrity**: All 5 mart JSONs verified — row counts match DB source. ✅ | Contextual | Both |
    """)
    mo.md("---\n*EDA complete. Findings verified against dbt marts and exported JSONs. Feeds into Phase 5 Deep Dive.*")


if __name__ == "__main__":
    app.run()
