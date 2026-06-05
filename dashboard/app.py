# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.0",
#     "pandas>=2.2.0",
#     "plotly>=6.7.0",
#     "numpy>=1.26.0",
# ]
# ///

import marimo

__generated_with = "0.23.7"
app = marimo.App(width="full")


@app.cell
def setup():
    import sys
    from pathlib import Path

    _project_root = Path(__file__).resolve().parent.parent
    if str(_project_root) not in sys.path:
        sys.path.insert(0, str(_project_root))

    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    from dashboard.charts.action_cards import action_cards
    from dashboard.charts.correlation_charts import (
        correlation_heatmap,
        pair_scatter,
        pre_post_comparison_table,
        rolling_correlation,
    )
    from dashboard.charts.geo_charts import (
        geo_choropleth,
        geo_comparison_scatter,
        geo_province_table,
    )
    from dashboard.charts.harvest_chart import harvest_chart
    from dashboard.charts.kpi_sparklines import kpi_sparklines
    from dashboard.charts.ramadan_overlay import ramadan_overlay
    from dashboard.charts.seasonal_heatmap import seasonal_heatmap
    from dashboard.charts.seasonal_summary_table import seasonal_summary_table
    from dashboard.charts.signal_badges import signal_badges
    from dashboard.charts.trend_forecast import trend_forecast
    from dashboard.charts.yearend_chart import yearend_chart
    from dashboard.charts.yoy_bar import yoy_bar
    from dashboard.data_access import (
        compute_action_windows,
        compute_heatmap_matrix,
        compute_ramadan_overlay,
        compute_yoy_delta,
        get_latest_prices,
    )
    from dashboard.data_static import load_json

    COMMODITIES = ["All", "Rice", "Cooking Oil", "Sugar", "Flour"]
    ISLAND_GROUPS = ["All", "Java", "Sumatera", "Kalimantan", "Sulawesi", "Eastern Indonesia"]

    return (
        mo, pd, px, go,
        load_json,
        compute_action_windows, compute_heatmap_matrix, compute_ramadan_overlay,
        compute_yoy_delta, get_latest_prices,
        trend_forecast, kpi_sparklines, yoy_bar, signal_badges,
        seasonal_heatmap, ramadan_overlay, harvest_chart, yearend_chart,
        action_cards, seasonal_summary_table,
        geo_choropleth, geo_comparison_scatter, geo_province_table,
        correlation_heatmap, pair_scatter, rolling_correlation, pre_post_comparison_table,
        COMMODITIES, ISLAND_GROUPS,
    )


@app.cell
def load_data(load_json):
    price_trends = load_json("price_trends")
    price_trends_national = load_json("price_trends_national")
    forecast_raw = load_json("forecast", key="data")
    forecast_meta = load_json("forecast", key="metadata")
    seasonal_patterns = load_json("seasonal_patterns")
    geographic_disparity = load_json("geographic_disparity")
    commodity_correlation = load_json("commodity_correlation")
    correlation_summary = load_json("correlation_summary")

    return (
        price_trends, price_trends_national, forecast_raw, forecast_meta,
        seasonal_patterns, geographic_disparity, commodity_correlation, correlation_summary,
    )


@app.cell
def global_filters(mo, COMMODITIES, ISLAND_GROUPS):
    commodity = mo.ui.dropdown(
        options=COMMODITIES,
        value="All",
        label="Commodity",
    )
    island = mo.ui.dropdown(
        options=ISLAND_GROUPS,
        value="All",
        label="Island Group",
    )
    year_range = mo.ui.range_slider(
        start=2007,
        stop=2024,
        step=1,
        value=[2007, 2024],
        label="Year Range",
    )
    return commodity, island, year_range


@app.cell
def apply_filters(commodity, island, year_range,
                  price_trends_national, forecast_raw, correlation_summary,
                  geographic_disparity, commodity_correlation):
    def _filter_year(df, col="month"):
        if df.empty:
            return df
        lo, hi = year_range.value
        if col in df.columns:
            return df[(df[col].astype(str).str[:4].astype(int) >= lo) & (df[col].astype(str).str[:4].astype(int) <= hi)]
        if "year" in df.columns:
            return df[(df["year"] >= lo) & (df["year"] <= hi)]
        return df

    trends_nat = price_trends_national.copy()
    if commodity.value != "All":
        trends_nat = trends_nat[trends_nat["commodity_consolidated"] == commodity.value]
    trends_nat = _filter_year(trends_nat)

    forecast = forecast_raw.copy()
    if commodity.value != "All":
        forecast = forecast[forecast["commodity"] == commodity.value]

    geo = geographic_disparity.copy()
    if commodity.value != "All":
        geo = geo[geo["commodity_consolidated"] == commodity.value]
    if island.value != "All":
        geo = geo[geo["island_group"] == island.value]
    geo = _filter_year(geo, "year")

    corr_summary = correlation_summary.copy()

    pair_df = commodity_correlation.copy()
    pair_df = _filter_year(pair_df)

    return trends_nat, forecast, geo, corr_summary, pair_df


@app.cell
def tab_trends(mo, trends_nat, forecast, commodity,
               kpi_sparklines, trend_forecast, yoy_bar, signal_badges):
    _commodity_val = commodity.value
    _kpi_fig = kpi_sparklines(trends_nat, commodity_filter=_commodity_val)
    _trend_fig = trend_forecast(trends_nat, forecast, commodity_filter=_commodity_val)
    _yoy_fig = yoy_bar(trends_nat, commodity_filter=_commodity_val)
    _signal_fig = signal_badges(trends_nat, forecast, commodity_filter=_commodity_val)

    trends_content = mo.vstack([
        mo.md("## Price Trends & Forecast"),
        mo.md("Is now a good time to lock in bulk purchase contracts?"),
        mo.ui.plotly(_kpi_fig),
        mo.ui.plotly(_trend_fig),
        mo.ui.plotly(_yoy_fig),
        mo.ui.plotly(_signal_fig),
        mo.md(
            "> **Model Limitations:** Forecast uses AutoARIMA/AutoETS with 6-month horizon. "
            "95% confidence intervals widen at 5-6 months. "
            "Cooking Oil post-2022 structural break reduces reliability. "
            "No volume weighting \u2014 all markets equal weight."
        ),
    ], gap="1rem")

    return (trends_content,)


@app.cell
def seasonal_controls(mo):
    driver = mo.ui.radio(
        options=["All", "Ramadan", "Harvest", "Year-End"],
        value="All",
        label="Seasonal Driver",
    )
    return (driver,)


@app.cell
def tab_seasonal(mo, pd, trends_nat, commodity, driver,
                 seasonal_heatmap, ramadan_overlay, harvest_chart, yearend_chart,
                 action_cards, seasonal_summary_table):
    _commodity_val = commodity.value

    _islamic_cal = pd.DataFrame()

    _heatmap_fig = seasonal_heatmap(trends_nat, commodity_filter=_commodity_val)
    _ramadan_fig = ramadan_overlay(trends_nat, _islamic_cal, commodity_filter=_commodity_val, driver=driver.value)
    _harvest_fig = harvest_chart(trends_nat, commodity_filter=_commodity_val, driver=driver.value)
    _yearend_fig = yearend_chart(trends_nat, commodity_filter=_commodity_val, driver=driver.value)
    _cards_fig = action_cards(trends_nat, _islamic_cal, commodity_filter=_commodity_val, driver=driver.value)
    _summary_df = seasonal_summary_table(trends_nat, _islamic_cal, commodity_filter=_commodity_val)

    _seasonal_table = mo.ui.table(_summary_df) if not _summary_df.empty else mo.md("_No seasonal data available_")

    seasonal_content = mo.vstack([
        mo.md("## Seasonal Patterns"),
        mo.md("When should we increase stock for each commodity?"),
        driver,
        mo.ui.plotly(_cards_fig),
        mo.md(
            "> Seasonal analysis uses national-level data for Rice, Sugar, Flour. "
            "Island-level breakdown available for Cooking Oil only."
        ),
        mo.ui.plotly(_heatmap_fig),
        mo.ui.plotly(_ramadan_fig),
        mo.ui.plotly(_harvest_fig),
        mo.ui.plotly(_yearend_fig),
        _seasonal_table,
    ], gap="1rem")

    return (seasonal_content,)


@app.cell
def tab_geographic(mo, geo, commodity, island,
                   geo_choropleth, geo_comparison_scatter, geo_province_table):
    _commodity_val = commodity.value
    _island_val = island.value

    _geo_data = geo.copy()
    if _commodity_val != "All":
        _geo_data = _geo_data[_geo_data["commodity_consolidated"] == _commodity_val]
    if _island_val != "All":
        _geo_data = _geo_data[_geo_data["island_group"] == _island_val]

    _choropleth_fig = geo_choropleth(_geo_data)
    _comparison_fig = geo_comparison_scatter(_geo_data)
    _province_df = geo_province_table(_geo_data)

    _geo_table = mo.ui.table(_province_df) if not _province_df.empty else mo.md("_No geographic data available_")

    geo_content = mo.vstack([
        mo.md("## Geographic Disparity"),
        mo.md("Which island group offers the best sourcing price?"),
        mo.md(
            "> Geographic analysis is limited to Cooking Oil. Rice, Sugar, and Flour "
            "have no market-level actual prices in the WFP dataset."
        ),
        mo.ui.plotly(_choropleth_fig),
        mo.ui.plotly(_comparison_fig),
        mo.md("### Province Detail"),
        _geo_table,
    ], gap="1rem")

    return (geo_content,)


@app.cell
def signal_controls(mo):
    lag = mo.ui.radio(
        options=[0, 1, 2, 3],
        value=1,
        label="Lag (months)",
    )

    pair = mo.ui.dropdown(
        options=[
            "Rice \u2194 Oil",
            "Rice \u2194 Sugar",
            "Rice \u2194 Flour",
            "Oil \u2194 Sugar",
            "Oil \u2194 Flour",
            "Sugar \u2194 Flour",
        ],
        value="Rice \u2194 Oil",
        label="Commodity Pair",
    )

    return lag, pair


@app.cell
def tab_signals(mo, pair_df, corr_summary, lag, pair,
                correlation_heatmap, pair_scatter, rolling_correlation,
                pre_post_comparison_table):
    _pair_val = pair.value.lower().replace(" \u2194 ", "-")
    _corr_heatmap_fig = correlation_heatmap(corr_summary, lag=lag.value)
    _scatter_fig = pair_scatter(pair_df, _pair_val)
    _rolling_fig = rolling_correlation(pair_df, _pair_val)
    _comparison_df = pre_post_comparison_table(corr_summary)

    _strongest_row = None
    if not corr_summary.empty:
        _lag_df = corr_summary[corr_summary["lag_months"] == lag.value].copy()
        if not _lag_df.empty:
            _lag_df["abs_r"] = _lag_df["pearson_r"].abs()
            _strongest_row = _lag_df.nlargest(1, "abs_r").iloc[0]

    if _strongest_row is not None:
        _pair_label = _strongest_row["commodity_pair"].replace("-", " \u2194 ").title()
        _r_val = _strongest_row["pearson_r"]
        implication = (
            f"The strongest leading relationship at {lag.value}-month lag is "
            f"{_pair_label} (r = {_r_val:.3f}). "
            f"Procurement teams should monitor this pair as an early warning signal."
        )
    else:
        implication = ""

    signals_content = mo.vstack([
        mo.md("## Commodity Signals"),
        mo.md("Which commodities to monitor as early warning indicators?"),
        lag,
        mo.ui.plotly(_corr_heatmap_fig),
        pair,
        mo.ui.plotly(_scatter_fig),
        mo.ui.plotly(_rolling_fig),
        mo.md("### Pre/Post 2022 Comparison"),
        mo.ui.table(_comparison_df) if not _comparison_df.empty else mo.md("_No comparison data available_"),
        mo.md(f"_Procurement Implication:_ {implication}") if implication else mo.md(""),
    ], gap="1rem")

    return (signals_content,)


@app.cell
def dashboard(mo, commodity, island, year_range,
              trends_content, seasonal_content, geo_content, signals_content):
    mo.hstack([commodity, island, year_range], gap="1rem")
    mo.ui.tabs({
        "Price Trends": trends_content,
        "Seasonal Patterns": seasonal_content,
        "Geographic Disparity": geo_content,
        "Commodity Signals": signals_content,
    })
    return
