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
        "The signal compares the **forecast average price over the next 2 months** against "
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

EXPLAINERS_P3 = {
    "island_cards": (
        "**Reading the island comparison cards**\n\n"
        "Each card shows the **2024 average Cooking Oil price** for one island group "
        "and its premium (or discount) relative to the Java baseline.\n\n"
        "\u2014 **Java** is the reference at 100 \u2014 most markets, lowest prices\n"
        "\u2014 **Plus values** indicate how much more expensive than Java "
        "(e.g., +16.4% = 16.4% above Java price)\n\n"
        "_Island groups sorted from cheapest to most expensive for quick sourcing decisions._"
    ),
    "bar_chart": (
        "**Reading the bar chart**\n\n"
        "Horizontal bars show each island group's **price index** with Java set to 100. "
        "A bar at 115 means prices in that island group average 15% higher than Java.\n\n"
        "\u2014 **Gray bar**: Java (baseline)\n"
        "\u2014 **Blue bars**: Other island groups\n\n"
        "_Use this to identify the most cost-effective sourcing regions. "
        "Combined with the province table below for market-level decisions._"
    ),
    "province_table": (
        "**Reading the province table**\n\n"
        "Each row is a province within the selected island group. Sort by any column "
        "to find the best sourcing opportunities.\n\n"
        "\u2014 **Index vs Java** > 100 = more expensive than Java average\n"
        "\u2014 **Months w/ Data** shows data coverage quality in 2024 "
        "(max 7 months, Jan\u2013Jul)\n\n"
        "_Use the island group dropdown to drill into a specific region, "
        "or select \"All\" to compare across all islands._"
    ),
    "data_scope": (
        "**Why only Cooking Oil?**\n\n"
        "The WFP dataset provides **province-level** price data for Cooking Oil only. "
        "Rice, Sugar, and Flour prices are available at **national level** only "
        "(single average per month).\n\n"
        "\u2014 Use **Price Trends** tab for national-level Rice/Sugar/Flour trends\n"
        "\u2014 Use this **Geographic tab** for Cooking Oil sourcing decisions\n\n"
        "_Data covers 34 provinces across 5 island groups for January\u2013July 2024._"
    ),
}

EXPLAINERS_P2 = {
    "action_cards": (
        "**Reading the action cards**\n\n"
        "Each card shows a commodity with a statistically meaningful seasonal price "
        "effect for the selected driver. The percentage is the **average premium** "
        "(or discount) during the seasonal window compared to the rest of the year.\n\n"
        "\u2014 **Positive %**: prices tend to rise during this window \u2192 stock up before\n"
        "\u2014 **Negative %**: prices tend to drop \u2192 consider delaying procurement\n\n"
        "_Only commodities with >3% average effect are shown. The consistency score "
        "indicates how many years the pattern held out of the available data._"
    ),
    "heatmap": (
        "**Reading the heatmap**\n\n"
        "Each cell shows the **average monthly price premium** vs. the annual average "
        "for that commodity. Darker blue = higher premium; lighter = lower.\n\n"
        "\u2014 **Values >0%** (darker): prices tend to be above average in this month\n"
        "\u2014 **Values <0%** (lighter): prices tend to be below average \u2014 "
        "potential procurement windows\n\n"
        "_This heatmap uses Gregorian calendar months. Ramadan shifts each year \u2014 "
        "see the Ramadan overlay below for an Islamic calendar-adjusted view._\n\n"
        "_Rice, Sugar, and Flour data ends March 2020 (WFP data gap). "
        "Cooking Oil data extends through December 2024._"
    ),
    "ramadan": (
        "**Reading the Ramadan overlay**\n\n"
        "Each thin line shows one year's price trajectory relative to Eid al-Fitr. "
        "The **bold line** is the multi-year average. The horizontal dotted line "
        "is the annual average baseline (index = 100).\n\n"
        "\u2014 **T-2**: 2 months before Eid (Ramadan start)\n"
        "\u2014 **T-1**: 1 month before Eid (peak Ramadan)\n"
        "\u2014 **T**: Eid al-Fitr month\n"
        "\u2014 **T+1**: 1 month after Eid\n\n"
        "_The red line highlights 2022, when Indonesia's palm oil export ban "
        "created an unusual price spike unrelated to Ramadan seasonality._\n\n"
        "_Source data is monthly, so the x-axis uses month-level granularity "
        "(not weekly as in some wireframe specifications)._"
    ),
    "harvest": (
        "**Reading the harvest chart**\n\n"
        "This chart shows **Rice** price index by month, with harvest discount "
        "windows highlighted in green (Mar\u2013Apr and Aug\u2013Sep).\n\n"
        "\u2014 **Green bars**: main harvest seasons when rice supply peaks and prices drop\n"
        "\u2014 **Blue bars**: non-harvest months\n\n"
        "_Rice is the only commodity with a pronounced harvest-driven price pattern. "
        "The dotted line marks the annual average (index = 100). Values below 100 "
        "indicate months where rice is historically cheaper._"
    ),
    "yearend": (
        "**Reading the year-end chart**\n\n"
        "Shows the average **Nov\u2013Dec price premium** for each commodity compared "
        "to the rest of the year. Year-end demand (holidays, harvesting) often "
        "pushes prices up.\n\n"
        "_The consistency score indicates how many years this premium was observed. "
        "Higher consistency = more reliable seasonal signal for procurement planning._"
    ),
    "summary": (
        "**Reading the summary table**\n\n"
        "All seasonal effects across all drivers in one sortable table. Sort by "
        "**Spike %** (absolute value) to find the strongest seasonal signals.\n\n"
        "\u2014 **Positive Spike %**: prices rise during this window (stock up before)\n"
        "\u2014 **Negative Spike %**: prices drop (potential procurement window)\n\n"
        "_**Lead Time** = how far in advance the seasonal effect begins. "
        "This is the most actionable column for procurement timing._"
    ),
}

EXPLAINERS_P4 = {
    "leading_indicators": (
        "**Reading the leading indicator cards**\n\n"
        "These cards show the **strongest predictive relationships** at the selected lag. "
        "A leading indicator is a commodity whose price movement tends to precede another's.\n\n"
        "\u2014 **r = correlation coefficient**: ranges from 0 (no relationship) to 1 (perfect).\n"
        "\u2014 **Stable post-2022**: the relationship held after the 2022 commodity shock.\n"
        "\u2014 **Weakened post-2022**: the relationship may have broken down \u2014 "
        "use with caution.\n\n"
        "_Procurement use case: if Rice consistently leads Flour by 1 month, a Rice price "
        "increase this month signals Flour procurement should be accelerated._"
    ),
    "correlation_matrix": (
        "**Reading the correlation matrix**\n\n"
        "Each cell shows the **Pearson correlation coefficient (r)** between two commodities "
        "at the selected lag. The row commodity **leads** the column commodity.\n\n"
        "\u2014 **Darker blue** = stronger positive relationship (prices move together)\n"
        "\u2014 **Diagonal cells** (commodity with itself) are blank\n\n"
        "_Click any cell to see the detailed scatter plot and stability chart for that pair. "
        "Change the lag selector above the matrix to see relationships at different lead times._"
    ),
    "scatter_plot": (
        "**Reading the scatter plot**\n\n"
        "Each point is one month of paired price data. The **x-axis** is the leading "
        "commodity's price; the **y-axis** is the following commodity's price (lagged).\n\n"
        "\u2014 **Blue dots**: Pre-2022 data (more stable relationship period)\n"
        "\u2014 **Red dots**: Post-2022 data (may show structural break)\n"
        "\u2014 **Dashed gray line**: Overall trend (full period)\n\n"
        "_If the red and blue dots cluster around the same trend line, the relationship "
        "is stable. If they diverge, the 2022 shock changed the relationship._"
    ),
    "stability_chart": (
        "**Reading the stability chart**\n\n"
        "Shows the **rolling 3-year correlation coefficient** over time for the selected "
        "commodity pair. This is the most analytically honest visual in the dashboard.\n\n"
        "\u2014 **Line above r = 0.3**: meaningful relationship\n"
        "\u2014 **Dashed gray line**: 2022 commodity shock\n"
        "\u2014 **Declining trend**: relationship weakening \u2014 treat directional signals "
        "with caution\n\n"
        "_A stable flat line above 0.5 means the relationship is reliable for procurement "
        "planning. A declining or volatile line means the relationship is breaking down._"
    ),
    "implication_card": (
        "**How procurement implications are generated**\n\n"
        "The implication card translates the statistical relationship into plain-language "
        "procurement guidance for a Category Manager audience.\n\n"
        "\u2014 **Green card** (info): stable relationship \u2014 can be used for planning\n"
        "\u2014 **Amber card** (warn): relationship weakened post-2022 \u2014 directional "
        "signal only\n\n"
        "_No r-values or statistical jargon. The card describes what it means for "
        "procurement timing, not how the statistic was computed._\n\n"
        "_This recommendation is generated from the data. It does not account for supplier "
        "contract terms or logistics constraints._"
    ),
}
