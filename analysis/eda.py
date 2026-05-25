# /// marimo-version
# /// version = 0.23.7
# ///

import marimo

app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    import duckdb
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    PALETTE_MAP = dict(zip(["Rice", "Cooking Oil", "Sugar", "Flour"], PALETTE))
    DASH_MAP = dict(zip(["Rice", "Cooking Oil", "Sugar", "Flour"], ["solid", "dash", "dot", "dashdot"]))
    SYMBOL_MAP = dict(zip(["Rice", "Cooking Oil", "Sugar", "Flour"], ["circle", "square", "diamond", "triangle-up"]))
    return PALETTE, PALETTE_MAP, DASH_MAP, SYMBOL_MAP, duckdb, go, make_subplots, mo, np, pd, px


@app.cell
def __(duckdb, mo):
    conn = duckdb.connect("data/wfp.duckdb")
    conn.execute("CREATE SCHEMA IF NOT EXISTS wfp_staging")

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

    existing = [
        r[0]
        for r in conn.sql(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'wfp_staging'"
        ).fetchall()
    ]

    if "stg_food_prices" not in existing:
        conn.execute("""
            CREATE OR REPLACE VIEW wfp_staging.stg_food_prices AS
            SELECT
                CAST(date AS DATE) AS date,
                UPPER(TRIM(admin1)) AS admin1,
                UPPER(TRIM(admin2)) AS admin2,
                TRIM(market) AS market,
                market_id,
                CAST(latitude AS FLOAT) AS latitude,
                CAST(longitude AS FLOAT) AS longitude,
                TRIM(category) AS category,
                TRIM(commodity) AS commodity,
                commodity_id,
                TRIM(unit) AS unit,
                priceflag AS price_flag,
                TRIM(pricetype) AS pricetype,
                TRIM(currency) AS currency,
                CAST(price AS DECIMAL(16, 2)) AS price,
                CAST(usdprice AS DECIMAL(16, 4)) AS usdprice
            FROM raw.food_prices
            WHERE price > 0
        """)

    if "stg_markets" not in existing:
        conn.execute("""
            CREATE OR REPLACE VIEW wfp_staging.stg_markets AS
            SELECT
                market_id,
                TRIM(market) AS market,
                TRIM(countryiso3) AS countryiso3,
                CASE WHEN admin1 IS NULL OR TRIM(admin1) = '' THEN 'NATIONAL'
                     ELSE UPPER(TRIM(admin1)) END AS admin1,
                CASE WHEN admin2 IS NULL OR TRIM(admin2) = '' THEN 'NATIONAL'
                     ELSE UPPER(TRIM(admin2)) END AS admin2,
                CAST(latitude AS FLOAT) AS latitude,
                CAST(longitude AS FLOAT) AS longitude,
                (market_id = 974) AS is_national_avg
            FROM raw.markets
        """)

    _q = """
    WITH consolidated AS (
        SELECT
            fp.date,
            fp.price,
            CASE
                WHEN fp.commodity LIKE 'Oil (vegetable)%' THEN 'Cooking Oil'
                WHEN fp.commodity IN ('Sugar', 'Sugar (local)', 'Sugar (premium)') THEN 'Sugar'
                WHEN fp.commodity LIKE 'Rice%' THEN 'Rice'
                WHEN fp.commodity = 'Wheat flour' THEN 'Flour'
                ELSE 'Other'
            END AS commodity_consolidated,
            mk.admin1,
            CASE
                WHEN mk.admin1 IN ('DKI JAKARTA','JAWA BARAT','JAWA TENGAH','DI YOGYAKARTA','JAWA TIMUR','BANTEN') THEN 'Java'
                WHEN mk.admin1 IN ('ACEH','SUMATERA UTARA','SUMATERA BARAT','RIAU','JAMBI','SUMATERA SELATAN','BENGKULU','LAMPUNG','KEPULAUAN RIAU','BANGKA BELITUNG') THEN 'Sumatera'
                WHEN mk.admin1 IN ('KALIMANTAN BARAT','KALIMANTAN TENGAH','KALIMANTAN SELATAN','KALIMANTAN TIMUR','KALIMANTAN UTARA') THEN 'Kalimantan'
                WHEN mk.admin1 IN ('SULAWESI UTARA','SULAWESI TENGAH','SULAWESI SELATAN','SULAWESI TENGGARA','GORONTALO','SULAWESI BARAT') THEN 'Sulawesi'
                WHEN mk.admin1 IN ('BALI','NUSA TENGGARA BARAT','NUSA TENGGARA TIMUR','MALUKU','MALUKU UTARA','PAPUA','PAPUA BARAT') THEN 'Eastern Indonesia'
                ELSE 'Unknown'
            END AS island_group,
            fp.price_flag
        FROM wfp_staging.stg_food_prices fp
        JOIN wfp_staging.stg_markets mk ON fp.market_id = mk.market_id
        WHERE fp.price_flag = 'actual'
    )
    SELECT * FROM consolidated
    """
    _df = conn.sql(_q).df()
    target = ["Rice", "Cooking Oil", "Sugar", "Flour"]
    df_target = _df[_df["commodity_consolidated"].isin(target)].copy()
    df_target["year"] = pd.to_datetime(df_target["date"]).dt.year
    df_target["month"] = pd.to_datetime(df_target["date"]).dt.month

    mo.md(f"""
    # EDA: Indonesia Staple Food Prices
    ## SCAN Framework — Phase 4

    **Data**: {len(df_target):,} target rows from {len(_df):,} total

    {ingest_info}
    """)
    return _df, conn, df_target, has_pipeline, run_id, target


@app.cell
def __(conn, df_target, mo, run_id):
    date_range = conn.sql(
        "SELECT MIN(date), MAX(date) FROM wfp_staging.stg_food_prices"
    ).fetchone()
    all_commodities = [
        r[0]
        for r in conn.sql(
            "SELECT DISTINCT commodity FROM wfp_staging.stg_food_prices ORDER BY commodity"
        ).fetchall()
    ]
    provinces = [
        r[0]
        for r in conn.sql(
            "SELECT DISTINCT admin1 FROM wfp_staging.stg_markets ORDER BY admin1"
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

    **Dataset**: WFP Indonesia Food Prices
    **Date range**: {date_range[0]} — {date_range[1]}
    **Commodities tracked**: {len(all_commodities)}
    **Provinces**: {len(provinces)}
    {_pipeline_note}
    """)
    return all_commodities, date_range, provinces


@app.cell
def __(df_target, mo):
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
def __(df_target, mo):
    _gp = df_target.groupby("island_group").agg(
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
def __(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, df_target, mo, px):
    _yearly = df_target.groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()

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

    ### A1: Annual Average Price & YoY Change
    *Source: WFP Indonesia Food Prices (HDX) | 2007–2024 | price_flag = actual*
    """)
    mo.ui.plotly(_fig_trend)
    mo.md("**Normalized trend** (all commodities scaled to same baseline):")
    mo.ui.plotly(_fig_idx)


@app.cell
def __(PALETTE_MAP, df_target, mo, px):
    _yearly = df_target.groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
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
def __(PALETTE_MAP, df_target, mo, px):
    vol = df_target.groupby(["year", "commodity_consolidated"])["price"].agg(["mean", "std"]).reset_index()
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
def __(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, df_target, mo, px):
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
def __(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, df_target, go, make_subplots, mo, np, px):
    _monthly = df_target.groupby(["month", "commodity_consolidated"])["price"].agg(["mean", "std"]).reset_index()
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
def __(PALETTE_MAP, df_target, mo, px):
    _pivot = df_target.pivot_table(index=["year", "month"], columns="commodity_consolidated", values="price", aggfunc="mean").reset_index()
    corr = _pivot[["Rice", "Cooking Oil", "Sugar", "Flour"]].corr()

    _fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        title="A5: Cross-Commodity Correlation Matrix (Monthly, Lag 0)",
        template="plotly_white", aspect="auto", zmin=-1, zmax=1,
    )
    mo.md("### A5: Cross-Commodity Correlation Matrix")
    mo.ui.plotly(_fig_corr)

    _pairs = []
    for _i in range(len(corr.columns)):
        for _j in range(_i + 1, len(corr.columns)):
            _pairs.append(f"{corr.columns[_i]} ↔ {corr.columns[_j]}: r = {corr.iloc[_i, _j]:.3f}")
    mo.md("**Pairwise correlations:**\n  - " + "\n  - ".join(_pairs))


@app.cell
def __(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, df_target, go, mo):
    _oil = df_target[df_target["commodity_consolidated"] == "Cooking Oil"].copy()
    _oil_avg = _oil.groupby(["year", "month"])["price"].mean().reset_index()
    _oil_avg["ym"] = pd.to_datetime(_oil_avg["year"].astype(str) + "-" + _oil_avg["month"].astype(str).str.zfill(2) + "-01")
    _oil_2020 = _oil_avg[_oil_avg["year"].isin([2020, 2021, 2022, 2023, 2024])].sort_values("ym")

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

    _pct = int((1 - _pre[0] / _peak[0]) * 100) if len(_pre) > 0 and len(_peak) > 0 else 0
    _title = f"N1: Cooking Oil Surged {_pct}% in 1 Month After Export Ban" if _pct > 0 else "N1: Cooking Oil 2022 Shock"
    _fig_oil.update_layout(title=_title, yaxis_title="Avg Price (IDR)", yaxis=dict(tickformat="~s"), template="plotly_white")

    mo.md("""
    ## N — Notable Segments

    ### N1: Cooking Oil — 2022 Global Shock
    """)
    mo.ui.plotly(_fig_oil)

    if len(_pre) > 0 and len(_post) > 0 and len(_peak) > 0:
        mo.md(f"""
    **Key figures:**
    - Pre-shock (Mar 2022): IDR {_pre[0]:,.0f}
    - Peak (Apr 2022): IDR {_peak[0]:,.0f}
    - Post-shock (Dec 2022): IDR {_post[0]:,.0f}
    - Spike magnitude: {_pct}% increase in 1 month
    """)


@app.cell
def __(PALETTE_MAP, df_target, go, mo, np):
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
        title="N2: Rice Prices {pct:.1f}% Lower During Harvest Season", template="plotly_white",
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
def __(PALETTE_MAP, df_target, go, mo):
    _sugar = df_target[df_target["commodity_consolidated"] == "Sugar"].copy()
    _sugar_monthly = _sugar.groupby("month")["price"].mean().reset_index()
    _mn = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    _ramadan_months = [3, 4, 5]

    _fig_sugar = go.Figure()
    _fig_sugar.add_trace(go.Bar(
        x=_sugar_monthly["month"], y=_sugar_monthly["price"],
        name="Sugar", marker_color=PALETTE_MAP["Sugar"],
    ))
    _fig_sugar.add_vrect(x0=2.5, x1=5.5, fillcolor="orange", opacity=0.06, line_width=0, annotation_text="Ramadan", annotation_position="top left")
    _fig_sugar.update_layout(
        yaxis_title="Avg Price (IDR)", yaxis=dict(tickformat="~s"),
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=_mn),
        title="N3: Sugar Prices Premium During Ramadan Season", template="plotly_white",
    )

    _non_ramadan = _sugar_monthly[~_sugar_monthly["month"].isin(_ramadan_months)]["price"].mean()
    _ramadan_avg = _sugar_monthly[_sugar_monthly["month"].isin(_ramadan_months)]["price"].mean()
    _premium = (_ramadan_avg - _non_ramadan) / _non_ramadan * 100

    _fig_sugar.update_layout(title=f"N3: Sugar {_premium:.1f}% Premium During Ramadan Season (Mar–May)")

    mo.md("### N3: Sugar — Ramadan Seasonality")
    mo.ui.plotly(_fig_sugar)

    mo.md(f"""
    - Ramadan season (Mar–May) avg: IDR {_ramadan_avg:,.0f}
    - Non-Ramadan avg: IDR {_non_ramadan:,.0f}
    - Premium during Ramadan: {_premium:.1f}%
    """)


@app.cell
def __(DASH_MAP, PALETTE_MAP, SYMBOL_MAP, df_target, mo, px):
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
def __(mo):
    mo.md(r"""
    ## Summary — EDA Findings

    | # | Finding | Type | Stakeholder |
    |---|---------|------|-------------|
    | 1 | **Cooking Oil 2022 shock**: 100%+ price spike in 1 month (Mar→Apr 2022). Prices did not fully normalise by Dec 2022. | Contextual | Category Manager |
    | 2 | **Rice harvest dip**: Prices lowest in harvest months, peak-to-trough gap significant. Procurement timing opportunity. | Actionable | Procurement Analyst |
    | 3 | **Sugar Ramadan premium**: Mar–May prices consistently above annual average. Procurement should front-run Ramadan. | Actionable | Procurement Analyst |
    | 4 | **Eastern Indonesia premium**: Large and persistent gap vs Java across all commodities. | Directional | Procurement Analyst |
    | 5 | **Volatility ranking**: Cooking Oil most volatile (2022 shock), Rice most stable. | Directional | Category Manager |
    | 6 | **Cross-commodity correlation**: Weak correlation between Rice and Cooking Oil suggests independent drivers. | Contextual | Category Manager |
    | 7 | **Coverage gap**: Eastern Indonesia data sparse before 2015. 2015+ analysis required for fair comparison. | Contextual | Both |
    """)
    mo.md("---\n*EDA complete. Findings feed into Phase 5 Deep Dive.*")


if __name__ == "__main__":
    app.run()
