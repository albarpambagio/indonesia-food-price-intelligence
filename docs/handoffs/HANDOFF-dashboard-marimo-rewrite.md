# Handoff: Dashboard Marimo Rewrite (Native UI, No Vizro Patterns)

**Generated:** 2026-06-05 15:21 (updated with wireframe specifics)
**Trigger:** Agent was asked to plan and prepare execution of a full Marimo-native dashboard rewrite, replacing Vizro-derived visual hacks with proper Marimo UI components (`mo.stat()`, `mo.callout()`, etc.).

---

## Context

Previous handoff (`docs/handoffs/HANDOFF-vizro-to-marimo-migration.md`) already migrated from Vizro/Dash to a single Marimo notebook (`dashboard/app.py`). Chart functions still carried old patterns that look "very bad visually":

- **KPI cards** via Plotly `make_subplots` with annotation text overlays
- **Signal badges** via Plotly annotations on an invisible chart
- **Action cards** via Plotly annotations with background/border colors
- **YoY bar chart** replaced by `mo.ui.table` with emoji indicators (per wireframes)
- **Info boxes** via `mo.md("> ...")` blockquotes
- **Last cell bug**: `mo.hstack` + `mo.ui.tabs` were intermediate expressions, not final

User created detailed wireframes at `docs/wireframes/marimo-wireframe-*.md` (5 files). This handoff incorporates all wireframe-driven architecture decisions.

---

## Architecture (Per Wireframes)

### File Layout at Runtime (WASM)

```
dist/
├── index.html          ← marimo export html-wasm output
├── data/               ← copied from dashboard/public/data/
│   ├── price_trends.json
│   ├── forecast.json
│   ├── seasonal_patterns.json
│   ├── geographic_disparity.json
│   ├── commodity_correlation.json
│   └── correlation_summary.json
└── assets/
    └── indonesia_provinces.geojson
```

**Dual path resolution:** Local dev uses `dashboard/public/data/*.json`. Build script copies to `dist/data/`. The WASM runtime sees `data/*.json` (relative to index.html). `data_static.py` resolves via `Path(__file__).parent / "public" / "data"` for local; for WASM, `data/` is relative to the HTML file.

### Cell DAG (Granular — Not Monolithic)

```
imports
    ↓
data_loading (8 JSONs + islamic calendar CSV)
    ↓
global_filters          ← commodity_dd, island_dd, year_slider
    ↓
    ├── Page 1 cells:
    │   ├── page1_derived_data       ← filters + computes latest/yoy
    │   ├── kpi_cards                ← mo.stat() × 4 + sparkline charts
    │   ├── chart_commodity_radio    ← mo.ui.radio local to trend chart
    │   ├── trend_chart              ← mo.ui.plotly(go.Figure) with forecast
    │   ├── buy_signal_monitor       ← mo.md() with colored dots (native)
    │   ├── yoy_table                ← mo.ui.table with emoji flags
    │   └── footnote                 ← mo.callout(kind="info")
    │
    ├── Page 2 cells:
    │   ├── driver_toggle            ← mo.ui.radio (Ramadan/Harvest/Year-End/All)
    │   ├── action_cards             ← mo.stat() with mo.hstack()
    │   ├── data_notice              ← mo.callout(kind="info")
    │   ├── gregorian_heatmap        ← go.Heatmap(colorscale="Blues")
    │   ├── driver_chart             ← if/elif pattern: ramadan/harvest/yearend
    │   └── summary_table            ← mo.ui.table(sortable=True)
    │
    ├── Page 3 cells:
    │   ├── selected_island_state    ← mo.state("All") — cross-filter
    │   ├── kpi_cards_map            ← mo.ui.button(on_click=set_selected_island) × 5
    │   ├── map_year_slider          ← mo.ui.slider(2007–2024)
    │   ├── choropleth_map           ← mo.ui.plotly(px.choropleth)
    │   ├── island_line_chart        ← mo.ui.plotly(go.Scatter)
    │   └── province_table           ← mo.ui.table filtered by selected_island
    │
    ├── Page 4 cells:
    │   ├── selected_pair_state      ← mo.state(("Rice","Oil"))
    │   ├── lag_selector             ← mo.ui.radio({0,1,2,3})
    │   ├── leading_indicator_cards  ← mo.hstack(mo.vstack styled cards)
    │   ├── correlation_matrix       ← mo.ui.plotly(go.Heatmap)
    │   ├── pair_selector_dd         ← leader_dd + follower_dd → sync to state
    │   ├── pair_scatter             ← mo.ui.plotly(go.Scatter) pre/post 2022
    │   ├── stability_chart          ← mo.ui.plotly(go.Scatter) rolling r
    │   ├── implication_card         ← mo.callout(kind="warn"/"info")
    │   └── detail_table             ← mo.ui.table(on_select=...) → sync to state
    │
    └── tab_assembly_cell           ← mo.ui.tabs({4 tabs}) as FINAL expression
```

### mo.state() Usage (Two Instances)

| State | Page | Sources | Consumers | Why mo.state() |
|-------|------|---------|-----------|----------------|
| `selected_island` | 3 | KPI button `on_click`, choropleth map click | Province drill-down table | Two UI elements write to one shared value |
| `selected_pair` | 4 | Matrix click, pair dropdowns, table `on_select` | Scatter, stability, implication card | Three UI sources → one sink |

All other reactivity flows through marimo's normal DAG (widget `.value` as cell arguments).

---

## Per-Page Wireframe Details

### Page 1 — Price Trends

| Section | Component | Implementation |
|---------|-----------|---------------|
| KPI cards | `mo.hstack` of `mo.stat()` | `mo.stat(value=f"Rp {price:,.0f}", label="Rice", caption="↑ +3.2% YoY", bordered=True, slot=mo.ui.plotly(sparkline))`. Sparkline = tiny `go.Scatter` with axes hidden, height ~60px. Red ↑ / green ↓ via f-string |
| Trend chart | `mo.ui.plotly(go.Figure)` | Local `chart_commodity_radio` independent of global `commodity_dd`. 17yr actual line + 6mo forecast dashed + 95% CI fill. Vertical separator at forecast start. 2022 structural break annotation |
| Buy signal monitor | `mo.md()` with inline HTML | Colored dots: `● BUY NOW` (green), `● HOLD` (gray), `● WATCH` (orange). No Plotly annotations |
| YoY table | `mo.ui.table` | Annual % change per commodity. Pre-format values with emoji: `"+12.3% 🔴"`, `"-2.1% 🟢"`. Columns: year, rice_pct, oil_pct, sugar_pct, flour_pct |
| Footnote | `mo.callout(kind="info")` | Model limitations plain language |

### Page 2 — Seasonal

| Section | Component | Implementation |
|---------|-----------|---------------|
| Driver toggle | `mo.ui.radio` | Horizontal button group. Options: "Ramadan / Lebaran", "Harvest Season", "Year-End", "All Drivers". Default: Ramadan |
| Action cards | `mo.stat()` in `mo.hstack` | Reads `action_windows_df` filtered by driver. Sort by abs(spike_pct) descending. Skip rows with abs < 3% threshold. Show `🛒 Commodity: +X.X%` |
| Data notice | `mo.callout(kind="info")` | "Seasonal analysis uses national-level data for Rice, Sugar, Flour. Island breakdown for Cooking Oil only." |
| Gregorian heatmap | `go.Heatmap(colorscale="Blues", zmid=0)` | 4×12 matrix. Single-hue white→dark scale centered at zero. Text shows ±%. Always shown regardless of driver |
| Driver chart | `if/elif` in one cell | Ramadan: multi-year overlay with 17yr avg bold line. Harvest: Rice bar chart with green/blue months. Year-End: commodity premium bar chart. All Drivers: info text |
| Summary table | `mo.ui.table(sortable=True)` | Sorted by abs(premium_pct). Pre-format negatives with 🟢, positives with 🔴 |

### Page 3 — Geographic

| Section | Component | Implementation |
|---------|-----------|---------------|
| Data banner | `mo.callout(kind="warn")` | "Only Cooking Oil has province-level prices. Rice/Sugar/Flour national only." Always visible |
| KPI cards | `mo.ui.button(on_click=...)` | 5 buttons, one per island group. Java = baseline (no %). Others: `↑ X.X% vs Java` or `↓ X.X% vs Java`. Clicking calls `set_selected_island(name)` |
| Map year slider | `mo.ui.slider(2007–2024)` | Page-specific. Manual only (no animation). Animatable in Phase 2 via `mo.state` + `time.sleep()` loop |
| Choropleth map | `mo.ui.plotly(px.choropleth)` | GeoJSON from `assets/indonesia_provinces.geojson`. Colorscale="Blues". Click calls `set_selected_island(clicked)`. Not rendered for non-Oil commodities |
| Island line chart | `mo.ui.plotly(go.Scatter)` | One line per island group over time. Java dashed gray. Y-axis > 90 to show small gaps |
| Province table | `mo.ui.table` | Filtered by `selected_island()`. Shows province, island_group, avg_price, vs Java (pre-formatted with emoji), coverage date range |

### Page 4 — Commodity Signals

| Section | Component | Implementation |
|---------|-----------|---------------|
| Island notice | `mo.callout(kind="info")` | "Island Group filter disabled on this page — correlation analysis is national level." Global dropdown stays enabled |
| Lag selector | `mo.ui.radio` | Options dict: `{"0 months": 0, "1 month": 1, "2 months": 2, "3 months": 3}`. Default: 1 |
| Leading indicator cards | `mo.hstack` of `mo.vstack` styled cards | Top 2 relationships by r at selected lag. Each card: `📈 Leader → Follower`, `r = X.XX`, `✅ Stable` / `⚠ Weakened post-2022`, plain-language implication text |
| Correlation matrix | `mo.ui.plotly(go.Heatmap)` | 4×4. Row = leader, column = follower. colorscale="Blues". Diagonal = None (white). Annotation: "Row commodity leads column commodity". Click updates `selected_pair` |
| Pair scatter | `mo.ui.plotly(go.Scatter)` | Pre-2022 blue dots, Post-2022 red dots. OLS trend line. Read from `selected_pair()` |
| Rolling stability | `mo.ui.plotly(go.Scatter)` | 3yr rolling r. Horizontal line at r=0.3. Vertical line at 2022 shock |
| Pair selector dropdowns | `mo.hstack([leader_dd, "→", follower_dd])` | Reads `selected_pair()[0]` as default. Changes sync back to state via downstream cell |
| Implication card | `mo.callout(kind="warn"/"info")` | Plain language only. No r-values. ⚠ warning if `abs(pre_r - post_r) > 0.2` is non-negotiable |
| Detail table | `mo.ui.table(on_select=...)` | All pairs at selected lag. Columns: leader, follower, r, pre_2022_r, post_2022_r, stability (✅/⚠). Row click updates `selected_pair` via `on_select` |

---

## Tab Labels (Match Wireframes)

| Label | Tab Content Variable |
|-------|---------------------|
| "Price Trends" | `page1_content` |
| "Seasonal" | `page2_content` |
| "Geographic" | `page3_content` |
| "Commodity Signals" | `page4_content` |

---

## Files to Modify

| File | Change |
|------|--------|
| `dashboard/charts/kpi_sparklines.py` | Rewrite → export `sparkline_chart()` returning tiny `go.Figure` (axes hidden, ~60px height). One trace per commodity. No annotations, no subplots, no KPI text |
| `dashboard/charts/seasonal_heatmap.py` | Rewrite → use `go.Heatmap(colorscale="Blues", zmid=0)` instead of `px.imshow(RdBu_r)` |

## Files to Delete

| File | Reason |
|------|--------|
| `dashboard/charts/signal_badges.py` | Replaced by `mo.md()` with inline HTML colored dots |
| `dashboard/charts/action_cards.py` | Replaced by `mo.stat()` in `mo.hstack()` |
| `dashboard/charts/yoy_bar.py` | Replaced by `mo.ui.table` with emoji indicators |

## Files to Create

| File | Source |
|------|--------|
| `dashboard/public/data/islamic_calendar.csv` | Copy from `transform/seeds/islamic_calendar.csv` |

## Files to Keep (as-is)

| Asset | Path |
|-------|------|
| JSON data loader | `dashboard/data_static.py` |
| Pandas compute helpers (5 functions) | `dashboard/data_access.py` |
| WASM build script | `dashboard/build.py` |
| Static JSON data (7 files) | `dashboard/public/data/*.json` |
| GeoJSON | `dashboard/assets/indonesia_provinces.geojson` |
| `trend_forecast.py` | Clean Plotly — unchanged |
| `ramadan_overlay.py` | Plotly — keep (called by driver_chart assembly) |
| `harvest_chart.py` | Plotly — keep (called by driver_chart assembly) |
| `yearend_chart.py` | Plotly — keep (called by driver_chart assembly) |
| `correlation_charts.py` | Plotly — keep (all 4 functions used) |
| `geo_charts.py` | Plotly — keep (all 3 functions used) |
| `seasonal_summary_table.py` | Returns pd.DataFrame — keep |

---

## Execution Notes

- **Marimo version:** 0.23.7 — `mo.stat()`, `mo.callout()`, `mo.style()`, `mo.accordion()` all available
- **Run commands:** `uv run marimo edit dashboard/app.py` (interactive), `uv run python dashboard/app.py` (script mode)
- **WASM export:** `marimo export html-wasm dashboard/app.py -o dist/index.html --mode run -f`
- **Linting:** `ruff check dashboard/` — existing E501/F821 false positives safe to ignore
- **Type checking:** `ruff check` only; `ty` cannot resolve marimo cross-cell scoping
- **PEP 723 header** must be at top of `app.py`
- **All chart functions already stripped of `@capture` decorators** — no Vizro dependencies remain
- **Final expression rule:** Every cell must have its output as the last expression (bare `chart` or `fig`, not `mo.ui.plotly(fig)` as intermediate)
- **No `if` cell guards:** Use `if/elif` pattern (assign to variable, return last) not `if` around final expression
- **No `try/except` for control flow:** Let errors surface naturally

---

## Validation

- [ ] `marimo check dashboard/app.py` passes
- [ ] `ruff check dashboard/` clean (false positives OK)
- [ ] `uv run python dashboard/app.py` script mode exits cleanly
- [ ] `marimo export html-wasm dashboard/app.py -o /tmp/test.html --mode run -f` succeeds
- [ ] All 4 tabs render in browser with correct data
- [ ] Global filters update charts reactively
- [ ] Page 3 KPI card click → province table updates
- [ ] Page 4 matrix click → scatter/stability/implication updates
- [ ] `mo.stat()` KPI cards render with prices + YoY arrows
- [ ] `mo.callout()` info boxes visible on each page

---

## Suggested Skills

| Skill | When to Use |
|-------|-------------|
| `marimo-notebook` | When writing/editing `app.py` notebook cells — cell structure patterns, UI component reference, script mode patterns, `mo.stop()` usage |
| `systematic-debugging` | If `marimo check` fails, chart rendering issues in WASM mode, or `mo.ui.plotly()` displays incorrectly |
| `cloudflare-pages-deploy` | After WASM export succeeds — for deploying `dist/` to Cloudflare Pages |
