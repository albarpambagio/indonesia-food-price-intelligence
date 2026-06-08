EXPLAINERS = {
    "kpi_cards": (
        "**Reading the KPI cards**\n\n"
        "Each card shows the **latest available monthly average price** across all "
        "national market monitoring points. The percentage below it is the "
        "**year-over-year change** \u2014 this month vs. the same month last year.\n\n"
        "\u2014 Arrow **up + red**: prices higher than a year ago \u2192 less favourable buying conditions\n"
        "\u2014 Arrow **down + green**: prices lower than a year ago \u2192 potentially favourable conditions\n\n"
        "_Note: These reflect broad market averages. Regional prices and supplier "
        "contract rates may differ._"
    ),
    "trend_chart": (
        "**Reading the trend chart**\n\n"
        "The **solid lines** show historical monthly average prices. The **dashed lines** "
        "extend into the forecast period. The **shaded band** is the 95% confidence "
        "interval \u2014 the model expects actual prices to land within this range "
        "19 times out of 20.\n\n"
        "The vertical dashed line marks where historical data ends and forecast begins.\n\n"
        "_The \u201c2022 Export Ban\u201d annotation marks Indonesia\u2019s palm oil export ban "
        "(Apr\u2013May 2022), which caused the cooking oil price spike visible in that period._\n\n"
        "_Procurement tip: Narrow bands signal high model confidence; wide bands mean "
        "high uncertainty \u2014 treat those months as \u201cmonitor, don\u2019t commit.\u201d_"
    ),
    "buy_signal": (
        "**How buy signals are calculated**\n\n"
        "The signal compares the **forecast average price over the next 6 months** against "
        "the **most recent actual price**:\n\n"
        "| Signal | Ratio | Meaning for procurement |\n"
        "|--------|-------|------------------------|\n"
        "| \u2705 BUY NOW | Forecast avg < 98% of current | Model expects prices to fall; "
        "buying now locks in a higher cost than waiting |\n"
        "| \u23f8\ufe0f HOLD | Ratio between 0.98\u20131.02 | No strong directional signal; monitor weekly |\n"
        "| \U0001f7e1 WATCH | Forecast avg > 102% of current | Prices expected to rise; "
        "consider accelerating procurement or forward contracts |\n\n"
        "_Important: These signals are based on historical pattern extrapolation only. "
        "Government interventions, import policy changes, and weather events are not modelled._"
    ),
    "yoy_table": (
        "**Reading the YoY table**\n\n"
        "Each cell shows the **percentage change in the full-year average price** compared "
        "to the prior year. This differs from the KPI card figure (which is month vs. same "
        "month) \u2014 the table smooths out seasonal spikes and gives a cleaner view of "
        "structural inflation.\n\n"
        "Positive values in red = annual price inflation for that commodity.\n"
        "Negative values in green = annual deflation (rare; often reflects a policy "
        "intervention).\n\n"
        "_Procurement tip: Years with 5%+ change across multiple commodities often "
        "coincide with supply shocks or currency depreciation \u2014 useful context for "
        "long-term contract negotiations._"
    ),
    "forecast_note": (
        "**How reliable are these forecasts?**\n\n"
        "The model fits historical seasonal and trend patterns. Reliability degrades "
        "over time:\n\n"
        "\u2014 **1\u20132 months out**: High reliability; seasonal patterns dominate\n"
        "\u2014 **3\u20134 months out**: Moderate; macroeconomic drift begins to matter\n"
        "\u2014 **5\u20136 months out**: Low; confidence intervals are wide \u2014 use "
        "directional signal only, not the specific price point\n\n"
        "_This model cannot predict: government price controls, new import tariffs, "
        "crop failures, or global commodity shocks. Always validate against supplier "
        "quotes before committing._"
    ),
}
