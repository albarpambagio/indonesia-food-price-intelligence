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
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import calendar
    return calendar, duckdb, go, make_subplots, mo, pd, px


@app.cell
def __(duckdb, mo):
    conn = duckdb.connect("data/wfp.duckdb")
    conn.execute("CREATE SCHEMA IF NOT EXISTS wfp_staging")
    conn.execute(
        """
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
        FROM read_csv_auto('data/raw/wfp_food_prices_idn.csv')
        WHERE price > 0
        """
    )
    conn.execute(
        """
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
        FROM read_csv_auto('data/raw/wfp_markets_idn.csv')
        """
    )
    mo.md("**DuckDB connected** — staging views loaded from CSV.")
    return conn,


@app.cell
def __(conn, mo):
    fp = conn.sql("SELECT * FROM wfp_staging.stg_food_prices").df()
    mk = conn.sql("SELECT * FROM wfp_staging.stg_markets").df()
    mo.md(f"""
    # EDA: Indonesia Staple Food Prices
    ## SCAN Framework — Phase 4

    **Data loaded**: {len(fp):,} price rows, {len(mk):,} markets.
    """)
    return fp, mk


@app.cell
def __(conn, mo):
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
    """)
    return all_commodities, date_range, provinces


@app.cell
def __(conn, mo, pd):
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
    ## C — Coverage Gaps

    **Target commodities**: {len(df_target):,} / {len(_df):,} rows ({len(df_target)/len(_df)*100:.1f}%)
    **Non-target excluded**: {len(_df) - len(df_target):,} rows (eggs, beef, chicken, chili, garlic, shallot, fuel, etc.)

    **Coverage by commodity:**
    """)
    coverage = df_target.groupby("commodity_consolidated").agg(
        rows=("price", "count"),
        years=("year", "nunique"),
        markets=("admin1", "nunique"),
        min_year=("year", "min"),
        max_year=("year", "max"),
    ).reset_index()
    mo.ui.table(coverage, label="Target Commodity Coverage")
    return _df, df_target, coverage, target


@app.cell
def __(mo, df_target):
    _gp = df_target.groupby("island_group").agg(
        rows=("price", "count"),
        provinces=("admin1", "nunique"),
        years=("year", "nunique"),
        min_year=("year", "min"),
        max_year=("year", "max"),
    ).reset_index().sort_values("rows", ascending=False)
    mo.md("### Coverage by Island Group")
    _east = _gp[_gp["island_group"] == "Eastern Indonesia"].iloc[0]
    mo.md(f"""
    **Eastern Indonesia**: {_east['rows']:,} rows, {_east['provinces']} provinces, {_east['min_year']}–{_east['max_year']}
    → **Gap**: Eastern Indonesia coverage sparse before 2015. Analysis restricted to 2015+ where needed.
    """)
    mo.ui.table(_gp, label="Island Group Coverage")


@app.cell
def __(mo, px, df_target):
    _yearly = df_target.groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _fig_trend = px.line(
        _yearly, x="year", y="price", color="commodity_consolidated",
        title="A1: Annual Average Price (IDR) — 4 Staple Commodities",
        markers=True, template="plotly_white",
    )
    _fig_trend.update_layout(yaxis_title="Avg Price (IDR)", xaxis=dict(dtick=1))
    mo.md("""
    ## A — Aggregates

    ### A1: Annual Average Price & YoY Change
    """)
    mo.ui.plotly(_fig_trend)


@app.cell
def __(mo, df_target):
    _yearly = df_target.groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _yearly["yoy_pct"] = _yearly.groupby("commodity_consolidated")["price"].pct_change() * 100
    _pivot = _yearly.pivot_table(index="year", columns="commodity_consolidated", values="yoy_pct").reset_index()
    _pivot = _pivot.round(1)
    mo.md("**Year-over-Year % Change Table**")
    mo.ui.table(_pivot.fillna("").astype(str), label="YoY% Change by Commodity")


@app.cell
def __(mo, px, df_target):
    vol = df_target.groupby(["year", "commodity_consolidated"])["price"].agg(["mean", "std"]).reset_index()
    vol["cv"] = (vol["std"] / vol["mean"]) * 100
    _fig_vol = px.line(
        vol, x="year", y="cv", color="commodity_consolidated",
        title="A2: Price Volatility (CV%) — Std Dev / Mean × 100",
        markers=True, template="plotly_white",
    )
    _fig_vol.update_layout(yaxis_title="Coefficient of Variation (%)", xaxis=dict(dtick=1))
    mo.md("### A2: Price Volatility (CV%)")
    mo.ui.plotly(_fig_vol)
    _avg_cv = vol.groupby("commodity_consolidated")["cv"].mean().reset_index().sort_values("cv", ascending=False)
    mo.md("**Average CV% (all years)**")
    mo.ui.table(_avg_cv.round(1), label="Average Volatility by Commodity")


@app.cell
def __(mo, px, df_target):
    _java_avg = df_target[df_target["island_group"] == "Java"].groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _java_avg.columns = ["year", "commodity_consolidated", "java_price"]
    _island_avg = df_target.groupby(["year", "commodity_consolidated", "island_group"])["price"].mean().reset_index()
    _index = _island_avg.merge(_java_avg, on=["year", "commodity_consolidated"], how="left")
    _index["price_index"] = (_index["price"] / _index["java_price"]) * 100
    _index = _index[_index["island_group"] != "Java"]
    _fig_index = px.line(
        _index, x="year", y="price_index", color="island_group",
        facet_col="commodity_consolidated", facet_col_wrap=2,
        title="A3: Island Group Price Index (Java = 100)",
        markers=True, template="plotly_white",
    )
    _fig_index.update_layout(yaxis_title="Price Index (Java=100)")
    _fig_index.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.5)
    mo.md("### A3: Island Group Price Index vs Java")
    mo.ui.plotly(_fig_index)


@app.cell
def __(mo, px, df_target):
    _monthly = df_target.groupby(["month", "commodity_consolidated"])["price"].mean().reset_index()
    _fig_seasonal = px.line(
        _monthly, x="month", y="price", color="commodity_consolidated",
        title="A4: Month-of-Year Average Price (All Years Pooled)",
        markers=True, template="plotly_white",
    )
    _fig_seasonal.update_layout(
        yaxis_title="Avg Price (IDR)",
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]),
    )
    mo.md("### A4: Month-of-Year Seasonality")
    mo.ui.plotly(_fig_seasonal)


@app.cell
def __(mo, px, df_target):
    _pivot = df_target.pivot_table(index=["year", "month"], columns="commodity_consolidated", values="price", aggfunc="mean").reset_index()
    corr = _pivot[["Rice", "Cooking Oil", "Sugar", "Flour"]].corr()
    _fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        title="A5: Cross-Commodity Correlation Matrix (Monthly, Lag 0)",
        template="plotly_white", aspect="auto",
    )
    mo.md("### A5: Cross-Commodity Correlation Matrix")
    mo.ui.plotly(_fig_corr)
    _pairs = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            _pairs.append(f"{corr.columns[i]} ↔ {corr.columns[j]}: r = {corr.iloc[i, j]:.3f}")
    mo.md("**Pairwise correlations:**\n  - " + "\n  - ".join(_pairs))


@app.cell
def __(mo, px, df_target):
    _oil = df_target[df_target["commodity_consolidated"] == "Cooking Oil"].copy()
    _oil_avg = _oil.groupby(["year", "month"])["price"].mean().reset_index()
    _oil_avg["ym"] = _oil_avg["year"].astype(str) + "-" + _oil_avg["month"].astype(str).str.zfill(2)
    _oil_avg = _oil_avg.sort_values("year").reset_index(drop=True)
    _oil_2020 = _oil_avg[_oil_avg["year"].isin([2020, 2021, 2022, 2023, 2024])]
    _fig_oil = px.line(
        _oil_2020, x="ym", y="price",
        title="N1: Cooking Oil 2022 Shock — Monthly Price",
        markers=True, template="plotly_white",
    )
    _fig_oil.add_vline(x="2022-03", line_dash="dash", line_color="red", opacity=0.5)
    _fig_oil.add_vline(x="2022-05", line_dash="dash", line_color="orange", opacity=0.5)
    _fig_oil.update_layout(yaxis_title="Avg Price (IDR)", xaxis_tickangle=45)
    mo.md("""
    ## N — Notable Segments

    ### N1: Cooking Oil — 2022 Global Shock
    """)
    mo.ui.plotly(_fig_oil)
    _pre = _oil_avg[_oil_avg["ym"] == "2022-03"]["price"].values
    _post = _oil_avg[_oil_avg["ym"] == "2022-12"]["price"].values
    _peak = _oil_avg[_oil_avg["ym"] == "2022-04"]["price"].values
    if len(_pre) > 0 and len(_post) > 0 and len(_peak) > 0:
        mo.md(f"""
    **Key figures:**
    - Pre-shock (Mar 2022): IDR {_pre[0]:,.0f}
    - Peak (Apr 2022): IDR {_peak[0]:,.0f}
    - Post-shock (Dec 2022): IDR {_post[0]:,.0f}
    - Spike magnitude: {(1 - _pre[0] / _peak[0]) * 100:.0f}% increase in 1 month
    """)
    else:
        mo.md("**Insufficient data for 2022 window.**")


@app.cell
def __(mo, px, df_target):
    _rice = df_target[df_target["commodity_consolidated"] == "Rice"].copy()
    _rice_monthly = _rice.groupby("month")["price"].mean().reset_index()
    _fig_rice = px.bar(
        _rice_monthly, x="month", y="price",
        title="N2: Rice Harvest Seasonality — Average Price by Month",
        template="plotly_white",
        color="price", color_continuous_scale="Greens",
    )
    _fig_rice.update_layout(
        yaxis_title="Avg Price (IDR)",
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]),
    )
    mo.md("### N2: Rice — Harvest Cycle Seasonality")
    mo.ui.plotly(_fig_rice)
    _min_m = _rice_monthly.loc[_rice_monthly["price"].idxmin()]
    _max_m = _rice_monthly.loc[_rice_monthly["price"].idxmax()]
    mo.md(f"""
    **Rice seasonality:**
    - Lowest price month: {_min_m['month']} (IDR {_min_m['price']:,.0f})
    - Highest price month: {_max_m['month']} (IDR {_max_m['price']:,.0f})
    - Peak-to-trough gap: {(_max_m['price'] - _min_m['price']) / _min_m['price'] * 100:.1f}%
    """)


@app.cell
def __(mo, px, df_target):
    _sugar = df_target[df_target["commodity_consolidated"] == "Sugar"].copy()
    _sugar_monthly = _sugar.groupby("month")["price"].mean().reset_index()
    _fig_sugar = px.bar(
        _sugar_monthly, x="month", y="price",
        title="N3: Sugar — Ramadan Effect (Month-of-Year Average)",
        template="plotly_white",
        color="price", color_continuous_scale="Oranges",
    )
    _fig_sugar.update_layout(
        yaxis_title="Avg Price (IDR)",
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]),
    )
    mo.md("### N3: Sugar — Ramadan Seasonality")
    mo.ui.plotly(_fig_sugar)
    _ramadan_months = [3, 4, 5]
    _non_ramadan = _sugar_monthly[~_sugar_monthly["month"].isin(_ramadan_months)]["price"].mean()
    _ramadan_avg = _sugar_monthly[_sugar_monthly["month"].isin(_ramadan_months)]["price"].mean()
    mo.md(f"""
    **Sugar — Ramadan pattern:**
    - Ramadan season (Mar–May) avg: IDR {_ramadan_avg:,.0f}
    - Non-Ramadan avg: IDR {_non_ramadan:,.0f}
    - Premium during Ramadan: {(_ramadan_avg - _non_ramadan) / _non_ramadan * 100:.1f}%
    """)


@app.cell
def __(mo, px, df_target):
    _east = df_target[df_target["island_group"] == "Eastern Indonesia"].groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _java = df_target[df_target["island_group"] == "Java"].groupby(["year", "commodity_consolidated"])["price"].mean().reset_index()
    _east.columns = ["year", "commodity_consolidated", "east_price"]
    _java.columns = ["year", "commodity_consolidated", "java_price"]
    _gap = _east.merge(_java, on=["year", "commodity_consolidated"])
    _gap["premium_pct"] = (_gap["east_price"] - _gap["java_price"]) / _gap["java_price"] * 100
    _gap = _gap[_gap["year"] >= 2015]
    _fig_east = px.line(
        _gap, x="year", y="premium_pct", color="commodity_consolidated",
        title="N4: Eastern Indonesia — Price Premium vs Java (2015+)",
        markers=True, template="plotly_white",
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
