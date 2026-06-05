"""Page 2 — Seasonal Patterns (Vizro).

Question: "When should we increase stock for each commodity?"
Data: mart_price_trends_national + int_islamic_calendar
"""

import vizro.models as vm

from dashboard.charts.harvest_chart import harvest_chart
from dashboard.charts.ramadan_overlay import ramadan_overlay
from dashboard.charts.seasonal_heatmap import seasonal_heatmap
from dashboard.charts.seasonal_summary_table import seasonal_summary_table
from dashboard.charts.yearend_chart import yearend_chart


def _build_action_cards() -> vm.Card:
    return vm.Card(
        text="""
### Action Window — Seasonal Driver

Select a seasonal driver above to see procurement timing recommendations.

- **Ramadan**: Stock up 2 months before Eid al-Fitr
- **Harvest**: Rice discounts during Mar-Apr and Aug-Sep
- **Year-End**: Watch Nov-Dec price premiums

Cards update when the driver toggle changes.
        """,
    )


def _build_data_availability_notice() -> vm.Card:
    return vm.Card(
        text="""
> ℹ️ Seasonal analysis uses national-level data for Rice, Sugar, Flour.
> Island-level breakdown available for Cooking Oil only.
> Rice/Sugar/Flour data ends March 2020 (WFP data gap).
        """,
    )


seasonal_patterns_page = vm.Page(
    title="Seasonal Patterns",
    description="Price premiums by season — 2007-2024 historical average",
    components=[
        vm.Container(
            components=[
                _build_action_cards(),
                _build_data_availability_notice(),
                vm.Graph(
                    id="seasonal_heatmap",
                    figure=seasonal_heatmap(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.Graph(
                    id="ramadan_overlay",
                    figure=ramadan_overlay(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.Graph(
                    id="harvest_chart",
                    figure=harvest_chart(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.Graph(
                    id="yearend_chart",
                    figure=yearend_chart(
                        data_frame="mart_price_trends_national",
                    ),
                ),
                vm.AgGrid(
                    id="seasonal_summary_table",
                    figure=seasonal_summary_table(
                        data_frame="mart_price_trends_national",
                    ),
                ),
            ],
            layout=vm.Flex(direction="column", gap="20px"),
        ),
    ],
    controls=[
        vm.Parameter(
            id="s2-param-commodity",
            targets=[
                "seasonal_heatmap.commodity_filter",
                "ramadan_overlay.commodity_filter",
                "yearend_chart.commodity_filter",
                "seasonal_summary_table.commodity_filter",
            ],
            selector=vm.Dropdown(
                options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
                value="All",
                multi=False,
            ),
        ),
        vm.Parameter(
            id="s2-param-driver",
            targets=[
                "ramadan_overlay.driver",
                "harvest_chart.driver",
                "yearend_chart.driver",
            ],
            selector=vm.RadioItems(
                options=["All", "Ramadan", "Harvest", "Year-End"],
                value="All",
            ),
        ),
    ],
)
