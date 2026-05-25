# Wireframe Spec — Page 3: Geographic Disparity
**Fidelity:** Annotated Mid-Fi
**Audience:** Procurement Analyst (primary)
**Decision Enabled:** "Which island group or province offers the best sourcing price right now?"
**Data Source:** `geographic_disparity.json`

---

## Layout — Desktop (1280px)

```
┌─────────────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                    [1]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🌾 Food Price Intelligence                                      │ │
│ │ [Price Trends] [Seasonal] [Geographic] [Commodity Signals]     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│  "Geographic" active (underlined)                                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PAGE HEADER                                                   [2]   │
│  H1: "Geographic Price Disparity"                                   │
│  Subtitle: "Price Index vs Java Baseline · Island Group & Province" │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ GLOBAL FILTERS                                                [3]   │
│ ┌──────────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│ │ Commodity [Rice ▼]   │  │ Island Group[▼]  │  │ Year Range    │ │
│ └──────────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                     │
│  [3a] Commodity defaults to Rice — most complete geographic coverage│
│  [3b] Island Group filter here controls province drill-down [7]     │
│       only — map [5] always shows all island groups                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ KPI CARDS — CURRENT PRICE INDEX BY ISLAND GROUP               [4]   │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ JAVA     │ │SUMATERA  │ │KALIMANTAN│ │SULAWESI  │ │ EASTERN  │ │
│ │          │ │          │ │          │ │          │ │ INDONESIA│ │
│ │ 100      │ │ ~~~      │ │ ~~~      │ │ ~~~      │ │ ~~~      │ │
│ │ baseline │ │ vs Java  │ │ vs Java  │ │ vs Java  │ │ vs Java  │ │
│ │          │ │ ↑ +~~%   │ │ ↑ +~~%   │ │ ↑ +~~%   │ │ ↑ +~~%   │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                                     │
│  [4a] Java = 100 always. Other cards show index value + % premium  │
│  [4b] "Current" = most recent year of data (2024)                  │
│  [4c] ↑ red = more expensive than Java. ↓ green = cheaper          │
│  [4d] Clicking a card highlights that island group on map and       │
│       filters province drill-down table                             │
│  [4e] Five equal-width cards — scroll horizontally on mobile        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ INDONESIA CHOROPLETH MAP                                      [5]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Price Index vs Java — [Selected Commodity]"                │ │
│ │                                                                 │ │
│ │  ┌─────────────────────────────────────────────────────────┐   │ │
│ │  │                     [MAP OF INDONESIA]                  │   │ │
│ │  │  Island groups colored by price index vs Java           │   │ │
│ │  │                                                         │   │ │
│ │  │  Sumatera     ░░░  (light — near Java price)            │   │ │
│ │  │  Java         ███  (baseline — medium gray)             │   │ │
│ │  │  Kalimantan   ░░░  (light)                              │   │ │
│ │  │  Sulawesi     ▒▒▒  (mid — moderate premium)             │   │ │
│ │  │  Eastern ID   ███  (dark — high premium)                │   │ │
│ │  │                                                         │   │ │
│ │  │  [hover: Island Group | Price Index | Avg Price IDR]    │   │ │
│ │  │  [click: filter province drill-down to that group]      │   │ │
│ │  └─────────────────────────────────────────────────────────┘   │ │
│ │                                                                 │ │
│ │  Scale: ░░ Near Java   ▒▒ +10–20%   ██ +20–40%   ███ +40%+    │ │
│ │                                                                 │ │
│ │  Year slider: [2007] ────●──── [2024]  [▶ Animate]             │ │
│ │                                                                 │ │
│ │  ⓘ Province-level detail available below for island groups      │ │
│ │  with sufficient data coverage (2015–2024).                     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [5a] Rendered using GeoJSON + Recharts or D3 SVG                  │
│  [5b] Island group granularity only on map — not province level     │
│  [5c] Single-hue color scale (light = near Java, dark = far above) │
│  [5d] Year slider animates color intensity changes over time        │
│  [5e] "Animate" button plays 2007→2024 at 1 second per year        │
│  [5f] Height: 340px                                                 │
│  [5g] GeoJSON source: Indonesia island group boundaries             │
│       (simplified for web performance — not full provincial detail) │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ ISLAND GROUP COMPARISON CHART                                 [6]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Price Index Over Time — Island Groups vs Java"             │ │
│ │                                                                 │ │
│ │  Index ▲   ─── Java (100)                                       │ │
│ │        │   ─── Eastern ID      ╭──────────────────             │ │
│ │        │   ─── Sulawesi      ╭─╯                               │ │
│ │  120   │              ──────╯                                   │ │
│ │        │   ─── Kalimantan ╭─────────────────────               │ │
│ │  110   │              ───╯                                      │ │
│ │        │   ─── Sumatera ─────────────────────────              │ │
│ │  100 ──┼─────────────────────────────────── Java               │ │
│ │        └──────────────────────────────────────────────────▶    │ │
│ │          2007  2010  2013  2016  2019  2022  2024               │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [6a] Chart type: Recharts LineChart, 5 series                     │
│  [6b] Java = flat horizontal line at 100 (baseline reference)       │
│  [6c] Shows whether gaps are narrowing or widening over time        │
│  [6d] Tooltip: Year | All island group indices                      │
│  [6e] Responds to Commodity filter — redraws for each commodity     │
│  [6f] Height: 260px                                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PROVINCE DRILL-DOWN TABLE                                     [7]   │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ H2: "Province Detail — [Selected Island Group]"                 │ │
│ │ Subtitle: "2015–2024 only · Coverage validated"  [Search...]   │ │
│ │                                                                 │ │
│ │ Province       │ Island Group  │ Avg Price │ vs Java │ Coverage │ │
│ │ ───────────────────────────────────────────────────────────── │ │
│ │ PAPUA          │ Eastern ID    │ Rp ~~~~~  │ +~~%    │ 2015–24  │ │
│ │ MALUKU UTARA   │ Eastern ID    │ Rp ~~~~~  │ +~~%    │ 2015–24  │ │
│ │ SULAWESI UTARA │ Sulawesi      │ Rp ~~~~~  │ +~~%    │ 2015–24  │ │
│ │ ...            │ ...           │ ...       │ ...     │ ...      │ │
│ │ JAWA BARAT     │ Java          │ Rp ~~~~~  │ +~~%    │ 2007–24  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [7a] Default: shows all provinces, sorted by vs Java descending    │
│  [7b] Clicking island group KPI card [4] or map [5] filters rows   │
│  [7c] Coverage column: shows actual date range for that province    │
│       — transparent about data gaps                                 │
│  [7d] "vs Java" column: red if above, green if below Java price     │
│  [7e] Provinces with <12 months coverage excluded and noted         │
│       in table footer                                               │
│  [7f] TanStack Table — sortable                                     │
│  [7g] Responds to Commodity filter                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layout — Mobile (390px)

```
┌────────────────────────────┐
│ NAV                  [≡]   │
├────────────────────────────┤
│ H1: Geographic Disparity   │
├────────────────────────────┤
│ FILTERS (stacked)          │
│ [Commodity ▼]              │
│ [Island Group ▼]           │
│ Year: [2007]────[2024]     │
├────────────────────────────┤
│ KPI CARDS (horizontal      │
│ scroll — 5 cards)          │
├────────────────────────────┤
│ MAP                        │
│ Full width, height 220px   │
│ Pinch to zoom              │
│ Year slider below map      │
├────────────────────────────┤
│ LINE CHART (island groups) │
│ Full width, height 220px   │
│ Legend below               │
├────────────────────────────┤
│ PROVINCE TABLE             │
│ Horizontal scroll          │
│ Sticky province column     │
└────────────────────────────┘
```

---

## States

| State | Behavior |
|-------|----------|
| **Loading** | Skeleton map placeholder (gray rectangle), skeleton cards and charts |
| **Map: island group clicked** | That group highlighted with border; KPI card for that group gets focus ring; province table filtered to that group |
| **Year slider moved** | Map recolors to show price index for selected year; KPI cards update |
| **Animate playing** | Map colors animate year by year; slider thumb moves; Animate button becomes Pause |
| **Island Group filter = specific group** | Province table filtered; map highlights that group; other charts unchanged |
| **Commodity changed** | All components redraw — map, line chart, KPI cards, province table |
| **Province with limited coverage** | Coverage column shows "2015–24" in lighter text; tooltip explains coverage gap |

---

## Annotations

| # | Element | Note |
|---|---------|------|
| 4 | KPI cards | Five cards is one more than the pharmacy project's three — horizontal scroll on mobile is acceptable here because island groups are the primary analytical unit |
| 5 | Map | Most visually impressive element in the project. The year animation is the feature that will make a hiring manager say "oh that's clever." Test it thoroughly |
| 5 | Coverage note | "Province-level detail available below for groups with sufficient coverage" must be visible without scrolling — it sets expectations before the user reaches the table |
| 6 | Gap trend line | Whether Eastern Indonesia's premium is narrowing (logistics improving) or widening (structural isolation) is the most interesting geographic finding. Make the trend direction readable at a glance |
| 7 | Coverage column | This column is an act of analytical honesty. Hiding data gaps would be easier — showing them explicitly demonstrates data quality discipline that hiring managers notice |

---

## Content Specifications

| Element | Source | Format |
|---------|--------|--------|
| Island group KPI data | `geographic_disparity.json → current_index[]` | `{island_group, index, premium_pct}` |
| Choropleth map data | `geographic_disparity.json → annual_index[]` | `{year, island_group, index}` — for year slider |
| GeoJSON boundaries | Bundled in `/dashboard/public/indonesia_island_groups.geojson` | Simplified polygon boundaries |
| Line chart data | `geographic_disparity.json → annual_index[]` | Same array as map, pivoted to wide format client-side |
| Province table | `geographic_disparity.json → province_detail[]` | `{province, island_group, avg_price, vs_java_pct, coverage_start, coverage_end}` |
