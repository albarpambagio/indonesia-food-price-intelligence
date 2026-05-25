# Wireframe Spec — Page 4: Commodity Signals
**Fidelity:** Annotated Mid-Fi
**Audience:** Category Manager (primary), Procurement Analyst (secondary)
**Decision Enabled:** "Which commodities should we monitor as early warning indicators for others?"
**Data Source:** `commodity_correlation.json`

---

## Layout — Desktop (1280px)

```
┌─────────────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                    [1]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🌾 Food Price Intelligence                                      │ │
│ │ [Price Trends] [Seasonal] [Geographic] [Commodity Signals]     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│  "Commodity Signals" active (underlined)                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PAGE HEADER                                                   [2]   │
│  H1: "Commodity Signals"                                            │
│  Subtitle: "Leading Indicators & Input Cost Bundling · 2007–2024"  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ GLOBAL FILTERS                                                [3]   │
│ ┌──────────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│ │ Commodity [All ▼]    │  │ Island Group     │  │ Year Range    │ │
│ │                      │  │ [National ▼] ⚠   │  │               │ │
│ └──────────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                     │
│ PAGE-SPECIFIC: Lag Selector                                         │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │  Lag:  [0 months]  [1 month]  [2 months]  [3 months]           │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
 │  [3a] Lag selector = tab-style, updates correlation matrix [5]     │
 │  [3b] Default: 1 month — most operationally relevant for monthly   │
 │       procurement cycles                                            │
 │  [3c] Island Group filter has no effect — all correlation           │
 │       analysis conducted at national level per WFP data coverage    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ LEADING INDICATOR CALLOUT CARDS                               [4]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Top Leading Relationships"                                 │ │
│ │                                                                 │ │
│ │ ┌──────────────────────────────┐  ┌──────────────────────────┐ │ │
│ │ │ 📈 [Commodity A] →           │  │ 📈 [Commodity C] →        │ │ │
│ │ │    [Commodity B]             │  │    [Commodity D]          │ │ │
│ │ │                              │  │                           │ │ │
│ │ │ Leads by ~~ month(s)         │  │ Leads by ~~ month(s)      │ │ │
│ │ │ Correlation: r = ~.~~        │  │ Correlation: r = ~.~~     │ │ │
│ │ │ Stable post-2022: [Yes/No]   │  │ Stable post-2022: [Yes/No]│ │ │
│ │ │                              │  │                           │ │ │
│ │ │ "When [A] rises, expect [B]  │  │ Plain-language implication│ │ │
│ │ │  to follow in ~~ month(s)."  │  │ for Category Manager      │ │ │
│ │ └──────────────────────────────┘  └──────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [4a] Shows top 2 strongest leading relationships across all lags   │
│  [4b] Plain-language implication written for Category Manager —     │
│       not "r = 0.72 at lag 2" but "When rice rises, expect flour   │
│       to follow within 2 months"                                    │
│  [4c] "Stable post-2022" flag important — 2022 commodity shock      │
│       may have broken historical relationships                       │
│  [4d] Cards update when lag selector changes                        │
│  [4e] If no strong relationship at selected lag (r < 0.3):          │
│       card shows "No strong leading relationship at this lag"        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ CORRELATION MATRIX HEATMAP                                    [5]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Cross-Commodity Correlation Matrix"                        │ │
│ │ Subtitle: "At [~] month lag. r = 1.0 = perfect co-movement"    │ │
│ │                                                                 │ │
│ │              Rice    Oil    Sugar   Flour                       │ │
│ │  Rice    │   ─     │ ~.~~ │  ~.~~  │  ~.~~  │                 │ │
│ │  Oil     │  ~.~~   │  ─   │  ~.~~  │  ~.~~  │                 │ │
│ │  Sugar   │  ~.~~   │ ~.~~ │   ─    │  ~.~~  │                 │ │
│ │  Flour   │  ~.~~   │ ~.~~ │  ~.~~  │   ─    │                 │ │
│ │                                                                 │ │
│ │  Scale: ░░ r<0.3  ▒▒ 0.3–0.6  ██ 0.6–0.8  ███ r>0.8          │ │
│ │                                                                 │ │
│ │  [hover: Commodity A | Commodity B | r = X.XX | lag = N months] │ │
│ │  [click cell: highlights that pair in scatter chart [6]]        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [5a] 4×4 grid — diagonal always blank (self-correlation = 1.0)    │
│  [5b] Matrix is asymmetric — upper triangle = A leads B,           │
│       lower triangle = B leads A                                    │
│  [5c] Label clarification above matrix: "Row commodity leads column │ │
│       commodity at selected lag"                                    │
│  [5d] Single-hue color scale: white (low r) → dark (high r)        │
│  [5e] Updates when lag selector changes                             │
│  [5f] Strongest cell highlighted with border automatically          │
│  [5g] Height: 240px                                                 │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐  ┌───────────────────────────────────┐
│ COMMODITY PAIR SCATTER  [6]  │  │ RELATIONSHIP STABILITY       [7]  │
│                              │  │                                   │
│ H2: "Price Co-Movement"      │  │ H2: "Rolling Correlation          │
│ Subtitle: "Select a pair     │  │ Stability"                        │
│ from the matrix above"       │  │ Subtitle: "3-year rolling window" │
│                              │  │                                   │
│  [Commodity A ▼] vs          │  │  r ▲  1.0                         │
│  [Commodity B ▼]             │  │     │   ────────────────          │
│                              │  │     │  ╱            ╲             │
│  B price ▲                   │  │  0.5│ ╱              ╲────        │
│          │    · ·   ·        │  │     │╱                            │
│          │  ·   · ·  ·       │  │  0.0├────────────────────────▶   │
│          │ ·  · ·   · ·      │  │     2007  2012  2017  2022  2024  │
│          │·  · ·  ·          │  │                                   │
│          └────────────────▶  │  │  ─── Rolling r  ─── r=0.3 floor  │
│              A price         │  │                                   │
│                              │  │  [7a] Shows selected pair from    │
│  [6a] Recharts ScatterChart  │  │  matrix click or dropdown [6]     │
│  [6b] Dot color: period      │  │  [7b] Vertical marker at 2022     │
│  (pre/post 2022 split)       │  │  shock — did relationship break?  │
│  [6c] Trend line overlay     │  │  [7c] Recharts LineChart          │
│  [6d] Default pair = top     │  │  [7d] Width: ~55% of row          │
│  leading relationship        │  │  [7e] Height: 220px               │
│  [6e] Height: 260px          │  └───────────────────────────────────┘
│  [6f] Width: ~40% of row     │
└──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PROCUREMENT IMPLICATION CARD                                  [8]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Input Cost Bundling Recommendation"                        │ │
│ │                                                                 │ │
│ │ Based on the strongest leading relationships identified:        │ │
│ │                                                                 │ │
│ │ ┌───────────────────────────────────────────────────────────┐  │ │
│ │ │ 📦 BUNDLE PROCUREMENT                                     │  │ │
│ │ │                                                           │  │ │
│ │ │ When [Commodity A] shows sustained price increase,        │  │ │
│ │ │ consider locking in [Commodity B] contracts within        │  │ │
│ │ │ ~~ months — historical data shows these move together     │  │ │
│ │ │ ~~/~~ times (r = ~.~~).                                   │  │ │
│ │ │                                                           │  │ │
│ │ │ ⚠ Relationship weakened post-2022 — treat as             │  │ │
│ │ │   directional signal, not deterministic.                  │  │ │
│ │ └───────────────────────────────────────────────────────────┘  │ │
│ │                                                                 │ │
│ │  This recommendation is generated from the data. It does not   │ │
│ │  account for supplier contract terms or logistics constraints.  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [8a] The analytical centrepiece of the page — translates the      │
│       correlation finding into a procurement action                 │
│  [8b] The "⚠ Relationship weakened post-2022" caveat is            │
│       non-negotiable — 2022 commodity shock may have broken         │
│       historical relationships permanently                          │
│  [8c] Updates when matrix pair selection changes                    │
│  [8d] Plain language only — no r values, no statistical jargon     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ FULL CORRELATION DETAIL TABLE                                 [9]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "All Pairwise Correlations"        [Lag: 0] [1] [2] [3]   │ │
│ │                                                                 │ │
│ │ Leading    │ Following  │ Lag  │  r    │ Pre-2022 r│ Post-2022 r│ │
│ │ ──────────────────────────────────────────────────────────────  │ │
│ │ Rice       │ Flour      │  2   │  ~.~~ │   ~.~~    │   ~.~~    │ │
│ │ Rice       │ Sugar      │  1   │  ~.~~ │   ~.~~    │   ~.~~    │ │
│ │ Oil        │ Rice       │  1   │  ~.~~ │   ~.~~    │   ~.~~    │ │
│ │ Sugar      │ Flour      │  3   │  ~.~~ │   ~.~~    │   ~.~~    │ │
│ │ ...        │ ...        │ ...  │ ...   │ ...       │ ...       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [9a] Shows all 12 directional pairs (4 commodities × 3 partners)  │
│  [9b] "Pre-2022 r" vs "Post-2022 r" split is the key column —      │
│       shows stability of each relationship                          │
│  [9c] Large divergence between pre/post = flag for instability      │
│  [9d] Sorted by r descending at selected lag                        │
│  [9e] Row click: updates scatter [6] and stability [7] charts       │
│  [9f] Lag toggle here matches page-level lag selector               │
│  [9g] TanStack Table                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layout — Mobile (390px)

```
┌────────────────────────────┐
│ NAV                  [≡]   │
├────────────────────────────┤
│ H1: Commodity Signals      │
├────────────────────────────┤
│ FILTERS (stacked)          │
│ [Commodity ▼]              │
│ [Island Group ▼]           │
│ Year: [2007]────[2024]     │
│ Lag: [0][1][2][3]          │
├────────────────────────────┤
│ LEADING INDICATOR CARDS    │
│ Stacked full width         │
├────────────────────────────┤
│ CORRELATION MATRIX         │
│ Full width, 4×4 grid       │
│ Tap cell to select pair    │
├────────────────────────────┤
│ SCATTER CHART              │
│ Full width, height 220px   │
├────────────────────────────┤
│ STABILITY CHART            │
│ Full width, height 180px   │
├────────────────────────────┤
│ IMPLICATION CARD           │
│ Full width                 │
├────────────────────────────┤
│ DETAIL TABLE               │
│ Horizontal scroll          │
└────────────────────────────┘
```

---

## States

| State | Behavior |
|-------|----------|
| **Loading** | Skeleton placeholders for all components |
| **Lag = 0** | Matrix shows contemporaneous correlations; callout cards may show weaker relationships; implication card notes "same-month co-movement, not predictive" |
| **Lag = 1, 2, or 3** | Matrix updates; strongest leading pair may change; callout cards update |
| **Matrix cell clicked** | That cell highlighted with ring; scatter chart updates to show that pair; stability chart updates; implication card updates |
| **No strong relationship (r < 0.3) at selected lag** | Callout cards show empty state: "No strong leading relationship at this lag — try a different lag" |
| **Post-2022 relationship broken** | ⚠ badge visible on callout card; implication card shows warning text |
| **Island Group filter changed** | No effect — all correlation analysis conducted at national level. Dropdown shows "[National ▼]" as locked value. Tooltip: "National-level analysis — Island Group disabled" |
| **Commodity filter = single** | Matrix reduces to show only rows/columns relevant to that commodity |

---

## Annotations

| # | Element | Note |
|---|---------|------|
| 3c | Island Group filter | Disabled — all 4 commodities correlated at national level. Cooking Oil is the only commodity with province-level data, but cross-commodity correlation requires all series at the same granularity |
| 4 | Leading indicator cards | Written for Category Manager — no r values visible here. Plain language only. This is the answer to the business question |
| 5 | Correlation matrix | The "Row leads Column" labelling must be crystal clear — correlation matrices are frequently misread. Add a one-line explanation above the matrix |
| 5 | Matrix asymmetry | Upper and lower triangles are different (A leads B ≠ B leads A at lag N). This is unusual for correlation matrices and needs clear labelling |
| 6 | Pre/post 2022 dot split | Color-coding dots by period makes the structural break visible in the scatter — hiring managers who know data will notice and appreciate this |
| 7 | Stability chart | The most analytically honest visual in the project — showing that a relationship may have broken is more valuable than pretending it's still strong |
| 8 | Implication card | The ⚠ post-2022 caveat is non-negotiable. Omitting it would make the recommendation misleading |
| 9 | Pre/post-2022 columns | This split in the detail table is the analytical differentiator of this page — most correlation analyses don't test for structural stability |

---

## Content Specifications

> **Scope:** All correlation analysis at national level. Island Group filter disabled.

| Element | Source | Format |
|---------|--------|--------|
| Leading indicator cards | `commodity_correlation.json → top_relationships[]` | `{leader, follower, lag_months, r, pre_2022_r, post_2022_r, stable, implication_text}` |
| Matrix data | `commodity_correlation.json → matrix[]` | `{leader, follower, lag, r}` — 48 records (4×4 commodities × 3 lags) |
| Scatter data | `commodity_correlation.json → pairs[]` | `{leader_price, follower_price, date, period}` — pre/post 2022 flag |
| Stability data | `commodity_correlation.json → rolling_r[]` | `{date, leader, follower, rolling_r_3yr}` |
| Detail table | `commodity_correlation.json → all_pairs[]` | `{leader, follower, lag, r, pre_2022_r, post_2022_r}` |
