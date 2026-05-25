# Wireframe Spec — Page 2: Seasonal Patterns
**Fidelity:** Annotated Mid-Fi
**Audience:** Procurement Analyst (primary), Category Manager (secondary)
**Decision Enabled:** "When should we increase stock for each commodity based on historical seasonal patterns?"
**Data Source:** `seasonal_patterns.json`

---

## Layout — Desktop (1280px)

```
┌─────────────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                    [1]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🌾 Food Price Intelligence                                      │ │
│ │ [Price Trends] [Seasonal] [Geographic] [Commodity Signals]     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│  "Seasonal" active (underlined)                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PAGE HEADER                                                   [2]   │
│  H1: "Seasonal Patterns"                                            │
│  Subtitle: "Price Premiums by Season · 2007–2024 Historical Average"│
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ GLOBAL FILTERS                                                [3]   │
│ ┌──────────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│ │ Commodity [All ▼]    │  │ Island Group[▼]  │  │ Year Range    │ │
│ └──────────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                     │
│ PAGE-SPECIFIC: Seasonal Driver Toggle                               │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │  [Ramadan/Lebaran]  [Harvest Season]  [Year-End]  [All Drivers] │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [3a] Seasonal driver toggle = tab-style selector, not dropdown     │
│  [3b] Active driver updates all charts on page                      │
│  [3c] "All Drivers" shows combined view on heatmap only             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PROCUREMENT TIMING CALLOUT CARDS                              [4]   │
│ ┌──────────────────────────────────────────────────────────────── │
│ │ H2: "Action Window — [Selected Seasonal Driver]"                │
│ │                                                                 │
│ │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│ │ │ 🛒 SUGAR        │ │ 🛒 FLOUR        │ │ 🛒 COOKING OIL  │   │
│ │ │                 │ │                 │ │                 │   │
│ │ │ Stock up        │ │ Stock up        │ │ Monitor —       │   │
│ │ │ X weeks before  │ │ X weeks before  │ │ moderate effect │   │
│ │ │ Ramadan         │ │ Ramadan         │ │                 │   │
│ │ │                 │ │                 │ │                 │   │
│ │ │ Avg spike: +~~% │ │ Avg spike: +~~% │ │ Avg spike: +~~% │   │
│ │ │ ~~ of ~~ years  │ │ ~~ of ~~ years  │ │ ~~ of ~~ years  │   │
│ │ └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│ └──────────────────────────────────────────────────────────────── │
│                                                                     │
│  [4a] Only shows commodities with statistically meaningful effect   │
│       for selected driver (avg spike > 3%)                          │
│  [4b] "~~ of ~~ years" = consistency score (e.g. 14 of 17 years)   │
│  [4c] Cards update when seasonal driver toggle changes              │
│  [4d] Rice card appears here for Harvest Season driver only         │
│  [4e] Cards sorted by spike magnitude descending                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ SEASONAL HEATMAP                                              [5]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Monthly Price Premium vs Annual Average (%)"               │ │
│ │ Subtitle: "Darker = higher than annual average"                 │ │
│ │                                                                 │ │
│ │           Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec │
│ │ Rice    │ ░░  ░░  ███  ███  ░░  ░░  ░░  ██   ██  ░░  ░░   ░░ │ │
│ │ Oil     │ ░░  ███  ██  ░░   ░░  ░░  ░░  ░░   ░░  ░░  ░░   ░░ │ │
│ │ Sugar   │ ███  ██  ░░  ░░  ░░  ░░  ░░  ░░   ░░  ░░  ██   ██ │ │
│ │ Flour   │ ░░  ░░  ░░  ░░  ░░  ░░  ░░  ░░   ░░  ░░  ░░   ░░ │ │
│ │                                                                 │ │
│ │  Scale: ░░ Below avg  ▒▒ Near avg  ██ Above avg  ███ Well above│ │
│ │                                                                 │ │
│ │  [hover: Commodity | Month | Avg premium: +X.X% | Years: N/17] │ │
│ │                                                                 │ │
│ │  ⓘ Calendar note: Ramadan months shift each year. This heatmap  │ │
│ │  shows Gregorian months — use the Ramadan overlay below for     │ │
│ │  Islamic calendar-adjusted view.                                │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [5a] Recharts custom heatmap (BarChart or custom SVG cells)        │
│  [5b] Color: single-hue scale, white → dark (no rainbow)           │
│  [5c] Rows = 4 commodities. Columns = 12 months                    │
│  [5d] Values = avg % premium vs annual average, pooled across years │
│  [5e] Seasonal driver toggle does NOT change this chart —           │
│       this is always Gregorian calendar view. Note explains why.   │
│  [5f] Height: 200px                                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ RAMADAN OVERLAY CHART (visible when Ramadan driver selected)  [6]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Price Index Relative to Eid al-Fitr — All Years Overlaid"  │ │
│ │ Subtitle: "100 = annual average. X-axis = weeks relative to Eid"│ │
│ │                                                                 │ │
│ │  Index ▲                                                        │ │
│ │   130  │              ╭╮  ← 2022 outlier (export ban)          │ │
│ │   120  │         ╭────╯│                                        │ │
│ │   110  │    ╭────╯  ╭──╯                                        │ │
│ │   100 ─┼────────────────────────────────────── annual avg      │ │
│ │    90  │                    ╰─────                              │ │
│ │    80  │                                                        │ │
│ │        └────────────────────────────────────────────────────▶  │ │
│ │         T-8  T-6  T-4  T-2   T0   T+2  T+4  T+6               │ │
│ │               (weeks relative to Eid al-Fitr)                  │ │
│ │                                                                 │ │
│ │  Each thin line = one year. Bold line = 17-year average.        │ │
│ │  Commodity selector: [Rice] [Cooking Oil] [Sugar] [Flour]       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [6a] Chart type: Recharts LineChart, multi-series (one per year)  │
│  [6b] Individual year lines: thin, low opacity gray                 │
│  [6c] Average line: bold, dark — stands out from year lines         │
│  [6d] X-axis: T-8 to T+6 weeks relative to Eid                     │
│  [6e] Y-axis: price index (100 = annual average)                   │
│  [6f] Tooltip: Week | Avg index | Year-specific index on hover     │
│  [6g] Hidden when Harvest Season or Year-End driver selected        │
│  [6h] 2022 outlier explicitly labeled — do not hide it             │
│  [6i] Height: 280px                                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ HARVEST SEASON CHART (visible when Harvest Season selected)   [7]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Rice Price Index by Harvest Season"                        │ │
│ │ Subtitle: "Main harvest: Mar–Apr. Secondary: Aug–Sep."          │ │
│ │                                                                 │ │
│ │  Index ▲                                                        │ │
│ │   110  │  ██  ██  ░░  ░░  ██  ██  ██  ░░  ░░  ██  ██  ██      │ │
│ │   100 ─┼─────────────────────────────────────── annual avg ──  │ │
│ │    90  │  ░░  ░░  ██  ██  ░░  ░░  ░░  ██  ██  ░░  ░░  ░░      │ │
│ │        └────────────────────────────────────────────────────▶  │ │
│ │          Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec│
│ │                                                                 │ │
│ │  ██ Above average  ░░ Below average                             │ │
│ │  ↓ Harvest discount windows shaded green                        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [7a] Chart type: Recharts BarChart (deviation from 100)            │
│  [7b] Harvest months (Mar–Apr, Aug–Sep) shaded differently          │
│  [7c] Rice only — flour, sugar, cooking oil less relevant here      │
│  [7d] Shows average across all years, not individual years          │
│  [7e] Hidden when Ramadan or Year-End driver selected               │
│  [7f] Height: 220px                                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ YEAR-END CHART (visible when Year-End driver selected)        [8]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Year-End Price Premium (Nov–Dec) by Commodity"             │ │
│ │ Subtitle: "Average % premium vs rest of year"                   │ │
│ │                                                                 │ │
│ │  Premium ▲                                                      │ │
│ │          │   ████                                               │ │
│ │          │   ████  ████                                         │ │
│ │          │   ████  ████  ████                                   │ │
│ │          │   ████  ████  ████  ████                             │ │
│ │          └─────────────────────────────────────────────────▶   │ │
│ │             Rice   Oil   Sugar  Flour                           │ │
│ │                                                                 │ │
│ │  [tooltip: Commodity | Avg Nov-Dec premium | Consistency score] │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [8a] Chart type: Recharts BarChart, 4 bars                         │
│  [8b] Simple horizontal bars on mobile                              │
│  [8c] Hidden when Ramadan or Harvest driver selected                │
│  [8d] Height: 200px                                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ SEASONAL SUMMARY TABLE                                        [9]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Seasonal Effect Summary — All Drivers"                     │ │
│ │                                                                 │ │
│ │ Driver        │ Commodity │ Avg Premium│ Consistency│ Lead Time │ │
│ │ ──────────────────────────────────────────────────────────────  │ │
│ │ Ramadan/Eid   │ Sugar     │ +~~%       │ ~~/17 yrs  │ ~~ weeks  │ │
│ │ Ramadan/Eid   │ Flour     │ +~~%       │ ~~/17 yrs  │ ~~ weeks  │ │
│ │ Harvest       │ Rice      │ -~~%       │ ~~/17 yrs  │ Mar–Apr   │ │
│ │ Year-End      │ Sugar     │ +~~%       │ ~~/17 yrs  │ Nov–Dec   │ │
│ │ ...           │ ...       │ ...        │ ...        │ ...       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [9a] Always visible regardless of driver toggle                    │
│  [9b] Sorted by Avg Premium descending                              │
│  [9c] Negative premiums (discounts) shown in different style        │
│  [9d] "Lead Time" = weeks/months before event when stock action     │
│       should be taken — this is the most actionable column          │
│  [9e] TanStack Table — sortable                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layout — Mobile (390px)

```
┌────────────────────────────┐
│ NAV                  [≡]   │
├────────────────────────────┤
│ H1: Seasonal Patterns      │
├────────────────────────────┤
│ FILTERS (stacked)          │
│ [Commodity ▼]              │
│ [Island Group ▼]           │
│ Year: [2007]────[2024]     │
├────────────────────────────┤
│ DRIVER TOGGLE (scroll row) │
│ [Ramadan][Harvest][Yr-End] │
├────────────────────────────┤
│ ACTION CARDS (stacked)     │
│ Full width per commodity   │
├────────────────────────────┤
│ HEATMAP                    │
│ Horizontal scroll          │
│ Sticky commodity column    │
├────────────────────────────┤
│ DRIVER-SPECIFIC CHART      │
│ Full width, height 220px   │
├────────────────────────────┤
│ SUMMARY TABLE              │
│ Horizontal scroll          │
└────────────────────────────┘
```

---

## States

| State | Behavior |
|-------|----------|
| **Loading** | Skeleton placeholders for all components |
| **Driver: Ramadan/Lebaran** | Ramadan overlay chart [6] visible; charts [7][8] hidden; action cards show Ramadan lead times |
| **Driver: Harvest Season** | Harvest chart [7] visible; charts [6][8] hidden; action cards show harvest discount window |
| **Driver: Year-End** | Year-end chart [8] visible; charts [6][7] hidden; action cards show Nov-Dec premium |
| **Driver: All Drivers** | Heatmap [5] and summary table [9] only — no driver-specific chart shown |
| **Commodity filter active** | Ramadan overlay chart filters to selected commodity; heatmap dims other rows |

---

## Annotations

| # | Element | Note |
|---|---------|------|
| 4 | Action cards | The most important element on the page for a procurement analyst — they want the answer, not the chart. Quantified lead time + consistency score is what makes this actionable vs decorative |
| 5 | Heatmap | Uses Gregorian calendar — explicitly noted in the footnote. Without this note, a hiring manager may ask "why doesn't March show a Ramadan spike?" |
| 6 | Ramadan overlay | The Islamic calendar alignment is the analytical centrepiece of this page. 17 overlaid lines showing consistent pre-Eid spike pattern is the most memorable visual in the project |
| 6 | 2022 outlier | Must be labelled. The cooking oil export ban creates a massive outlier — hiding it would be analytically dishonest |
| 9 | Lead Time column | The most actionable column in the entire dashboard — "stock up X weeks before Ramadan" directly translates to a calendar reminder for procurement |

---

## Content Specifications

| Element | Source | Format |
|---------|--------|--------|
| Action card data | `seasonal_patterns.json → action_windows[]` | `{commodity, driver, spike_pct, consistency, lead_weeks}` |
| Heatmap data | `seasonal_patterns.json → gregorian_heatmap[]` | `{commodity, month, premium_pct}` — 48 cells (4×12) |
| Ramadan overlay | `seasonal_patterns.json → ramadan_overlay[]` | `{year, week_relative, price_index}` |
| Harvest chart | `seasonal_patterns.json → harvest_index[]` | `{month, rice_index}` |
| Year-end chart | `seasonal_patterns.json → yearend_premium[]` | `{commodity, premium_pct, consistency}` |
| Summary table | `seasonal_patterns.json → summary[]` | `{driver, commodity, premium_pct, consistency, lead_time}` |
