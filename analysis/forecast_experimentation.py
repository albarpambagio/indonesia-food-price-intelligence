# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb",
#     "pandas",
#     "numpy",
#     "plotly",
#     "statsforecast",
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
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA, AutoETS, AutoTheta

    from pathlib import Path
    PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    PALETTE_MAP = dict(zip(["Rice", "Cooking Oil", "Sugar", "Flour"], PALETTE))
    PROJECT_DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "wfp.duckdb")
    return PALETTE, PALETTE_MAP, AutoARIMA, AutoETS, AutoTheta, StatsForecast, PROJECT_DB_PATH, duckdb, go, mo, np, pd, px


@app.cell
def script_mode(mo):
    is_script_mode = mo.app_meta().mode == "script"
    return (is_script_mode,)


@app.cell
def load_data(duckdb, mo, PROJECT_DB_PATH):
    conn = duckdb.connect(PROJECT_DB_PATH, read_only=True)
    query = """
        SELECT
            DATE_TRUNC('month', date) AS ds,
            commodity_consolidated AS commodity,
            AVG(price_idr) AS national_avg_price
        FROM wfp_intermediate.int_prices_normalised
        WHERE commodity_consolidated IS NOT NULL
          AND price_idr > 0
          AND unit IS NOT NULL
          AND EXTRACT(YEAR FROM date) BETWEEN 2007 AND 2024
        GROUP BY ds, commodity_consolidated
        ORDER BY ds, commodity_consolidated
    """
    df = conn.execute(query).fetchdf()
    df["ds"] = pd.to_datetime(df["ds"])
    conn.close()
    commodities = sorted(df["commodity"].unique())
    commodity_dd = mo.ui.dropdown(
        commodities, value="Rice", label="Select commodity"
    )
    return commodity_dd, commodities, df


@app.cell
def filter_commodity(df, commodity_dd, mo, pd):
    selected = commodity_dd.value
    hist = df[df["commodity"] == selected].copy()
    hist = hist.sort_values("ds").reset_index(drop=True)
    _rows = len(hist)
    _min_d = hist["ds"].min().strftime("%b %Y")
    _max_d = hist["ds"].max().strftime("%b %Y")
    data_info = mo.md(f"**{selected}**: {_rows} months ({_min_d} \u2013 {_max_d})")
    return data_info, hist, selected


@app.cell
def controls(mo):
    holdout_months = mo.ui.number_slider(
        start=3, stop=24, step=1, value=12, label="Holdout months"
    )
    forecast_horizon = mo.ui.number_slider(
        start=3, stop=12, step=1, value=6, label="Forecast horizon (months)"
    )
    season_length = mo.ui.number_slider(
        start=4, stop=24, step=1, value=12, label="Season length"
    )
    use_islamic = mo.ui.checkbox(
        value=True, label="Islamic calendar flags as exogenous regressors"
    )
    include_theta = mo.ui.checkbox(
        value=False, label="Include AutoTheta (slower)"
    )
    return (
        forecast_horizon, holdout_months, include_theta, season_length, use_islamic,
    )


@app.cell
def title(mo):
    mo.md("## Forecast Experimentation")
    return


@app.cell
def display_controls(data_info, forecast_horizon, holdout_months, include_theta, mo, season_length, use_islamic):
    mo.vstack([data_info, mo.hstack([
        holdout_months, forecast_horizon, season_length, use_islamic, include_theta,
    ])])
    return


@app.cell
def train_setup(hist, mo, pd, use_islamic):
    cal = pd.read_csv("transform/seeds/islamic_calendar.csv")
    for col in ["ramadan_start", "eid_date"]:
        cal[col] = pd.to_datetime(cal[col])
    cal["eid_month"] = cal["eid_date"].dt.to_period("M").astype(str)
    cal["t_minus_1"] = (cal["eid_date"] - pd.DateOffset(months=1)).dt.to_period("M").astype(str)
    cal["t_minus_2"] = (cal["eid_date"] - pd.DateOffset(months=2)).dt.to_period("M").astype(str)
    cal["t_minus_3"] = (cal["eid_date"] - pd.DateOffset(months=3)).dt.to_period("M").astype(str)

    train_df = hist[["commodity", "ds", "national_avg_price"]].copy()
    train_df.columns = ["unique_id", "ds", "y"]

    if use_islamic.value:
        train_df["ym"] = train_df["ds"].dt.to_period("M").astype(str)
        for _col, _flag in [("eid_month", "eid"), ("t_minus_1", "t1"), ("t_minus_2", "t2"), ("t_minus_3", "t3")]:
            train_df[_flag] = 0
            for _, _row in cal.iterrows():
                train_df.loc[train_df["ym"] == _row[_col], _flag] = 1

    return cal, train_df


@app.cell
def holdout_evaluation(
    AutoARIMA, AutoETS, AutoTheta, StatsForecast, holdout_months, include_theta,
    mo, np, pd, season_length, train_df,
):
    h = int(holdout_months.value)
    cutoff = train_df["ds"].max() - pd.DateOffset(months=h)
    train = train_df[train_df["ds"] <= cutoff].reset_index(drop=True)
    test = train_df[train_df["ds"] > cutoff].reset_index(drop=True)

    models = [AutoARIMA(season_length=int(season_length.value)),
              AutoETS(season_length=int(season_length.value))]
    if include_theta.value:
        models.append(AutoTheta(season_length=int(season_length.value)))

    sf = StatsForecast(models=models, freq="MS", n_jobs=1)
    sf.fit(df=train[["unique_id", "ds", "y"]])

    holdout_preds = sf.forecast(h=len(test), df=train[["unique_id", "ds", "y"]])

    mae_scores = {}
    for m in holdout_preds.columns:
        if m in ("unique_id", "ds") or "-lo-" in m or "-hi-" in m:
            continue
        actual = test["y"].values
        pred = holdout_preds[m].values
        mask = ~np.isnan(actual) & ~np.isnan(pred)
        mae_scores[m] = float(np.mean(np.abs(actual[mask] - pred[mask])))

    best_model = min(mae_scores, key=mae_scores.get)

    mo.md(f"**Holdout MAE by model**: {mae_scores}")
    return best_model, cutoff, h, holdout_preds, mae_scores, models, sf, test, train


@app.cell
def final_forecast(
    StatsForecast, best_model, cal, forecast_horizon, models, mo, selected, train_df,
):
    fh = int(forecast_horizon.value)
    chosen = [m for m in models if best_model in str(type(m))]
    sf_final = StatsForecast(models=chosen, freq="MS", n_jobs=1)

    exog_cols = [c for c in ["eid", "t1", "t2", "t3"] if c in train_df.columns]
    if exog_cols:
        sf_final.fit(df=train_df[["unique_id", "ds", "y", *exog_cols]])
        future_dates = pd.date_range(
            start=(train_df["ds"].max() + pd.DateOffset(months=1)).strftime("%Y-%m-%d"),
            periods=fh, freq="MS"
        )
        fdf = pd.DataFrame({"unique_id": selected, "ds": future_dates})
        fdf["ym"] = fdf["ds"].dt.to_period("M").astype(str)
        for _flag in ["eid", "t1", "t2", "t3"]:
            fdf[_flag] = 0
            for _, _row in cal.iterrows():
                fdf.loc[fdf["ym"] == _row[_flag.replace("eid", "eid_month").replace("t1", "t_minus_1").replace("t2", "t_minus_2").replace("t3", "t_minus_3")], _flag] = 1
        fcast = sf_final.forecast(h=fh, df=train_df[["unique_id", "ds", "y", *exog_cols]],
                                   X_df=fdf[["unique_id", "ds", *exog_cols]], level=[95])
    else:
        sf_final.fit(df=train_df[["unique_id", "ds", "y"]])
        fcast = sf_final.forecast(h=fh, df=train_df[["unique_id", "ds", "y"]], level=[95])

    model_cols = [c for c in fcast.columns if c not in ("unique_id", "ds") and "-lo-" not in c and "-hi-" not in c]
    best_model_name = model_cols[0] if model_cols else "?"
    mo.md(f"**Best model**: {best_model_name}")
    return model_cols, exog_cols, fcast, fh, sf_final


@app.cell
def plot_forecast(model_cols, fcast, go, selected, train, train_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=train["ds"], y=train["y"], mode="lines",
        name="Train", line=dict(color="#4C72B0", width=2)))
    fig.add_trace(go.Scatter(
        x=train_df[train_df["ds"] > train["ds"].max()]["ds"],
        y=train_df[train_df["ds"] > train["ds"].max()]["y"],
        mode="lines", name="Test (holdout)", line=dict(color="#DD8452", width=2, dash="dot")))

    lo_col = f"{model_cols[0]}-lo-95"
    hi_col = f"{model_cols[0]}-hi-95"

    fig.add_trace(go.Scatter(
        x=fcast["ds"], y=fcast[model_cols[0]], mode="lines+markers",
        name=f"Forecast ({model_cols[0]})", line=dict(color="#C44E52", width=2),
        marker=dict(size=6)))
    if lo_col in fcast.columns:
        fig.add_trace(go.Scatter(
            x=fcast["ds"], y=fcast[lo_col], mode="lines",
            name="Lower 95% CI", line=dict(color="#C44E52", width=1, dash="dash")))
        fig.add_trace(go.Scatter(
            x=fcast["ds"], y=fcast[hi_col], mode="lines",
            name="Upper 95% CI", line=dict(color="#C44E52", width=1, dash="dash"),
            fill="tonexty", fillcolor="rgba(196, 78, 82, 0.1)"))

    fig.update_layout(
        title=f"{selected} \u2014 National Average Price with Forecast",
        xaxis_title="Date", yaxis_title="Price (IDR)",
        template="plotly_white", height=500, margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified")
    fig.add_vline(x=train["ds"].max(), line=dict(color="gray", width=1, dash="dash"))
    fig.add_annotation(x=train["ds"].max(), y=1, yref="paper", text="holdout split",
                       showarrow=False, font=dict(size=10, color="gray"))
    return fig


@app.cell
def render_forecast_plot(mo, fig):
    mo.ui.plotly(fig)
    return


@app.cell
def cross_validation_analysis(AutoARIMA, AutoETS, AutoTheta, StatsForecast, best_model, include_theta, mo, np, season_length, train, train_df):
    mos_models = [AutoARIMA(season_length=int(season_length.value)),
                  AutoETS(season_length=int(season_length.value))]
    if include_theta:
        mos_models.append(AutoTheta(season_length=int(season_length.value)))

    sf_cv = StatsForecast(models=mos_models, freq="MS", n_jobs=1)
    cv_df = sf_cv.cross_validation(
        df=train_df[["unique_id", "ds", "y"]],
        h=6,
        step_size=1,
        n_windows=2,
    )
    cv_mae = cv_df.groupby("unique_id").apply(
        lambda g: {m: float(np.mean(np.abs(g["y"] - g[m]))) for m in [m for m in cv_df.columns if m not in ("unique_id", "ds", "y", "cutoff", "lo-95", "hi-95")]}
    ).iloc[0] if len(cv_df) > 0 else {}
    mo.md(f"**Cross-validation MAE (avg over 2 windows)**: {cv_mae}")
    return cv_df, cv_mae, sf_cv


@app.cell
def footer(mo):
    mo.md("---\n*Run `uv run marimo edit analysis/forecast_experimentation.py` to open interactively*")
    return


if __name__ == "__main__":
    app.run()
