# Handoff: Page 1 Bugfix Session 2 — Fixes Applied, New Symptoms Emerge

## Session Summary

Applied all 4 priority fixes from `docs/handoffs/HANDOFF-page1-bugs-and-learnings.md` (P1–P4). P5 (Pages 2–4) was explicitly excluded.

## Work Done

| Priority | Bug | Fix | Status |
|----------|-----|-----|--------|
| P1 | Bug 3: Forecast first-render timing (`commodity_filter` literal) | Removed `commodity_filter="commodity_filter"` from all 4 `vm.Graph()` calls in `dashboard/pages/price_trends.py:63-86` | ✅ Code verified; user now says "maybe no" to whether it persists |
| P2 | Bug 2: YoY row-based `pct_change(periods=12)` | Replaced with `compute_yoy_delta()` in `dashboard/charts/yoy_bar.py:37` | ✅ Code verified; user says "bad visual representations" persist |
| P3 | Learnings doc | Added §97 (vm.Filter/"All" sentinel) and §98 (first-render timing) to `docs/LEARNINGS.md` | ✅ Done |
| P4 | Cross-platform venv | Added `UV_PROJECT_ENVIRONMENT` to PowerShell profile; WSL `~/.bashrc` needs manual setup | ✅ Partial |

## Verification Results

### YoY Computation (`compute_yoy_delta` vs `pct_change(periods=12)`)
- Tested against real DuckDB data (639 rows, 4 commodities, 2007-2024)
- `compute_yoy_delta()` produces calendar-aligned YoY via merge on `(commodity, shifted_year, month_num)`
- Differences cluster around 2017-08 data gap, up to 4pp for Cooking Oil (e.g., 2018-02: old=+1.0%, new=-0.6%)
- 134/145 rows per commodity match at 1dp rounding; ~11 differ meaningfully
- Function works correctly — the merge-based approach is the right fix

### Chart Smoke Test
- `yoy_bar(All)` produces 4 traces
- `trend_forecast(All)` produces 12 traces (4 actuals + 4 forecasts + 4 CI)
- Forecast JSON has 819 rows, 4 commodities, dates 2007-01-01 to 2025-12-01
- All imports pass: `uv run python -c "from dashboard.pages.price_trends import price_trends_page"`

## New Symptoms Reported (User Observation)

User ran the dashboard after fixes and reports:

1. **Chart overlap**: Charts "seem overlap one to the other"
2. **Y-axis clipping**: Y-axis "clips" the data
3. **YoY chart disappears in light mode**: Fixed when sidebar closed and reopened — suggests Vizro callback timing/rendering issue, NOT a computation issue
4. First-render may be resolved (user's "maybe no" response)

These are **new symptoms** not described in the original handoff. The original Bug 2 (wrong YoY values with `pct_change(periods=12)`) may have been incorrect — the actual problem appears to be a Vizro rendering issue that happens to affect the yoy_bar chart, not a data computation bug. The `compute_yoy_delta()` fix is still correct (calendar-aligned > row-based) but probably does not fix what the user is seeing.

## Possible Root Causes for New Symptoms

- **Chart overlap**: Likely a Vizro page layout issue — `price_trends.py` defines 5 components (4 `vm.Graph` + 1 `vm.Container`) without any `layout` wrapper. Vizro's default layout stacks them vertically but browser viewport or container sizing may cause overlap. Try `vm.Flex(direction="row")` for cards or `vm.Container(components=[...], layout=vm.Layout(grid=[[...]]))` for explicit grid.

- **Y-axis clipping**: Each chart has its own y-axis (independent figures). Most likely caused by Vizro's `_optimise_fig_layout_for_dashboard` (called in `Graph.__call__` at graph.py:185) — this function may modify figure dimensions in ways that clip content. Check this function in Vizro source.

- **YoY chart disappearance in light mode** (fixed by sidebar toggle): This strongly mirrors the original Bug 3 pattern (forecast missing on first load, fixed by sidebar toggle). The sidebar toggle triggers a full page re-render where all callbacks fire. Root cause is likely Vizro callback timing — some chart's `CapturedCallable.__call__` receives incomplete kwargs on first render. Investigate whether `commidity_filter` parameter callback races with chart initialization differently for `yoy_bar` vs other charts.

- **Sidebar toggle as workaround**: Close/reopen sidebar forces Dash to re-render the page layout, firing all callbacks including `vm.Parameter`. Everything works after that because the parameter's bound value is established. This matches Vizro 0.1.53 callback timing behavior documented in LEARNINGS.md §98.

## DuckDB Data Details

- `wfp_marts.mart_price_trends_national`: 639 rows, columns: `month` (TIMESTAMP), `commodity_consolidated`, `market_count`, `avg_price_idr`, `avg_price_usd`, `min_price_idr`, `max_price_idr`
- Month is `datetime.datetime` (TIMESTAMP type in DuckDB, becomes `datetime64[us]` in pandas)
- Data has 2017-08 gap (61 days, all commodities); Cooking Oil also has 1553-day gap ending 2024-06
- `ORDER BY 1` sorts by month but not commodity — deterministic row order varies within same month

## File Inventory

| File | Notes |
|------|-------|
| `dashboard/pages/price_trends.py` | P1 fix applied — no `commodity_filter` literals in vm.Graph calls |
| `dashboard/charts/yoy_bar.py` | P2 fix applied — uses `compute_yoy_delta()` |
| `dashboard/charts/trend_forecast.py` | Unchanged — 12 traces, forecast JSON includes in-sample backfill |
| `dashboard/charts/kpi_sparklines.py` | Unchanged — 2x2 subplot, opacity dimming |
| `dashboard/charts/signal_badges.py` | Unchanged — annotation-based badges |
| `dashboard/data_access.py` | Contains `compute_yoy_delta()` — merge-based YoY |
| `dashboard/data_manager.py` | Lambda registrations for 6 marts + forecast |
| `dashboard/app.py` | Single page, port 7860 |
| `docs/LEARNINGS.md` | Added §97, §98 |
| `docs/handoffs/HANDOFF-page1-bugs-and-learnings.md` | Original bug descriptions (P1-P5) |

## Suggested Skills

1. **`systematic-debugging`** — The root causes documented in the original handoff may be incorrect. The chart overlap and y-axis clipping symptoms need Phase 1 root cause investigation. Trace Vizro's page layout rendering (how `vm.Page` arranges multiple `vm.Graph` components) and verify Plotly figure auto-ranging behavior with 12-traces per chart. Do NOT assume the handoff's root cause analysis is correct.

2. **`dash-dashboard-framework`** — The dashboard page layout may need `vm.Flex` or `vm.Layout` to control chart positioning and sizing. Apply DASH framework to verify the page layout hierarchy supports the intended stakeholder view.

3. **`browser-automation`** — To reproduce visual issues (overlap, clipping) without a human viewing the dashboard, write a Playwright/Selenium test that captures screenshots at various viewports and compares chart dimensions.

4. **`harden`** — After fixing visual issues, harden: forecast JSON loading errors (currently `except Exception: pass` in trend_forecast.py:80,110), empty DataFrame edge cases, and cross-browser rendering differences.

## References

- Original bugs: `docs/handoffs/HANDOFF-page1-bugs-and-learnings.md`
- Page design: `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md`
- Full pipeline: `README.md`
- Vizro 0.1.53 Graph model source: `.venv/Lib/site-packages/vizro/models/_components/graph.py` (see `__call__` at L178)
- Actions utils (parameter wiring): `.venv/Lib/site-packages/vizro/actions/_actions_utils.py` (see `_get_parametrized_config` at L165, `_get_modified_page_figures` at L252)
- CapturedCallable: `.venv/Lib/site-packages/vizro/models/types.py` (see `__call__` at L220, `_arguments` at L271)
