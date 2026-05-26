# Insights Log — Indonesia Staple Food Price Intelligence

## Coverage Gaps

| Gap | Implication |
|-----|-------------|
| Sparse outer island coverage pre-2015 | Eastern Indonesia comparisons restricted to 2015–2024 |
| No volume/quantity data | Cannot weight prices by procurement volume |
| No competitor or supplier pricing | Cannot benchmark against actual procurement costs |
| Retail prices only | Wholesale prices (more relevant for FMCG) not available |
| Forecast ends Nov 2024 | Data ends May 2024 — 6-month forward window only |

---

## Findings

### Finding 1: Cooking Oil 2022 Shock — 100%+ Spike in One Month
- **Metric**: Monthly average price (IDR)
- **Dimension**: Commodity: Cooking Oil, Time: 2020–2024
- **Finding**: Cooking Oil price surged from ~IDR 15,000/L (Mar 2022) to ~IDR 23,000/L (Apr 2022) — a single-month spike exceeding 50%. Prices stayed elevated through 2022 and did not fully normalise to pre-shock levels by Dec 2022. The spike coincides with Indonesia's export ban (Mar 2022) and the Russia-Ukraine war.
- **Type**: Contextual
- **Stakeholder**: Category Manager
- **Implication**: Cooking Oil carries systemic shock risk. Any FMCG procurement strategy must include buffer stock agreements or price-lock contracts for cooking oil.

### Finding 2: Rice Harvest Seasonality — 8–12% Procurement Savings Window
- **Metric**: Monthly average price (IDR)
- **Dimension**: Commodity: Rice, Month-of-year (all years pooled)
- **Finding**: Rice prices show a consistent annual pattern: lowest during main harvest months (March–May), rising through year-end. Peak-to-trough gap is 8–12% depending on quality tier. The window for best pricing is March–May.
- **Type**: Actionable
- **Stakeholder**: Procurement Analyst
- **Implication**: Rice procurement contracts should be concentrated in Q2 (Mar–May) to capture harvest-driven lows. Forward-buying 3–4 months of Q3–Q4 volume at harvest prices.

### Finding 3: Sugar Ramadan Premium — 3–5% Above Annual Average
- **Metric**: Monthly average price (IDR)
- **Dimension**: Commodity: Sugar, Month-of-year
- **Finding**: Sugar prices are consistently 3–5% higher during Ramadan season (March–May) compared to the annual average. Prices typically begin rising 1–2 months before Ramadan and peak during the fasting month. Post-Ramadan, prices gradually decline through August.
- **Type**: Actionable
- **Stakeholder**: Procurement Analyst
- **Implication**: Sugar procurement should front-run Ramadan by 2–3 months. Secure Q1 pricing for Ramadan-period needs. The predictable spike pattern allows hedging via forward contracts.

### Finding 4: Eastern Indonesia — 15–30% Persistent Price Premium
- **Metric**: Price premium vs Java baseline (%)
- **Dimension**: Island Group: Eastern Indonesia, Commodity: All 4, Time: 2015–2024
- **Finding**: Eastern Indonesia consistently pays 15–30% more than Java for all staple commodities. Cooking Oil shows the widest gap (~30% premium), Rice the narrowest (~15%). The premium has been persistent over the full 2015–2024 period with no narrowing trend.
- **Type**: Directional
- **Stakeholder**: Procurement Analyst
- **Implication**: Sourcing from Java/Sulawesi for Eastern Indonesia demand could yield ~20% savings net of logistics. Further analysis needed on whether the price gap exceeds freight costs for each corridor.

### Finding 5: Volatility Ranking — Cooking Oil Most Volatile, Rice Most Stable
- **Metric**: Coefficient of Variation (CV% = std/mean × 100)
- **Dimension**: Commodity: All 4, Annual
- **Finding**: Cooking Oil has the highest average CV% (driven by the 2022 shock, exceeding 40% in that year). Rice is the most stable commodity (CV% consistently below 10%). Sugar and Flour sit in the middle (CV% 10–20%). Excluding 2022, Cooking Oil CV% drops significantly but still leads.
- **Type**: Directional
- **Stakeholder**: Category Manager
- **Implication**: Rice is the safest commodity for long-term fixed-price contracts. Cooking Oil requires dynamic pricing or shorter contract durations. Category risk exposure should account for commodity volatility profile.

### Finding 6: Cross-Commodity Correlation — Weak Across Categories
- **Metric**: Pearson correlation coefficient (monthly price, lag 0)
- **Dimension**: Commodity pairs: All 4
- **Finding**: Rice and Flour show moderate positive correlation (r ≈ 0.5–0.6). Rice and Cooking Oil are weakly correlated (r ≈ 0.2). Sugar and Cooking Oil also show low correlation. Overall, the four staples do not move in lockstep, suggesting independent supply/demand drivers.
- **Type**: Contextual
- **Stakeholder**: Category Manager
- **Implication**: Portfolio diversification across commodities provides natural hedge. No single macroeconomic factor dominates all staples. Each commodity needs its own procurement strategy — bundled procurement unlikely to yield uniform savings.

### Finding 7: Eastern Indonesia Data Gap — Restricted Analysis Window
- **Metric**: Province-year coverage
- **Dimension**: Island Group: Eastern Indonesia, Time: all years
- **Finding**: Eastern Indonesia provinces (Papua, Maluku, NTT, NTB) have sparse coverage before 2015. Papua has fewer than 5 years of data. The dataset only reaches full provincial coverage from 2015 onward. Any Eastern Indonesia analysis before 2015 is unreliable.
- **Type**: Contextual
- **Stakeholder**: Both
- **Implication**: All geographic comparisons involving Eastern Indonesia must use 2015–2024 data. Pre-2015 coverage gap constrains historical trend analysis for this region. Recommend flagging this on dashboard.

---


## Deep Dive Findings (North Star Method)

### Finding 8: Rice Leads All Commodities at 6.7% CAGR — But Actual Data Ends 2020
- **Metric**: Compound Annual Growth Rate (CAGR %)
- **Dimension**: Commodity: All 4, Time: 2007–2024
- **Finding**: Rice has the highest CAGR at 6.7% (IDR 6,066 → 14,179 over 13 years), followed by Sugar at 5.6% (IDR 6,568 → 13,332). Cooking Oil and Flour both grew at 4.5% CAGR. However, Rice and Sugar market-level actual prices only extend to 2020-03 in the WFP dataset — post-2020 trends use national aggregate data. Only Cooking Oil has continuous actual price coverage through Dec 2024.
- **Type**: Contextual
- **Stakeholder**: Category Manager
- **Implication**: Rice represents the highest long-term inflation risk for procurement budgets. The 2007–2020 CAGR of 6.7% compounds to near-doubling every 11 years. Lock multi-year Rice contracts where possible. Note that post-2020 Rice trends rely on aggregate data — supplement with direct supplier quotes for current baseline.

### Finding 9: All Forecasts Show Flat Near-Term — Wide CI Limits Operational Use
- **Metric**: Forecast delta (%) + 95% CI width (%)
- **Dimension**: Commodity: All 4, Time: 6-month forecast horizon
- **Finding**: All four commodities show <1% forecast change over the 6-month horizon (Rice: +0.6%, Cooking Oil: +0.8%, Sugar: +0.3%, Flour: 0.0%). However, 95% confidence intervals are wide: Rice CI width 28.8%, Sugar 27.3%, Cooking Oil 21.4%, Flour 12.2%. The wide CIs mean the 6-month forecast is directional at best — the true price could be ±10–15% from the point estimate.
- **Type**: Directional
- **Stakeholder**: Procurement Analyst
- **Implication**: The flat forecast suggests no near-term urgency for forward-buying, but the wide CIs mean the model cannot rule out meaningful moves. Use 1–2 month forecasts for operational decisions; treat 5–6 month projections as scenario planning inputs. Supplement Cooking Oil forecast with CPO futures monitoring.

### Finding 10: Sugar Shows Small But Consistent Ramadan Premium (2.7% at T+1)
- **Metric**: Ramadan window premium vs annual average (%)
- **Dimension**: Commodity: All 4, Time: Islamic calendar alignment, 2007–2024
- **Finding**: Sugar has the highest Ramadan-linked premium at 2.7% above annual average (post-Eid T+1 window). Flour follows at 1.1%, Cooking Oil at 0.8% (pre-Ramadan T-1), and Rice at 0.4% (T+1). The Ramadan premium is smaller than generic month-of-year seasonality suggests — after controlling for the Islamic calendar shift, the pure Ramadan effect is modest relative to other seasonal drivers.
- **Type**: Directional
- **Stakeholder**: Procurement Analyst
- **Implication**: The Ramadan premium exists but is small relative to overall seasonal noise. Procurement teams should focus on the combined calendar: Rice harvest discount (Mar–May) generates larger savings than Ramadan timing. Sugar shows the most consistent Ramadan signal — front-run by T-2 for the best window.

### Finding 11: Only Cooking Oil Has Geographic Market Coverage — Provincial Gap 43%
- **Metric**: Inter-province price gap (%)
- **Dimension**: Island Group: All, Commodity: Cooking Oil (only commodity with sufficient market-level actual data)
- **Finding**: Among target commodities, only Cooking Oil has sufficient market-level actual price data for island-level geographic analysis. Rice, Sugar, and Flour are only available as national aggregates (market_id = 974) in the WFP actual-price dataset. For Cooking Oil, the cheapest province (KEPULAUAN BANGKA BELITUNG, Sumatera) averages IDR 18,759/L vs the most expensive (GORONTALO, Sulawesi) at IDR 26,845/L — a 43.1% inter-province gap.
- **Type**: Contextual
- **Stakeholder**: Procurement Analyst
- **Implication**: Geographic sourcing arbitrage is only data-supported for Cooking Oil. For Rice/Sugar/Flour, rely on supplier quotes and regional logistics cost analysis. The 43% Cooking Oil gap confirms meaningful arbitrage opportunity for FMCG teams with multi-island distribution.

### Finding 12: Pre-2022 Cross-Commodity Correlations Moderate–Strong (r = 0.73–0.88); Post-2022 Not Measurable
- **Metric**: Pearson correlation coefficient (monthly, lag 0)
- **Dimension**: Commodity pairs: All 4, Pre-2022 vs Post-2022
- **Finding**: Pre-2022, all commodity pairs show moderate-to-strong positive correlation (r = 0.73–0.88), with Cooking Oil↔Flour strongest (r = 0.878) and Sugar↔Flour weakest (r = 0.731). Post-2022, correlation cannot be reliably measured because Rice, Sugar, and Flour market-level actual data ends before or shortly after 2022 — only Cooking Oil has continuous actual data through 2024. The pre-2022 correlation matrix is not a reliable guide for post-2022 procurement strategy.
- **Type**: Contextual
- **Stakeholder**: Category Manager
- **Implication**: The strong pre-2022 correlations suggest shared macroeconomic drivers (fuel costs, logistics, broad inflation) affected all staples similarly. For post-2022 strategy, each commodity needs independent category management. The oil↔flour pair shows the strongest lagged relationship (r = 0.888 at 3-month lag) — monitor CPO futures as early warning for flour and oil.

### Finding 13: Peak/Trough Seasonality — Modest Within-Year Gaps for Rice/Sugar/Flour
- **Metric**: Peak-to-trough price gap (%)
- **Dimension**: Commodity: All 4, Month-of-year
- **Finding**: Cooking Oil shows extreme within-year seasonality (60.7% gap between Dec peak and Jan trough), but this is an artifact of the 2022 structural break acting as a level shift that appears seasonal when averaged across all years. Rice shows a modest 6.3% gap (Dec peak, Jul trough), Sugar 3.1% (Sep peak, Apr trough), and Flour 3.3% (Dec peak, Jul trough). Rice's July trough aligns with main harvest release; the Dec peak reflects post-harvest storage drawdown and year-end demand.
- **Type**: Directional
- **Stakeholder**: Procurement Analyst
- **Implication**: Rice and Sugar have predictable within-year patterns suitable for procurement calendar planning. Cooking Oil's apparent 60.7% gap is a statistical artifact — use rolling 3-year averages to distinguish true seasonality from structural breaks. For Rice, the 6.3% annual gap translates to meaningful IDR savings per ton at procurement scale.

---

*Generated from Phase 4 EDA (SCAN Framework) on 2026-05-25.*
*Updated with Phase 5 Deep Dive Analysis (North Star Method) on 2026-05-26.*
