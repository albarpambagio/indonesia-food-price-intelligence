# Wireframe Spec — Page 1: Price Trends & Forecast
**Fidelity:** Annotated Mid-Fi
**Audience:** Category Manager (primary), Procurement Analyst (secondary)
**Decision Enabled:** "Is now a good time to lock in bulk purchase contracts for key commodities?"
**Data Sources:** `price_trends.json`, `forecast.json`

---

## Layout — Desktop (1280px)

```
┌─────────────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                    [1]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🌾 Food Price Intelligence                                      │ │
│ │ [Price Trends] [Seasonal] [Geographic] [Commodity Signals]     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│  H: 56px | Logo left, nav links right | "Price Trends" active       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PAGE HEADER                                                   [2]   │
│  H1: "Price Trends & Forecast"                                      │
│  Subtitle: "Indonesian Staple Commodities · Jan 2007 – May 2024     │
│             + 6-Month Forecast"                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ GLOBAL FILTERS                                                [3]   │
│ ┌──────────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│ │ Commodity [All ▼]    │  │ Island Group[▼]  │  │ Year Range    │ │
│ │ Rice / Cooking Oil   │  │ All / Java /     │  │ [2007]──[2024]│ │
│ │ Sugar / Flour / All  │  │ Sumatera / ...   │  │ ◄─────────►  │ │
│ └──────────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                     │
│  [3a] Year Range: dual-handle slider, 2007–2024                     │
│  [3b] All filters persist across page navigation                    │
│  [3c] Commodity = All shows all four series on trend chart          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ KPI CARDS ROW — CURRENT PRICE SNAPSHOT                        [4]   │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌─────────┐ │
│ │ RICE          │ │ COOKING OIL   │ │ SUGAR         │ │ FLOUR   │ │
│ │               │ │               │ │               │ │         │ │
│ │ Rp ~~~~/KG    │ │ Rp ~~~~~/L    │ │ Rp ~~~~~/KG   │ │Rp~~~/KG │ │
│ │               │ │               │ │               │ │         │ │
│ │ ↑ ~~% YoY    │ │ ↑ ~~% YoY    │ │ ↑ ~~% YoY    │ │↑ ~% YoY │ │
│ │ [trend spark] │ │ [trend spark] │ │ [trend spark] │ │[spark]  │ │
│ └───────────────┘ └───────────────┘ └───────────────┘ └─────────┘ │
│                                                                     │
│  [4a] "Current price" = latest available (May 2024)                 │
│  [4b] YoY = vs May 2023. ↑ red if rising, ↓ green if falling       │
│  [4c] Sparkline: 24-month mini trend. Dotted extension = forecast   │
│  [4d] Four equal-width cards always shown regardless of filter      │
│  [4e] Loading state: gray skeleton placeholders                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ MAIN TREND + FORECAST CHART                                   [5]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "17-Year Price History + 6-Month Forecast"                  │ │
│ │                                                                 │ │
│ │ Commodity toggle: [Rice] [Cooking Oil] [Sugar] [Flour] [All]   │ │
│ │                                                                 │ │
│ │  IDR ▲                              ┆ FORECAST                 │ │
│ │      │                    ╭─────────┆╌╌╌╌╌╌ ░░░░░░            │ │
│ │      │           ╭────────╯         ┆      ╌╌╌╌╌╌╌            │ │
│ │      │    ╭──────╯                  ┆   ░░░░░░░░░░░░           │ │
│ │      │   ╱                          ┆╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌          │ │
│ │      │  ╱                           ┆                          │ │
│ │      └──────────────────────────────┆──────────────────────▶  │ │
│ │       2007  2010  2013  2016  2019  2022 2024  Nov2024         │ │
│ │                                     ┆                          │ │
│ │  ░░░ 95% confidence interval                                   │ │
│ │  ─── Actual prices   ╌╌╌ Forecast                              │ │
│ │                                                                 │ │
│ │  [Model: AutoARIMA ▼]  ← small dropdown to toggle model view   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [5a] Chart type: Recharts ComposedChart (Line + Area for CI)       │
│  [5b] Vertical dashed line separates actuals from forecast          │
│  [5c] Shaded area = 95% confidence interval, forecast region only   │
│  [5d] Commodity toggle updates series shown — All shows 4 lines     │
│  [5e] Structural break annotation: "2022 Export Ban" label on chart │
│  [5f] Tooltip: Date | Price IDR | Price USD | (if forecast: lower   │
│       bound, upper bound)                                           │
│  [5g] Y-axis: IDR formatted (e.g. "5K", "10K", "15K" per KG/L)    │
│  [5h] Height: 360px. Primary analytical element of the page        │
│  [5i] Responds to all three global filters                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐  ┌──────────────────────────────────┐
│ PROCUREMENT ACTION ZONE [6]  │  │ YoY INFLATION TABLE         [7]  │
│                              │  │                                  │
│ H2: "Buy Signal Monitor"     │  │ H2: "Annual Price Change"        │
│                              │  │                                  │
│ ┌──────────────────────────┐ │  │ Yr  │ Rice │ Oil  │ Sugar│ Flour │
│ │ Rice      ● WATCH        │ │  │ ─────────────────────────────── │
│ │ Forecast within range    │ │  │ 2024│ +~~% │ +~~% │ +~~% │ +~~% │
│ │                          │ │  │ 2023│ +~~% │ -~~% │ +~~% │ +~~% │
│ │ Cooking Oil ● BUY NOW   │ │  │ 2022│ +~~% │ +~~% │ +~~% │ +~~% │
│ │ Forecast lower than now  │ │  │ 2021│ +~~% │ +~~% │ +~~% │ +~~% │
│ │                          │ │  │ 2020│ -~~% │ +~~% │ -~~% │ +~~% │
│ │ Sugar     ● HOLD         │ │  │ ... │ ...  │ ...  │ ...  │ ...  │
│ │ Approaching spike season │ │  │                                  │
│ │                          │ │  │ [6a] Sortable by any column      │
│ │ Flour     ● WATCH        │ │  │ [6b] Red cell = >10% increase    │
│ │ Stable forecast          │ │  │ [6c] Green cell = decrease       │
│ └──────────────────────────┘ │  │ [6d] Responds to Year Range      │
│                              │  │      filter                      │
│  [6a] Signal logic:          │  └──────────────────────────────────┘
│  BUY NOW = forecast lower    │
│  bound < current price       │
│  HOLD = forecast stable      │
│  WATCH = forecast rising     │
│                              │
│  [6b] Color: BUY=dark,       │
│  HOLD=mid-gray, WATCH=light  │
│  [6c] Updated from           │
│  forecast.json signals array │
│  Width: ~35% of row          │
└──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ MODEL LIMITATIONS FOOTNOTE                                    [8]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ ⓘ Forecast limitations: This model describes historical price   │ │
│ │ patterns. It cannot anticipate government price controls,       │ │
│ │ import tariff changes, or weather events. Confidence intervals  │ │
│ │ widen significantly beyond 3 months. See methodology →          │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [8a] Always visible — not collapsible. Small font but present     │
│  [8b] "See methodology →" links to docs/model_methodology.md       │
│       (GitHub link, opens new tab)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layout — Mobile (390px)

```
┌────────────────────────────┐
│ NAV                  [≡]   │
├────────────────────────────┤
│ H1: Price Trends & Forecast│
│ Subtitle (2 lines max)     │
├────────────────────────────┤
│ FILTERS (stacked)          │
│ [Commodity ▼]              │
│ [Island Group ▼]           │
│ Year: [2007]────[2024]     │
├────────────────────────────┤
│ KPI: Rice      (full width)│
│ KPI: Cooking Oil           │
│ KPI: Sugar                 │
│ KPI: Flour                 │
├────────────────────────────┤
│ Commodity toggle (scroll   │
│ horizontally if needed)    │
│ TREND + FORECAST CHART     │
│ Full width, height 260px   │
│ Pinch to zoom enabled      │
├────────────────────────────┤
│ BUY SIGNAL MONITOR         │
│ Full width, stacked list   │
├────────────────────────────┤
│ YoY TABLE                  │
│ Horizontal scroll          │
│ Sticky year column         │
├────────────────────────────┤
│ Limitations footnote       │
└────────────────────────────┘
```

---

## States

| State | Behavior |
|-------|----------|
| **Loading** | Skeleton gray boxes for all charts and KPI cards |
| **Commodity = single (e.g. Rice)** | Trend chart shows single series; KPI cards all remain visible but Rice highlighted with border; YoY table filtered to Rice column only |
| **Commodity = All** | Four series on trend chart with distinct line styles (solid/dashed/dotted/dash-dot); all KPI cards equal weight |
| **Year Range narrowed** | Chart zooms to selected range; YoY table filters rows; KPI card sparklines adjust |
| **Hover on forecast region** | Tooltip shows date, forecast price, lower bound, upper bound |
| **Structural break annotation hover** | Small popover: "Indonesia cooking oil export ban, Apr–May 2022" |

---

## Annotations

| # | Element | Note |
|---|---------|------|
| 4 | KPI cards | Four cards always shown even when single commodity filtered — gives instant cross-commodity comparison without needing to change filter |
| 5 | Trend chart | The vertical dashed separator between actuals and forecast is the most important visual element on this page — make it prominent |
| 5 | Structural break | 2022 annotation must be present — without it a hiring manager will ask "what caused that spike?" and think you missed it |
| 6 | Buy Signal Monitor | Plain language signals for Category Manager audience — they should not need to read the chart to get the answer |
| 7 | YoY table | Finance audience anchor — gives exact numbers the charts approximate |
| 8 | Limitations footnote | Non-negotiable. Must be visible without scrolling on desktop |

---

## Content Specifications

| Element | Source | Format |
|---------|--------|--------|
| Current price | `price_trends.json → latest[]` | `Rp X,XXX/KG` or `Rp X,XXX/L` |
| YoY change | Calculated client-side | `+X.X%` red / `-X.X%` green |
| Sparklines | `price_trends.json → monthly[last 24]` | Array of 24 price values |
| Trend series | `price_trends.json → monthly[]` | `{date, commodity, price_idr, price_usd}` |
| Forecast series | `forecast.json → forecasts[]` | `{date, commodity, forecast, lower_95, upper_95, model}` |
| Buy signals | `forecast.json → signals[]` | `{commodity, signal: BUY/HOLD/WATCH, reason}` |
| YoY table | `price_trends.json → annual_change[]` | `{year, rice_pct, oil_pct, sugar_pct, flour_pct}` |
