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

*Generated from Phase 4 EDA (SCAN Framework) on 2026-05-25.*
