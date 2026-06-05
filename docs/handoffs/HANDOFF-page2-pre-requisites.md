# Handoff: Page 2 Pre-Requisites

**Generated:** 2026-06-05 10:40
**Context:** Conversation about what tasks must be completed before building Page 2 (Seasonal Patterns) in Vizro. User asked for a task inventory; analysis produced a 7-item checklist with constraints.

---

## Current State

- **Page 1 (Price Trends & Forecast):** Built and bugfixed (4 sessions documented in `HANDOFF-page1-bugs-and-learnings.md`, `HANDOFF-page1-completion.md`, `HANDOFF-page1-hover-theme-wireframe.md`)
- **Data layer:** `dashboard/data_manager.py` registers all 6 marts + forecast. `dashboard/data_access.py` has `load_mart()`, `load_forecast_data()`, `compute_yoy_delta()`, `get_latest_prices()`
- **Page 2 handoff:** `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` — full execution plan with data sources, chart signatures, conditional visibility, filter patterns, pitfalls
- **Implementation plan:** `docs/implementation-plan.md` §6.C.2 — 12 tasks (6.C.2.1 through 6.C.2.6), all ⬜

---

## Tasks Before Building Page 2

### Task 1: Extend `dashboard/data_access.py` — 3 new helpers

Per handoff §5, these must exist before chart files can import them:

```python
def compute_action_windows(df_national, driver, islamic_cal) -> pd.DataFrame:
    """Per-commodity: spike_pct, consistency_score, total_years, lead_months, data_scope"""

def compute_heatmap_matrix(df_national) -> pd.DataFrame:
    """4×12 matrix: commodity × month_of_year, values = mean premium % vs annual avg"""

def compute_ramadan_overlay(df_national, commodity, islamic_cal) -> pd.DataFrame:
    """Long DF: {year, month_relative, price_index} where month_relative ∈ [-2, +1]"""
```

Also need to load `int_islamic_calendar` from DuckDB (for Ramadan overlay and action windows). Follow existing `_connect()` pattern.

**Formulas** (from handoff §5):
- `spike_pct = (mean(price_index during driver months) - mean(non_driver)) / mean(non_driver) * 100`
- `consistency_score = count(years where avg_driver > avg_annual) / total_years_with_data`
- `month_relative = (price_month_year * 12 + price_month_num) - (eid_year * 12 + eid_month_num)`

### Task 2: Create 5 chart files in `dashboard/charts/`

| File | Capture decorator | Primary source | Notes |
|------|-------------------|-----------------|-------|
| `seasonal_heatmap.py` | `@capture("graph")` | `mart_price_trends_national` → `compute_heatmap_matrix()` | `px.imshow`, `color_continuous_scale` per wireframe [5b] |
| `ramadan_overlay.py` | `@capture("graph")` | `mart_price_trends_national` + `int_islamic_calendar` | Multi-year line, bold avg, 2022 outlier label |
| `harvest_chart.py` | `@capture("graph")` | `mart_price_trends_national` (Rice only) | Harvest vrect shading |
| `yearend_chart.py` | `@capture("graph")` | `mart_price_trends_national` (Nov–Dec) | 4-commodity bar |
| `seasonal_summary_table.py` | **`@capture("ag_grid")`** | `compute_action_windows()` × 3 drivers | NOT `@capture("graph")` — see pitfall #6 |

All 3 conditional charts (ramadan, harvest, yearend) use **Pattern A** (empty-figure swap): return `_empty_collapsed_fig()` when `driver != "their driver"`. Helper:

```python
def _empty_collapsed_fig() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        height=1, margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
```

Reference patterns: `dashboard/spike/custom_charts.py` (px.imshow), `dashboard/charts/trend_forecast.py` (CI fill, vline, annotation).

### Task 3: Create `dashboard/pages/seasonal_patterns.py`

`vm.Page` config with:
- Action cards row (3 `vm.Card` markdown + data-availability callout)
- Heatmap (always visible, all 4 commodities)
- 3 conditional charts (Ramadan / Harvest / Year-End, Pattern A toggle)
- Summary table (`vm.AgGrid`)
- Driver toggle: `vm.Parameter` + `vm.RadioItems`
- Commodity + Island dropdowns: `vm.Parameter` (§97 — "All" sentinel)
- Year Range slider: `vm.Filter(column="month", selector=vm.RangeSlider(...), show_in_url=True)`
- All filters set `show_in_url=True`

### Task 4: Register Page 2 in `dashboard/app.py`

```python
from dashboard.pages.seasonal_patterns import seasonal_patterns_page
dashboard = vm.Dashboard(pages=[price_trends_page, seasonal_patterns_page])
```

### Task 5: Smoke tests

```bash
uv run python -c "from dashboard.app import dashboard; print(len(dashboard.pages))"  # → 2
uv run python -c "from dashboard.app import dashboard; print([p.title for p in dashboard.pages])"
uv run python -c "from dashboard.charts.seasonal_heatmap import seasonal_heatmap; from dashboard.data_access import load_mart; fig = seasonal_heatmap(load_mart('mart_price_trends_national')); print('traces:', len(fig.data))"
```

### Task 6: Lint & format

```bash
ruff check .
ruff format --check .
```

---

## Key Constraints (from handoff §12)

| # | Constraint | Source |
|---|-----------|--------|
| 1 | Primary source is `mart_price_trends_national` (639 rows, all 4), NOT `mart_seasonal_patterns` (35 rows, Cooking Oil only) | LEARNINGS §99 |
| 2 | Rice/Sugar/Flour national prices end **2020-03** — must disclose or filter | DuckDB query |
| 3 | `month_relative` T-2 to T+1 (monthly grain, not weekly T-8 to T+6) | LEARNINGS §100 |
| 4 | `COMMODITY_COLORS` must match Page 1: `#4C72B0`, `#DD8452`, `#55A868`, `#C44E52` | Page 1 charts |
| 5 | Never pass literal default args in `vm.Graph(figure=fn(...))` | LEARNINGS §98 |
| 6 | `vm.Parameter` not `vm.Filter` for dropdowns containing "All" | LEARNINGS §97 |
| 7 | `vm.AgGrid` requires `@capture("ag_grid")`, not `@capture("graph")` | Vizro 0.1.53 API |
| 8 | Island filter only applies to Cooking Oil — silently ignore for other commodities | Handoff §6 |

---

## Files NOT to Modify

| File | Reason |
|------|--------|
| `dashboard/data_access.py` (existing functions) | Extend only; don't change signatures |
| `dashboard/data_manager.py` | Already correct, all 6 marts registered |
| `transform/` (any dbt model) | Complete, 77 tests pass |
| `dashboard/charts/*.py` for Page 1 | Working code |
| `dashboard/pages/price_trends.py` | Working code |
| `docs/wireframes/*` | Reference only |

---

## Reference Artifacts

| What | Path |
|------|------|
| Page 2 full handoff | `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` |
| Phase C handoff | `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md` |
| Implementation plan §6.C.2 | `docs/implementation-plan.md` (lines 470–484) |
| Vizro learnings §87–100 | `docs/LEARNINGS.md` |
| Page 1 reference code | `dashboard/pages/price_trends.py` + `dashboard/charts/*.py` |
| Wireframe spec | `docs/wireframes/wfp-wireframe-page2-seasonal-patterns.md` |
| Spike reference (px.imshow) | `dashboard/spike/custom_charts.py` |

---

## Suggested Skills

1. **`brainstorming`** — Confirm conditional-visibility approach (Pattern A) and chart function API shapes before coding
2. **`frontend-design`** — Build Vizro page layout: `vm.Container` grid, `vm.Card` action styling, `vm.Flex` column layout matching Page 1 visual rhythm
3. **`verification-before-completion`** — Run smoke tests §5 above before claiming done
4. **`polish`** — Final quality pass: alignment, color consistency with Page 1, heatmap color scale
5. **`clarify`** — Review UX copy: data-availability callout, calendar note on heatmap, 2022 outlier label, per-commodity date floor disclosure
