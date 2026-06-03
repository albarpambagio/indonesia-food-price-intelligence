# Handoff: Page 1 Bugfixes — vm.Filter Trap, YoY Computation, Parameter Timing

## Context

Indonesia Food Price Intelligence — Vizro 0.1.53 dashboard. Page 1 (`dashboard/pages/price_trends.py`) was previously ported with filters, model info card, and 4 custom charts. Three bugs remained after initial handoff completion (`docs/handoffs/HANDOFF-page1-completion.md`).

This session diagnosed and partially fixed them. Two bugs remain for the next agent.

## Bugs Found

### Bug 1 (FIXED): `vm.Filter` Treats "All" as Literal Column Value

**Symptom:** All charts showed "No data available" despite 639 rows in DuckDB.

**Root cause:** `vm.Filter(column="commodity_consolidated", selector=vm.Dropdown(options=["All", "Rice", ...], value="All"))` calls `_filter_isin(series, ["All"])` which filters for rows where `commodity_consolidated == "All"` — no matches → empty DataFrame. Vizro has no concept of "All" as a "show everything" sentinel.

**Fix:** Replaced `vm.Filter` with `vm.Parameter(targets=[...], selector=vm.Dropdown(...))`. Chart functions receive the Dropdown value directly and handle `"All"` → no-filter themselves via `if commodity_filter != "All"`.

**Files changed:**
- `dashboard/pages/price_trends.py`: `vm.Filter` → `vm.Parameter` with `targets=["kpi_sparklines.commodity_filter", "trend_forecast.commodity_filter", "yoy_bar.commodity_filter", "signal_badges.commodity_filter"]`
- All 4 chart files: `commodity_filter` restored with default `"All"` and `if commodity_filter != "All"` guard

**Reference:** Vizro source: `.venv/lib/python3.13/site-packages/vizro/models/_controls/filter.py:63-75` — `_filter_isin` applies `series.isin(value)` with no sentinel handling.

### Bug 2 (UNFIXED): YoY Computation Uses Row-Based `pct_change`

**Symptom:** YoY bar chart shows incorrect/erratic values.

**Root cause:** `yoy_bar.py:39` uses `sub["avg_price_idr"].pct_change(periods=12) * 100`. Pandas `pct_change(periods=12)` compares the value 12 **rows back**, not 12 **calendar months** back. When monthly data has gaps (639 rows / 4 commodities ≈ 160 months each vs 209 possible), the comparison aligns with the wrong month.

**Fix (not yet applied):** Replace `pct_change(periods=12)` with `compute_yoy_delta()` from `dashboard/data_access.py:86`. This function merges on `(commodity_consolidated, year, month_num)` with year shifted by +1, correctly handling gaps:

```python
from dashboard.data_access import compute_yoy_delta

# Before: sub["yoy_pct"] = sub["avg_price_idr"].pct_change(periods=12) * 100
# After: computed on full filtered dataset via merge-based delta
```

### Bug 3 (UNFIXED): Forecast Chart Broken on First Load, Fixes on Sidebar Toggle

**Symptom:** Forecast trend lines + CI area missing on initial page load. After toggling the sidebar (close/reopen), the chart renders correctly.

**Root cause:** Vizro callback timing. On first page load, `_get_parametrized_config()` (`_actions_utils.py:165`) returns the literal bound argument `{"commodity_filter": "commodity_filter"}` because the `vm.Parameter` callback **hasn't fired yet**. The chart function receives `commodity_filter="commodity_filter"` → no data matches → early return with "No data available" → forecast section never reached.

Sidebar toggle triggers a re-render where the `vm.Parameter` callback has fired → `commodity_filter` gets the real Dropdown value → chart renders correctly.

**Fix (not yet applied):** Remove `commodity_filter="commodity_filter"` from all 4 `vm.Graph()` calls in `price_trends.py`. Chart functions already have default `commodity_filter: str = "All"`. On first render, bound args won't include `commodity_filter`, so the function uses its default `"All"`. `vm.Parameter` will still override it on subsequent renders because `CapturedCallable.__call__` merges `{**bound_arguments, **kwargs}` with runtime kwargs overriding.

**Changed file (after fix):**
```python
# price_trends.py — remove commodity_filter from vm.Graph calls
vm.Graph(
    id="trend_forecast",
    figure=trend_forecast(data_frame="mart_price_trends_national"),  # no commodity_filter
),
```

**Reference:** `_actions_utils.py:252-280` — `_get_modified_page_figures` calls `_get_parametrized_config(ctds_parameter, target, data_frame=False)` which copies bound arguments. On first load, `ctds_parameter` is empty → config stays as literals.

## Current State

| File | LOC | Status | Notes |
|------|-----|--------|-------|
| `dashboard/app.py` | 25 | ✅ Complete | 1 page, `import dashboard.data_manager` |
| `dashboard/data_manager.py` | 23 | ✅ Complete | 7 keys (6 marts + forecast) |
| `dashboard/data_access.py` | 117 | ✅ Complete | `load_mart()`, `load_forecast_data()`, `compute_yoy_delta()`, `get_latest_prices()` |
| `dashboard/charts/trend_forecast.py` | 122 | ✅ Complete | Actuals + forecast + CI + vrect |
| `dashboard/charts/kpi_sparklines.py` | 117 | ✅ Complete | 2×2 subplot, dims non-selected at 0.3 opacity |
| `dashboard/charts/yoy_bar.py` | 60 | ⚠️ Bug 2 | Uses `pct_change(periods=12)` — needs `compute_yoy_delta()` |
| `dashboard/charts/signal_badges.py` | 102 | ✅ Complete | BUY/HOLD/WATCH via annotations |
| `dashboard/pages/price_trends.py` | 109 | ⚠️ Bug 3 | `commodity_filter="commodity_filter"` causes first-render timing issue |
| `docs/LEARNINGS.md` | — | ⬜ Needs §97, §98 | See below |

## Pending Work

### Priority 1: Fix Bug 3 (Forecast first-render timing)
- Remove `commodity_filter="commodity_filter"` from all 4 `vm.Graph()` calls in `price_trends.py`
- This lets chart functions use their `"All"` default on first render
- `vm.Parameter` override still works on subsequent renders

### Priority 2: Fix Bug 2 (YoY row-based pct_change)
- In `yoy_bar.py`, replace line 39 with `compute_yoy_delta()` from `data_access`
- Apply `compute_yoy_delta()` to the full filtered DataFrame, then extract per-commodity values

### Priority 3: Update LEARNINGS.md
- Add §97: `vm.Filter` treats "All" as literal column value — use `vm.Parameter` for sentinel-based filtering
- Add §98: `_get_parametrized_config` timing — bound argument literals on first render before callback fires

### Priority 4: Cross-platform venv
- Project lives on shared `D:` drive accessed from both Windows PowerShell and WSL
- `.venv` created by one platform is invalid on the other
- Recommended fix: add `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/venv-wfp-food-price"` to `~/.bashrc` (WSL) and in PowerShell profile for Windows
- Each platform gets its own venv path, `uv run` never reinstalls

### Priority 5: Pages 2-4
- Page 2 (Seasonal Patterns), Page 3 (Geographic Disparity), Page 4 (Commodity Signals) not started
- Reference: `docs/handoffs/HANDOFF-vizro-phase6-phasec-pages.md`
- Data sources for all 4 pages already registered in `data_manager.py`

## Vizro Patterns to Follow

| Pattern | Ref | Implementation |
|---------|-----|----------------|
| `@capture("graph")` must be called, not passed as ref | LEARNINGS §88 | `vm.Graph(figure=my_fn(data_frame="key"))` |
| `vm.Parameter` overrides bound args at runtime via `CapturedCallable.__call__` | This session | Targets like `"chart_id.commodity_filter"` set the parameter on the CapturedCallable |
| No `vm.Filter` for sentinel values like "All" | This session (Bug 1) | Use `vm.Parameter` instead; chart functions handle sentinel logic |
| Chart function defaults as fallback for first-render timing | This session (Bug 3) | Always provide sensible defaults; avoid bound argument literals for params wired to `vm.Parameter` |
| `vm.Flex(direction="row")` for side-by-side cards | Vizro docs | `vm.Container(components=[...], layout=vm.Flex(direction="row"))` |

## Cross-Platform Venv

The project is accessed from both Windows PowerShell and WSL on a shared NTFS drive. The `.venv` directory contains platform-specific binaries and cannot be shared.

**WSL workflow:**
```bash
cd "/mnt/d/PROJECT/food price dashboard"
rm -rf .venv
uv venv
uv sync
uv run python dashboard/app.py
```

**Windows PowerShell workflow:**
```powershell
cd "D:\PROJECT\food price dashboard"
Remove-Item -Recurse -Force .venv
uv venv
uv sync
uv run python dashboard/app.py
```

**Permanent fix:** Set `UV_PROJECT_ENVIRONMENT` to a platform-specific path per the instructions above.

## Suggested Skills

1. **`systematic-debugging`** — For diagnosing the remaining first-render timing bug (Bug 3). Requires tracing Vizro's callback chain from `_on_page_load` through `_get_parametrized_config` to `CapturedCallable.__call__`. Use `print()` statements or Vizro's `_log_call` decorator to trace execution order.

2. **`dash-dashboard-framework`** — For Pages 2-4 design decisions. Each page serves a different stakeholder question (seasonal, geographic, correlation). Apply the DASH (Decision, Audience, Signal, Hierarchy) framework to verify each page's layout.

3. **`harden`** — For edge cases: empty forecast data, DuckDB connection failure (read-only mode), filter combinations returning no data, forecast JSON corruption or missing file. Currently errors are silently swallowed via `except Exception: pass`.

4. **`analytics-insight-generation`** — For ensuring chart titles, axis labels, and footnote text communicate the business insight (SCAN framework), not just the data. The Procurement Analyst audience needs plain-language signals.

## Sensitive Info

- HF Spaces URL: `https://albarpambagio-wfp-food-price.hf.space/` (public)
- HF token: stored in `~/.cache/huggingface/credentials` (not in code)
- DuckDB path: `data/wfp.duckdb` (relative to project root)
- All data is public WFP dataset (CC BY-IGO 3.0)
