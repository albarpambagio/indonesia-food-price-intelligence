# Handoff: Page 1 Completion — Vizro Price Trends & Forecast

## Context

Indonesia Food Price Intelligence project — Vizro 0.1.53 dashboard migration. Page 1 (`dashboard/pages/price_trends.py`) has been partially ported from Dash to Vizro: the 4 custom chart files exist and the `vm.Page` loads. But it is missing filters, the model info card, and the footnote link. This session completes Page 1 before moving to Pages 2-4.

## Current State of Page 1

**Smoke test passes:** `from dashboard.app import dashboard` returns 1 page.

| File | LOC | Status | Notes |
|------|-----|--------|-------|
| `dashboard/app.py` | 25 | ✅ Vizro | `vm.Dashboard(pages=[price_trends_page])` |
| `dashboard/data_manager.py` | 23 | ✅ Vizro | 7 keys registered (6 marts + forecast) |
| `dashboard/data_access.py` | 117 | ✅ Keep | Framework-agnostic, `load_mart()`, `compute_yoy_delta()` |
| `dashboard/charts/trend_forecast.py` | 122 | ✅ Built | `@capture("graph")`, actuals + forecast + CI area + vline + vrect |
| `dashboard/charts/kpi_sparklines.py` | 129 | ✅ Built | 2×2 subplot, current price + YoY% + 24mo sparkline |
| `dashboard/charts/yoy_bar.py` | 60 | ✅ Built | Grouped bar, YoY% change per commodity |
| `dashboard/charts/signal_badges.py` | 102 | ✅ Built | BUY/HOLD/WATCH based on forecast vs current |
| `dashboard/pages/price_trends.py` | 74 | ⬜ Incomplete | Missing filters, model card, footnote link |

## Gaps to Close (Page 1 Only)

### Gap 1: Add `vm.Filter` controls (Commodity, Island Group, Year Range)

**Current:** `vm.Parameter` with `vm.Dropdown` for commodity only. No island or year filters.

**Target (wireframe [3]):**

```python
controls=[
    vm.Filter(
        column="commodity_consolidated",
        selector=vm.Dropdown(
            options=["All", "Rice", "Cooking Oil", "Sugar", "Flour"],
            value="All",
            multi=False,
        ),
        show_in_url=True,   # §89 — cross-page filter persistence
    ),
    vm.Filter(
        column="island_group",
        selector=vm.Dropdown(
            options=["All", "Java", "Sumatera", "Kalimantan", "Sulawesi", "Eastern Indonesia"],
            value="All",
            multi=False,
        ),
        show_in_url=True,
    ),
    # Year range as vm.Parameter (vm.Filter doesn't support range sliders natively)
    vm.Parameter(
        targets=["trend_forecast.data_frame", "yoy_bar.data_frame", "kpi_sparklines.data_frame", "signal_badges.data_frame"],
        selector=vm.RangeSlider(
            column="month",
            min="2007-01-01",
            max="2024-05-01",
            step="P1M",
            value=["2007-01-01", "2024-05-01"],
        ),
        show_in_url=True,
    ),
]
```

**Key decisions:**
- `vm.Filter` auto-filters all `data_frame` args of components on the page — no need to manually target each chart.
- `show_in_url=True` on every filter — ugly URLs but battle-tested cross-page state (LEARNINGS §89).
- Year range uses `vm.Parameter` with `vm.RangeSlider` because `vm.Filter` doesn't support dual-handle sliders.
- Island Group filter only affects Cooking Oil data. Rice/Sugar/Flour are national-level only — filter shows "all island groups" by default when those commodities selected (wireframe [3d]).
- Replace the existing `vm.Parameter(id="param-commodity", ...)` with `vm.Filter(column="commodity_consolidated", ...)`.

### Gap 2: Add forecast model info card

**Current:** Single `vm.Card` with limitations text only.

**Target (wireframe [5]):** Add a card showing per-commodity model selection and holdout MAE.

```python
vm.Container(
    children=[
        vm.Card(
            text="""
### Model Selection

| Commodity | Model | Holdout MAE |
|-----------|-------|-------------|
| Rice | AutoARIMA | 23 |
| Cooking Oil | AutoARIMA | 1,714 |
| Sugar | AutoETS | 89 |
| Flour | AutoETS | 23 |
            """,
        ),
        vm.Card(
            text="""
### Model Limitations

- Forecast uses AutoARIMA/AutoETS with 6-month horizon.
- 95% confidence intervals widen significantly at 5-6 months.
- Cooking Oil post-2022 structural break reduces forecast reliability.
- Forecast uses all price data (including aggregate flags); dashboard uses only 'actual' flag.
- No volume weighting — all markets equal weight.

[See methodology →](https://github.com/albarpambagio/wfp-food-price-intelligence/blob/main/docs/model_methodology.md)
            """,
        ),
    ],
    direction="horizontal",
)
```

**Key details:**
- Read model/MAE data from `forecast.json` metadata: `load_forecast_metadata()["models"]`.
- Populate the table dynamically, not hardcoded. Use `data_access.load_forecast_metadata()`.
- The limitations card merges with the footnote (wireframe [8]).
- "See methodology →" is a markdown link opening in new tab (wireframe [8b]).

### Gap 3: KPI sparklines — always show all 4 commodities

**Current:** When commodity filter ≠ "All", excluded commodities show "Filtered out" text.

**Target (wireframe [4d]):** "Four cards always shown regardless of filter — Rice highlighted with border."

**Change in `dashboard/charts/kpi_sparklines.py`:**
- Remove the `if commodity_filter != "All"` guard that hides filtered-out commodities.
- Instead, always compute all 4 sparklines.
- Add visual emphasis (thicker border / opacity) on the selected commodity when filter is active.
- The `commodity_filter` parameter should dim non-selected cards (lower opacity) rather than hide them.

### Gap 4: Commodity toggle should be inline, not separate dropdown

**Current:** `vm.Parameter` with `vm.Dropdown` in the controls panel.

**Target (wireframe [5]):** Inline toggle above the chart: `[Rice] [Cooking Oil] [Sugar] [Flour] [All]`

**Options:**
- (a) Keep `vm.Parameter` with `vm.RadioItems` (simpler, Vizro-native). The toggle appears in the controls panel, not inline on the chart. Acceptable for Vizro 0.1.x.
- (b) Build custom inline toggle via `vm.Card` + Dash callback. More work, closer to wireframe.

**Recommendation:** Option (a) — use `vm.Parameter(selector=vm.RadioItems(...))` instead of `vm.Dropdown`. This is Vizro-idiomatic and avoids custom callbacks. Document the deviation from wireframe in a code comment.

### Gap 5: Verify chart parity with Dash reference

**Checklist (from wireframe):**
- [ ] Trend chart: solid lines for actuals, dashed for forecast, CI shaded area via `fill="toself"` — ✅ already in `trend_forecast.py`
- [ ] Vertical dashed line at 2022-01-01 with "Cooking oil export ban" annotation — ✅ already in `trend_forecast.py`
- [ ] Forecast region shaded via `add_vrect` — ✅ already in `trend_forecast.py`
- [ ] Y-axis IDR formatted (`tickformat="~s"`) — ✅ already in `trend_forecast.py`
- [ ] Signal badges: BUY=green, HOLD=gray, WATCH=red — ✅ already in `signal_badges.py`
- [ ] YoY bar: grouped bars, `add_hline(y=0)` baseline — ✅ already in `yoy_bar.py`
- [ ] KPI sparklines: 2×2 subplot, 24-month mini trend — ✅ already in `kpi_sparklines.py`
- [ ] Limitations footnote always visible — needs "See methodology →" link (Gap 2)

### Gap 6: Cross-page filter persistence foundation

`show_in_url=True` on all `vm.Filter` instances. This is the Phase D concern but the filter definitions are created on Page 1 now — add `show_in_url=True` from the start so it's ready for cross-page sharing.

## What NOT to Change

| File | Reason |
|------|--------|
| `dashboard/data_access.py` | Framework-agnostic, works as-is |
| `dashboard/data_manager.py` | Already correct for Vizro |
| `dashboard/charts/trend_forecast.py` | Already correct — do not break the CI area, vline, or vrect |
| `dashboard/charts/yoy_bar.py` | Already correct |
| `dashboard/charts/signal_badges.py` | Already correct |
| `dashboard/charts/kpi_sparklines.py` | Only modify the filter behavior (Gap 3), not the subplot layout |
| `transform/` | dbt models complete |
| `export/export_json.py` | Complete |
| `forecast/run_forecast.py` | Complete |
| `analysis/` | Marimo notebooks complete |
| `docs/wireframes/` | Reference only |
| `docs/LEARNINGS.md` §87–96 | Already written |
| Pages 2–4 | Out of scope for this session |

## Vizro Patterns to Follow

| Pattern | Ref | Implementation |
|---------|-----|----------------|
| `@capture("graph")` must be called, not passed as ref | LEARNINGS §88 | `vm.Graph(figure=my_fn(data_frame="key"))` |
| `vm.Filter` scopes to all page components | Vizro docs | No need to list targets |
| `vm.Parameter` for non-data controls (range slider) | LEARNINGS §88 | Target specific component props |
| `show_in_url=True` for cross-page filter state | LEARNINGS §89 | Add to every `vm.Filter` |
| `data_manager["key"]` for lazy DataFrame load | LEARNINGS §90 | Already registered in `data_manager.py` |
| `vm.Container(direction="horizontal")` for side-by-side cards | Vizro docs | For model card + limitations card |
| Plotly figures use `layout.template="plotly_white"` | AGENTS.md | Already applied in all chart files |
| Never `connectgaps=True` on quality-filtered time-series | AGENTS.md | Already followed |

## File Change Summary

| File | Action | LOC delta |
|------|--------|-----------|
| `dashboard/pages/price_trends.py` | Edit — replace controls, add model card, add footnote link | ~+30 |
| `dashboard/charts/kpi_sparklines.py` | Edit — dim instead of hide filtered commodities | ~+5 |
| `dashboard/app.py` | No change needed | 0 |

## Verification

```bash
# 1. Smoke test — 1 page loads
uv run python -c "from dashboard.app import dashboard; print(len(dashboard.pages))"
# Expected: 1

# 2. Visual check — all 4 charts render
uv run python dashboard/app.py
# Visit http://localhost:7860
# Verify: KPI sparklines (4 cards visible), trend+forecast chart, YoY bar, signal badges

# 3. Filter test — commodity filter updates all charts
# Change dropdown to "Rice" → all 4 charts filter to Rice, KPI cards dim non-Rice

# 4. Filter test — URL persistence
# Set commodity=Sugar, island=Java → confirm URL params appear
# Navigate to another page (when built) → params persist

# 5. Model card — data loads from forecast.json metadata
# Confirm model names and MAE values display correctly

# 6. Limitations footnote — "See methodology →" link opens in new tab
```

## Suggested Skills

The agent continuing this work should invoke:

1. **`frontend-design`** — For building distinctive Vizro page layouts with intentional aesthetics. Use when designing the `vm.Page` layout grid and `vm.Card` styling.

2. **`impeccable`** — For polishing the custom chart functions. Use when refining the `@capture("graph")` functions for professional appearance.

3. **`harden`** — For edge cases: empty data states, filter combinations that return no data, graceful fallback when `forecast.json` metadata is missing.

4. **`clarify`** — For reviewing UX copy: the limitations footnote text, model info card labels, signal badge reasons. Must be clear for Procurement Analyst audience.

## Implementation Plan Reference

- Full plan: `docs/implementation-plan.md` §6.C.1 (lines 438–449)
- Handoff (full Phase C): `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md`
- Wireframe spec: `docs/wireframes/wfp-wireframe-page1-price-trends-forecast.md`
- Wireframe evaluation: `docs/wireframes/wfp-vizro-wireframe-evaluation.md`
- LEARNINGS: `docs/LEARNINGS.md` §87–96

## Sensitive Info (Redacted)

- HF Spaces URL: `https://albarpambagio-wfp-food-price.hf.space/`
- HF token: stored in `~/.cache/huggingface/credentials` (not in code)
- DuckDB path: `data/wfp.duckdb` (relative to project root)
