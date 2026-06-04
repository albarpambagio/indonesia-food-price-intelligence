# Wireframe Spec — Page 1: YoY Inflation Chart Redesign
**Fidelity:** Annotated Mid-Fi with 5 Layout Options
**Audience:** Category Manager (primary), Procurement Analyst (secondary)
**Decision Enabled:** "When are prices rising/falling fastest, and which commodities are driving inflation?"
**Data Source:** `price_trends.json` (monthly prices → YoY% = year-over-year delta per commodity)

---

## Current Implementation (Baseline)

Grouped bar chart: 4 commodity groups side-by-side per month, height = year-over-year % change.

```
 Current: Single-grouped bar, all commodities overlaid
 ┌─────────────────────────────────────────────────────┐
 │  YoY ▲  Rice     Oil     Sugar    Flour             │
 │  +30%│ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██        │
 │  +20%│ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██        │
 │  +10%│ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██        │
 │    0%├──────────────────────────────────────────    │
 │  -10%│                                              │
 │      └──────────────────────────────────────────▶   │
 │       2010              2015              2020      │
 │                                                      │
 │  Legend: █ Rice  █ Cooking Oil  █ Sugar  █ Flour   │
 └─────────────────────────────────────────────────────┘
```

### Known Issues
1. **No hovertemplate** — default Plotly bar hover is unreliable after Vizro's clientside callback strips internal hover state
2. **Annotation colors baked in** — `font.color` and `line_color` survive Vizro theme swap
3. **All-commodity overload** — 4 grouped bars per month × 200+ months creates visual clutter

---

## Option A: Grouped Bar (Improved)

Current format with targeted fixes + reference bands.

```
 ┌─────────────────────────────────────────────────────┐
 │  YoY ▲                                               │
 │  +30%│──────────────────────────────────────────     │  ← +2σ band
 │      │    ██       ██                                │
 │  +20%│ ██ ██ ██    ██ ██ ██                         │
 │      │ ██ ██ ██ ██ ██ ██ ██ ██                      │
 │  +10%│ ██ ██ ██ ██ ██ ██ ██ ██ ██                   │
 │    0%├═══════════════════════════════════════════    │  ← zero line (thick)
 │  -10%│                                              │
 │      └──┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──▶   │
 │       2014 2015 2016 2017 2018 2019 2020 2021 2022   │
 │                                                      │
 │  Legend: █ Rice  █ Cooking Oil  █ Sugar  █ Flour   │
 │  Tooltip: Rice | Jan 2022 | YoY: +12.3%             │
 └─────────────────────────────────────────────────────┘
```

| # | Element | Note |
|---|---------|------|
| A1 | Horizontal reference bands | ±1σ, ±2σ bands at 10%/20%/30% — contextualize spike severity |
| A2 | Thick zero line | `line_width=2`, dark gray — visual anchor for inflation vs deflation |
| A3 | Per-trace hovertemplate | `<b>{name}</b><br>{x:%b %Y}<br>YoY: {y:+.1f}%` — survives Vizro callback |
| A4 | 12-month rolling x-axis | Show only 10-12 years at a time (reduces bar density) |
| A5 | Theme-adaptive colors | Remove explicit `font.color`, use `rgba(128,128,128,0.3)` for lines |

### Trade-offs
- **+** Minimal code change from current implementation
- **+** Familiar visual for procurement analysts
- **-** Still cluttered when all 4 commodities shown simultaneously
- **-** Bar group overlap at monthly grain is inevitable

---

## Option B: Faceted Bars Per Commodity

2×2 subplot grid, one commodity per panel, independent y-axes.

```
 ┌─────────────────────┐  ┌─────────────────────┐
 │  Rice                │  │  Cooking Oil         │
 │  YoY ▲               │  │  YoY ▲               │
 │  +20%│ ██ ██ ██ ██   │  │ +100%│ ██ ██ ██ ██   │
 │    0%├───────────    │  │   0%├───────────    │
 │      └──────────▶    │  │     └──────────▶    │
 │      2015     2020   │  │     2015     2020   │
 ├─────────────────────┤  ├─────────────────────┤
 │  Sugar               │  │  Flour               │
 │  YoY ▲               │  │  YoY ▲               │
 │  +15%│ ██ ██ ██ ██   │  │  +10%│ ██ ██ ██ ██   │
 │    0%├───────────    │  │    0%├───────────    │
 │      └──────────▶    │  │     └──────────▶    │
 │      2015     2020   │  │     2015     2020   │
 └─────────────────────┘  └─────────────────────┘
```

| # | Element | Note |
|---|---------|------|
| B1 | Shared x-axis | All 4 panels share same time range for cross-comparison |
| B2 | Independent y-axes | Cooking Oil needs wider range (+100%) vs Flour (+10%) |
| B3 | Single bar per panel | No grouping — one commodity per panel, bar = monthly YoY% |
| B4 | Commodity header | Bold label top-left of each panel |
| B5 | Zero line per panel | Thin dashed line at 0% in each subplot |

### Trade-offs
- **+** Every bar visible without overlap
- **+** Independent y-scales respect each commodity's volatility
- **+** Procurement analyst can scan all 4 at once
- **-** 4 small panels — harder to see overall inflation trend across commodities
- **-** Less horizontal space per commodity means fewer months visible

---

## Option C: YoY as Overlay Lines

Thin lines overlaid on the main trend+forecast chart background, using secondary y-axis.

```
 ┌─────────────────────────────────────────────────────┐
 │  Price (IDR) ▲                                       │
 │  15K ┌───────────────────────────────────────        │
 │       │                      ╭────                    │
 │  10K ─│──────────────╭───────╯                       │
 │       │      ╭───────╯                               │
 │   5K ─│─────╯                                        │
 │       │ ╭────                                        │
 │    0K └──────────────────────────────────────────▶   │
 │       2007  2010  2013  2016  2019  2022  2024       │
 │                                                      │
 │  ─────────────────────────────────────────────       │
 │  YoY overlay (secondary axis) ▲                      │
 │  +30%│              ╭──╮              ╭──           │
 │  +20%│    ╭──╮  ╭──╯  ╰──╮  ╭──╮  ╭──╯             │
 │  +10%│ ╭──╯  ╰──╯       ╰──╯  ╰──╯                │
 │    0%├──────────────────────────────────────────    │
 │      └──────────────────────────────────────────▶   │
 │       2007  2010  2013  2016  2019  2022  2024       │
 │                                                      │
 │  ─── Rice  ─── Cooking Oil  ─── Sugar  ─── Flour     │
 └─────────────────────────────────────────────────────┘
```

| # | Element | Note |
|---|---------|------|
| C1 | Dual y-axis | Primary = price (IDR), Secondary = YoY% |
| C2 | Thin lines | `width=1.5`, muted opacity — complementary, not dominant |
| C3 | Linked legend | Same color per commodity matches main trend lines |
| C4 | Zero line | Dashed line across YoY overlay pane |
| C5 | Collapsible | Default collapsed — user toggles YoY overlay on/off |

### Trade-offs
- **+** Directly connects price level with inflation rate — "price is high AND rising fast"
- **+** No extra page real estate consumed
- **+** Category Manager sees price + inflation in one view
- **-** Dual y-axis can confuse non-technical users
- **-** YoY lines may visually compete with price trend lines
- **-** Requires more sophisticated chart construction (shared x-axis, dual y)

---

## Option D: Year × Commodity Heatmap

Grid: rows = year, columns = commodity, cell color = YoY% for that year.

```
 ┌──────────────────────────────────────────────┐
 │  Year │ Rice  │ Oil   │ Sugar │ Flour        │
 ├──────┼───────┼───────┼───────┼───────┤       │
 │ 2024 │ +3.2% │ -0.8% │ +5.1% │ +2.0% │  ← ▼  hottest
 │ 2023 │ +1.1% │ +8.4% │ +2.2% │ +1.5% │  ↓    │
 │ 2022 │ +7.5% │+42.1% │+12.3% │ +6.8% │  │    │
 │ 2021 │ -2.1% │+15.2% │ +3.0% │ +0.5% │  │    │
 │ 2020 │ +1.8% │ -3.5% │ -1.2% │ +2.2% │  │    │
 │ 2019 │ +3.0% │ +2.1% │ +0.8% │ -0.3% │  │    │
 │ 2018 │ +4.2% │ +1.5% │ +2.5% │ +1.0% │  │    │
 │ 2017 │ +2.5% │ -0.2% │ +1.8% │ +3.5% │  ▲    │
 │  ... │  ...  │  ...  │  ...  │  ...  │       │
 │ 2008 │+15.0% │+25.0% │+10.0% │+12.0% │  ← 2008 crisis
 │ 2007 │ +5.0% │ +3.0% │ +8.0% │ +6.0% │       │
 └──────┴───────┴───────┴───────┴───────┘       │
                                                 │
  Color scale: ■ < -5%  ■ -5%–0%  ■ 0–5%  ■ 5–15%  ■ >15%
  (Red→White→Green divergent)
```

| # | Element | Note |
|---|---------|------|
| D1 | Divergent color scale | Red = deflation, White = stable, Green = inflation |
| D2 | Numeric annotation | Cell shows exact YoY% value + arrow icon |
| D3 | Hover detail | Tooltip: "Cooking Oil · 2022 · +42.1% (structural break: export ban)" |
| D4 | Year axis | Reverse-chronological (newest at top) — procurement cares about recent |
| D5 | Color threshold legend | 5-bucket divergent scale explained below heatmap |

### Trade-offs
- **+** Best for spotting patterns: which years had broad inflation? Which commodities broke out?
- **+** 2022 Cooking Oil spike jumps out immediately
- **+** Compact — fits in small real estate
- **+** No monthly grain noise — yearly aggregation is decision-relevant for contract timing
- **-** Loses monthly granularity (seasonal patterns within year invisible)
- **-** Less familiar chart type for procurement audience

---

## Option E: Small Multiples Calendar (Vertical Stack)

Vertical column of mini bar charts, one per commodity. Each commodity gets full width, shorter height.

```
 ┌────────────────────────────────────────────────┐
 │  Rice                                            │
 │  ▲ YoY                                           │
 │  │  ██ ██ ██    ██ ██ ██    ██ ██ ██            │
 │  │  ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██        │
 │  ├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──▶  │
 │  '14 '15 '16 '17 '18 '19 '20 '21 '22 '23 '24    │
 │                                                  │
 │  Cooking Oil                                      │
 │  ▲                                                │
 │  │       ██                                      │
 │  │       ██ ██ ██ ██ ██ ██ ██ ██ ██ ██          │
 │  │ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██      │
 │  ├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──▶  │
 │  '14 '15 '16 '17 '18 '19 '20 '21 '22 '23 '24    │
 │                                                  │
 │  Sugar                                            │
 │  ▲                                                │
 │  │    ██ ██    ██ ██ ██    ██ ██ ██ ██          │
 │  │ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██      │
 │  ├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──▶  │
 │  '14 '15 '16 '17 '18 '19 '20 '21 '22 '23 '24    │
 │                                                  │
 │  Flour                                            │
 │  ▲                                                │
 │  │       ██          ██          ██              │
 │  │ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██ ██      │
 │  ├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──▶  │
 │  '14 '15 '16 '17 '18 '19 '20 '21 '22 '23 '24    │
 └────────────────────────────────────────────────┘
```

| # | Element | Note |
|---|---------|------|
| E1 | Shared x-axis range | All charts aligned to same time window for cross-comparison |
| E2 | Consistent y-scale | Same YoY% range per commodity (auto-scaled per panel) |
| E3 | Commodity label | Left-aligned bold name, top of each panel |
| E4 | Zero line | Thin line at 0% per panel |
| E5 | Collapsible sections | Default show 4; user can collapse/expand individual commodities |

### Trade-offs
- **+** Each commodity gets full attention — no visual interference
- **+** Vertical scrolling is natural for procurement workflow
- **+** Scales well if more commodities added later
- **+** Each bar is large enough for accurate reading
- **-** Requires more vertical space than grouped bar
- **-** Cannot see cross-commodity monthly correlation at a glance

---

## Comparison Matrix

| Criteria | A (Improved) | B (Faceted) | C (Overlay) | D (Heatmap) | E (Multiples) |
|----------|:------------:|:-----------:|:-----------:|:-----------:|:-------------:|
| Cross-commodity comparison | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Monthly granularity | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| Spike visibility | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Code change from current | ⭐⭐⭐⭐⭐ (minimal) | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ |
| Space efficiency | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Audience familiarity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| Category Manager decision-readiness | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### Recommendation

**Option D (Heatmap)** scores highest on decision-readiness for the Category Manager — the key question is "when did inflation spike and for which commodity?" and the heatmap answers that in one glance. **Option A (Improved)** is the lowest-risk evolution: fix the hover, add reference bands, ship today. Recommended path: ship A first (30-min fix), then build D as the Phase 7 enhancement.

---

## States

| State | Behavior |
|-------|----------|
| **Loading** | Gray skeleton matching selected layout shape |
| **All commodities** | All 4 series shown per layout design |
| **Single commodity** | Filtered to one (e.g. Rice) — heatmap shows 1 column, faceted shows 1 panel, multiples shows 1 row |
| **No data for period** | Empty state: "No price data for selected filters" |
| **Hover** | Tooltip with commodity, date, exact YoY% (±CI if applicable) |
| **Theme toggle (light/dark)** | All explicit colors removed — Vizro template controls font/line colors |
