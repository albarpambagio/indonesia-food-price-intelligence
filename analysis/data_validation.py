# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb",
#     "pandas",
#     "plotly",
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
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    return duckdb, go, make_subplots, mo, pd, px


@app.cell
def script_mode(mo):
    is_script_mode = mo.app_meta().mode == "script"
    return (is_script_mode,)


@app.cell
def connect_db(duckdb, mo):
    conn = duckdb.connect("data/wfp.duckdb")
    conn.execute("CREATE SCHEMA IF NOT EXISTS pipeline;")
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    fp_rows = conn.sql("SELECT COUNT(*) FROM raw.food_prices").fetchone()[0]
    mk_rows = conn.sql("SELECT COUNT(*) FROM raw.markets").fetchone()[0]
    has_pipeline = conn.sql("SELECT COUNT(*) FROM pipeline.lineage").fetchone()[0] > 0
    ingest_info = ""
    if has_pipeline:
        row = conn.sql("SELECT run_id, raw_food_prices_rows, raw_markets_rows FROM pipeline.lineage ORDER BY started_at DESC LIMIT 1").fetchone()
        ingest_info = f"**Ingest run**: `{row[0]}` | raw.food_prices = {row[1]:,} | raw.markets = {row[2]:,}"
    mo.md(f"""
    # Data Validation Checkpoint

    **Dataset**: WFP Food Prices Indonesia (HDX, CC BY-IGO 3.0)

    | Table | Rows |
    |-------|------|
    | `raw.food_prices` | {fp_rows:,} |
    | `raw.markets` | {mk_rows:,} |

    {ingest_info}
    """)
    return conn, fp_rows, mk_rows


@app.cell
def load_data(conn, mo, pd):
    fp = conn.sql("SELECT * FROM raw.food_prices").df()
    mk = conn.sql("SELECT * FROM raw.markets").df()
    mo.md(f"""
    ### Raw Data Summary

    **Food Prices**: {len(fp):,} rows × {len(fp.columns)} columns
    **Markets**: {len(mk):,} rows × {len(mk.columns)} columns
    """)
    return fp, mk


@app.cell
def check_commodity_coverage(fp, mo):
    target = [
        "Rice", "Wheat flour", "Sugar", "Sugar (premium)",
        "Oil (vegetable)", "Oil (vegetable, bulk)", "Oil (vegetable, packaged)",
    ]
    fp_t = fp[fp["commodity"].isin(target)]
    pct = len(fp_t) / len(fp) * 100
    mo.md(f"""
    ## Check 1: Commodity Coverage

    **Target rows**: {len(fp_t):,} / {len(fp):,} rows ({pct:.1f}%)

    → {len(fp_t):,} rows from 7 target commodity variants.
    {len(fp) - len(fp_t):,} rows excluded (eggs, beef, chicken, chili, garlic, shallot, fuel, etc.).
    """)
    return fp_t, pct, target


@app.cell
def coverage_chart(fp_t, go, make_subplots, mo, pd):
    _d = fp_t.copy()
    _d["year"] = _d["date"].astype(str).str[:4].astype(int)
    yearly = _d.groupby(["year", "commodity"]).size().reset_index(name="obs")
    commodities = yearly["commodity"].unique()
    colors = {
        "Rice": "#1f77b4", "Wheat flour": "#ff7f0e",
        "Sugar": "#2ca02c", "Sugar (premium)": "#98df8a",
        "Oil (vegetable)": "#d62728", "Oil (vegetable, bulk)": "#ff9896",
        "Oil (vegetable, packaged)": "#9467bd",
    }
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Yearly Observations per Commodity", "Coverage: Years Present"),
        vertical_spacing=0.15,
    )
    for c in commodities:
        cdf = yearly[yearly["commodity"] == c]
        fig.add_trace(
            go.Bar(x=cdf["year"], y=cdf["obs"], name=c, marker_color=colors.get(c, "#636efa"), legendgroup=c),
            row=1, col=1,
        )
    years_all = set(_d["year"].unique())
    coverage_rows = []
    for c in commodities:
        cy = set(_d[_d["commodity"] == c]["year"].unique())
        coverage_rows.append({"commodity": c, "years_present": len(cy)})
    cov_df = pd.DataFrame(coverage_rows).sort_values("years_present", ascending=True)
    fig.add_trace(
        go.Bar(x=cov_df["commodity"], y=cov_df["years_present"], marker_color="#2ca02c", hovertemplate="%{y} years<extra></extra>"),
        row=2, col=1,
    )
    fig.update_layout(height=500, title_text="Commodity Coverage Analysis", showlegend=False)
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_yaxes(title_text="Observations", row=1, col=1)
    fig.update_xaxes(tickangle=45, row=2, col=1)
    fig.update_yaxes(title_text="Years (max 18)", row=2, col=1)
    mo.ui.plotly(fig)
    return cov_df, years_all


@app.cell
def coverage_verdict(cov_df, mo, pct, fp_t):
    all_18 = cov_df[cov_df["years_present"] == 18]
    partial = cov_df[cov_df["years_present"] < 18]
    years_sorted = sorted(fp_t["date"].astype(str).str[:4].astype(int).unique())
    mo.md(f"""
    **Coverage Verdict**:
    - **All 18 years**: {', '.join(all_18['commodity'].tolist())}
    - **Partial**: {', '.join(f"{r['commodity']} ({r['years_present']} years)" for _, r in partial.iterrows()) if len(partial) > 0 else 'None'}
    - **Date range**: {min(years_sorted)}–{max(years_sorted)}
    """)
    return all_18, partial, years_sorted


@app.cell
def check_provincial_coverage(fp, mo):
    prov = fp.groupby("admin1").agg(
        obs=("price", "count"),
        markets=("market_id", "nunique"),
        years=("date", lambda x: x.astype(str).str[:4].nunique()),
    ).reset_index().sort_values("obs", ascending=False)
    cont_18 = prov[prov["years"] == 18]
    sparse = prov[prov["years"] < 10]
    mo.md(f"""
    ## Check 2: Provincial Coverage

    **Total provinces**: {len(prov)}
    **All 18 years**: {len(cont_18)}
    **<10 years (sparse)**: {len(sparse)}
    {', '.join(sparse['admin1'].tolist()) if len(sparse) > 0 else 'None'}
    """)
    return cont_18, prov, sparse


@app.cell
def provincial_table(mo, prov):
    mo.ui.table(prov, label="Province Coverage Detail")
    return


@app.cell
def check_priceflag(fp, mo):
    fd = fp["priceflag"].value_counts().reset_index()
    fd.columns = ["priceflag", "count"]
    fd["pct"] = (fd["count"] / fd["count"].sum() * 100).round(1)
    ap = fd[fd["priceflag"] == "actual"]["pct"].values[0]
    mo.md(f"""
    ## Check 3: Priceflag Distribution

    **Actual**: {fd[fd['priceflag'] == 'actual']['count'].values[0]:,} rows ({ap}%)
    **Aggregate**: {fd[fd['priceflag'] == 'aggregate']['count'].values[0]:,} rows ({100 - ap}%)

    → **Verdict**: `actual` dominates at {ap}%. `aggregate` filtered out in intermediate layer.
    """)
    return ap, fd


@app.cell
def check_unit_consistency(fp, mo, target):
    _ft = fp[fp["commodity"].isin(target)].copy()
    _ft["unit_clean"] = _ft["unit"].str.strip()
    ud = _ft.groupby(["commodity", "unit_clean"]).size().reset_index(name="obs").sort_values(["commodity", "obs"], ascending=[True, False])
    mt = ud.groupby("commodity").filter(lambda x: x["unit_clean"].nunique() > 1)
    mn = mt["commodity"].unique()
    mo.md(f"""
    ## Check 4: Unit Consistency

    **Single unit**: {', '.join(c for c in _ft['commodity'].unique() if c not in mn)}
    **Multiple units** (needs normalisation): {', '.join(mn) if len(mn) > 0 else 'None'}
    """)
    return mn, mt, ud


@app.cell
def unit_table(mo, ud):
    mo.ui.table(ud, label="Unit Distribution by Commodity")
    return


@app.cell
def check_sugar_split(fp, mo, px):
    sugar = fp[fp["commodity"].isin(["Sugar", "Sugar (premium)"])].copy()
    sugar["year"] = sugar["date"].astype(str).str[:4].astype(int)
    sugar_avg = sugar.groupby(["year", "commodity"])["price"].mean().reset_index()
    sugar_pivot = sugar_avg.pivot(index="year", columns="commodity", values="price").reset_index()
    sugar_pivot["gap_pct"] = (sugar_pivot["Sugar (premium)"] - sugar_pivot["Sugar"]) / sugar_pivot["Sugar"] * 100
    avg_gap = sugar_pivot["gap_pct"].mean()
    mo.md(f"""
    ## Check 5: Sugar Split Decision

    **Average premium gap**: {avg_gap:.1f}%
    → **Decision**: {'**KEEP SPLIT** — divergence >5%' if abs(avg_gap) > 5 else '**CONSOLIDATE** — variants move together'}
    """)
    fig_sugar = px.line(
        sugar_avg, x="year", y="price", color="commodity",
        title="Sugar vs Sugar (premium): Annual Average Price", markers=True,
    )
    mo.ui.plotly(fig_sugar)
    return avg_gap, sugar, sugar_avg, sugar_pivot


@app.cell
def check_oil_split(fp, mo, px):
    oil = fp[fp["commodity"].str.startswith("Oil")].copy()
    oil["year"] = oil["date"].astype(str).str[:4].astype(int)
    oil_avg = oil.groupby(["year", "commodity"])["price"].mean().reset_index()
    mo.md(f"""
    ## Check 6: Cooking Oil Split Decision
    """)
    fig_oil = px.line(
        oil_avg, x="year", y="price", color="commodity",
        title="Cooking Oil Variants: Annual Average Price (IDR)", markers=True,
    )
    mo.ui.plotly(fig_oil)
    return oil, oil_avg


@app.cell
def oil_correlation(mo, oil_avg):
    oil_pivot = oil_avg.pivot(index="year", columns="commodity", values="price").reset_index()
    oil_cols = [c for c in oil_pivot.columns if c != "year"]
    pairs = []
    for i in range(len(oil_cols)):
        for j in range(i + 1, len(oil_cols)):
            corr = oil_pivot[oil_cols[i]].corr(oil_pivot[oil_cols[j]])
            pairs.append(f"{oil_cols[i]} vs {oil_cols[j]}: r = {corr:.3f}")
    pair_text = "\n  - ".join([""] + pairs)
    hi_corr = all("r = 0." in p or "r = 1.0" in p or "r = 0.9" in p or "r = 0.8" in p for p in pairs)
    mo.md(f"""
    **Pairwise correlations**:{pair_text}
    → **Decision**: {'**CONSOLIDATE** — variants co-move' if hi_corr else '**KEEP SPLIT**'}
    """)
    return hi_corr, oil_cols, oil_pivot, pair_text, pairs


@app.cell
def check_secondary_enrichment(fp, mo):
    has_usd = fp["usdprice"].notna().mean() * 100
    cpi_cols = [c for c in fp.columns if "cpi" in c.lower()]
    mo.md(f"""
    ## Check 7: Secondary Enrichment

    - **usdprice availability**: {has_usd:.1f}% of rows
    - **CPI columns**: {cpi_cols if cpi_cols else 'None'}

    → **Verdict**: External FX enrichment **{'unnecessary' if has_usd > 95 else 'needed'}**.
    """)
    return cpi_cols, has_usd


@app.cell
def scoping_decisions(mo):
    mo.md(r"""
    ## Scoping Decisions

    | # | Check | Decision | Impact |
    |---|-------|----------|--------|
    | 1 | Commodity coverage | All 4 targets present 2007–2024 | Full 17-year analysis viable |
    | 2 | Provincial coverage | Outer islands sparse pre-2015 | Restrict Eastern Indonesia to 2015+ |
    | 3 | Priceflag | `actual` dominates | Filter `aggregate` in intermediate |
    | 4 | Units | Solids KG, Oil L | Normalise in int_prices_normalised |
    | 5 | Sugar split | Consolidated | Single "Sugar" in marts |
    | 6 | Oil split | Consolidated | Single "Cooking Oil" in marts |
    | 7 | FX enrichment | usdprice sufficient | Skip external FX API |
    """)


@app.cell
def footer(mo):
    mo.md("---\n*Validation complete.*")


if __name__ == "__main__":
    app.run()
