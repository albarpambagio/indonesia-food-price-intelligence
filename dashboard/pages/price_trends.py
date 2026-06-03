"""Page 1 — Price Trends & Forecast (Vizro).

Question: "Is now a good time to lock in bulk purchase contracts?"
Data: mart_price_trends_national + forecast.json
"""

import vizro.models as vm

from dashboard.charts.kpi_sparklines import kpi_sparklines
from dashboard.charts.signal_badges import signal_badges
from dashboard.charts.trend_forecast import trend_forecast
from dashboard.charts.yoy_bar import yoy_bar
from dashboard.data_access import load_forecast_metadata


def _build_model_info_card() -> vm.Container:
    """Build model info card with dynamic model selection and MAE from forecast metadata."""
    metadata = load_forecast_metadata()
    models = metadata.get("models", {})

    rows = []
    for commodity in ["Rice", "Cooking Oil", "Sugar", "Flour"]:
        if commodity in models:
            model = models[commodity]
            selected = model.get("selected", "N/A")
            mae = model.get("holdout_mae", 0)
            rows.append(f"| {commodity} | {selected} | {mae:,.0f} |")

    table_rows = "\n".join(rows)

    return vm.Container(
        components=[
            vm.Card(
                text=f"""### Model Selection

| Commodity | Model | Holdout MAE |
|-----------|-------|-------------|
{table_rows}
                """,
            ),
            vm.Card(
                text="""
### Model Limitations

- Forecast uses AutoARIMA/AutoETS with 6-month horizon.
- 95% confidence intervals widen significantly at 5-6 months.
- Cooking Oil post-2022 structural break reduces forecast reliability.
- Forecast uses all price data (including aggregate flags); dashboard uses only 'actual' flag.
- No volume weighting — all markets equal weight.

[See methodology →](https://github.com/albarpambagio/wfp-food-price-intelligence/blob/main/docs/model_methodology.md)
                """,
            ),
        ],
        layout=vm.Flex(direction="row"),
    )


price_trends_page = vm.Page(
    title="Price Trends & Forecast",
    description="17-year national price history with 6-month forecast overlay",
    components=[
        vm.Graph(
            id="kpi_sparklines",
            figure=kpi_sparklines(
                data_frame="mart_price_trends_national",
                commodity_filter="commodity_filter",
            ),
        ),
        vm.Graph(
            id="trend_forecast",
            figure=trend_forecast(
                data_frame="mart_price_trends_national",
                commodity_filter="commodity_filter",
            ),
        ),
        vm.Graph(
            id="yoy_bar",
            figure=yoy_bar(
                data_frame="mart_price_trends_national",
                commodity_filter="commodity_filter",
            ),
        ),
        vm.Graph(
            id="signal_badges",
            figure=signal_badges(
                data_frame="mart_price_trends_national",
                commodity_filter="commodity_filter",
            ),
        ),
        _build_model_info_card(),
    ],
    controls=[
        vm.Parameter(
            id="param-commodity",
            targets=[
                "kpi_sparklines.commodity_filter",
                "trend_forecast.commodity_filter",
                "yoy_bar.commodity_filter",
                "signal_badges.commodity_filter",
            ],
            selector=vm.Dropdown(
                options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
                value="All",
                multi=False,
            ),
        ),
    ],
)
