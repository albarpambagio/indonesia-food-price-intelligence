# Handoff: Page 1 — YoY Hover, Theme Text Colors, Wireframe Designs

## Session Summary

Debugged three remaining issues on Page 1 after the layout/y-axis fix landed (`9c0c948`):

1. **YoY chart hover doesn't show individual values** — bar traces lack `hovertemplate`; default Plotly bar hover may be unreliable after Vizro's `update_graph_theme` shallow-copies the figure
2. **Text/data labels unreadable in dark mode** — explicit font colors baked into figure JSON survive Vizro's theme template swap
3. **Wireframe for YoY layout redesign** — user wants 5 layout options documented in `docs/wireframes/`

## Work Done

| Item | Detail | Status |
|------|--------|--------|
| Chart overlap | Wrapped 5 components in `vm.Container(layout=vm.Flex(direction="column", gap="20px"))` at `price_trends.py:63-92` | ✅ Committed in `9c0c948` |
| Y-axis clipping | Added `yaxis_automargin=True`, `margin=dict(t=50, b=50, autoexpand=True)` to `yoy_bar.py:73-77` and `trend_forecast.py:118-121` | ✅ Committed in `9c0c948` |
| YoY robustness | Replaced row-based `pct_change(periods=12)` with `compute_yoy_delta()` (merge-based, calendar-aligned), added `has_any_bar` guard, `marker_line_color`, `showlegend` | ✅ Committed in `9c0c948` |
| LEARNINGS.md | Documented §97 (`vm.Filter` "All" sentinel → `vm.Parameter`) and §98 (`_get_parametrized_config` first-render timing) | ✅ Committed in `9c0c948` |
| Root cause: theme text colors | Traced Vizro's `update_graph_theme` (dashboard.js:95-108) — shallow copy swaps only `layout.template`, cannot override explicit font properties set in traces/annotations. Confirmed via `fig.to_json()` that explicit `color` values survive serialization. | ✅ Investigated |
| YoY chart renders (not a disappearance bug) | User corrected: chart DOES render — it's the text that's unreadable in dark mode. Bars and axis labels appear but annotation colors are wrong. | ✅ Misconception corrected |

## Remaining Work

### P1 — YoY Chart Hover

**Problem**: `yoy_bar.py` bar traces lack `hovertemplate`. Plotly's default bar hover may be unreliable after Vizro's clientside callback replaces the figure object.

**Fix**: Add explicit `hovertemplate` to each `go.Bar` in `yoy_bar.py:49-57`:
```python
go.Bar(
    x=sub["month"],
    y=sub["yoy_pct"],
    name=commodity_name,
    marker_color=color,
    marker_line_color="rgba(0,0,0,0)",
    hovertemplate="<b>%{fullData.name}</b><br>%{x|%b %Y}<br>YoY: %{y:+.1f}%<extra></extra>",
)
```

**Decision**: Use default per-trace tooltip (not `hovermode="x unified"`). User answered "default".

### P2 — Theme-Adaptive Text Colors

**Root cause**: Vizro's `update_graph_theme` (dashboard.js:95-108) creates a shallow copy and replaces only `layout.template`. Explicitly-set `font.color`, `line_color` in traces/annotations are **baked into the figure JSON** and survive template swap unchanged.

**Files to fix**:

| File | Line | Current | Fix |
|------|------|---------|-----|
| `kpi_sparklines.py` | 103 | `font=dict(size=11, color=f"rgba(0,0,0,{opacity})")` | `font=dict(size=11)` — dead code: filtered-out commodities `continue` before reaching this line |
| `trend_forecast.py` | 91 | `font=dict(size=10, color="gray")` | `font=dict(size=10)` — let Vizro template control color |
| `trend_forecast.py` | 83 | `line_color="gray"` | `line_color="rgba(128,128,128,0.3)"` — visible on both backgrounds |
| `yoy_bar.py` | 68 | `line_color="gray"` | `line_color="rgba(128,128,128,0.3)"` |

**No change needed**: `signal_badges.py` uses saturated HTML inline colors (`#28a745`, `#dc3545`) — visible on both backgrounds; axis labels/legends/subplot titles have no explicit color → template adapts correctly.

### P3 — YoY Wireframe Document

Create `docs/wireframes/wfp-wireframe-page1-yoy-redesign.md` with 5 layout options:

| Option | Type | Description |
|--------|------|-------------|
| **A** | Grouped bar (improved) | Current format + hover + horizontal gridlines + reference bands |
| **B** | Faceted bars per commodity | 2×2 subplot grid, one per commodity, individual y-axes |
| **C** | YoY as overlay lines | Thin lines on the main trend+forecast chart background |
| **D** | Year×Commodity heatmap | Rows=year, cols=commodity, color=YoY% |
| **E** | Small multiples calendar | Vertical stack of mini bar charts, one per commodity |

Format should match existing wireframes (ASCII layout, numbered annotations, states table). Reference `docs/wireframes/wfp-wireframe-page1-price-trends-forecast.md` for style.

## Root Cause Analysis Summary

| Symptom | Root Cause | Fix Reference |
|---------|-----------|---------------|
| Chart overlap | No layout container — Vizro default wraps bare Graphs incorrectly | `price_trends.py:63-92` (Container + Flex) |
| Y-axis clipping | No `yaxis_automargin`, tight margins | `yoy_bar.py:73-77`, `trend_forecast.py:118-121` |
| Wrong YoY values | Row-based `pct_change(periods=12)` not calendar-aligned | `compute_yoy_delta()` in `data_access.py:86` |
| Theme text unreadable | Explicit `font.color` in annotations survives Vizro template swap | See P2 above |
| Hover not working | Missing `hovertemplate` on bar traces | See P1 above |

## Key Vizro Internals Discovered

- `update_graph_theme` (dashboard.js:95-108): shallow-copies figure, replaces only `layout.template`. Does NOT override trace-level or annotation-level properties. **This is a fundamental Vizro limitation** — any explicitly-set property in the chart function survives theme toggle.
- Vizro light/dark templates define `font.color` as `rgba(20,23,33,...)` / `rgba(255,255,255,...)` at `layout.annotationdefaults.font.color`, `layout.xaxis.title.font.color`, `layout.font.color` etc. These apply only for properties NOT explicitly set in the figure.
- `Graph._optimise_fig_layout_for_dashboard` (graph.py:257-285): called after figure computation; sets `clickmode`, `modebar.remove`, `margin.t`. Does NOT touch explicit colors.

## Files Changed (this session)

| File | Change |
|------|--------|
| `dashboard/pages/price_trends.py` | Container+Flex layout, removed commodity_filter literals |
| `dashboard/charts/yoy_bar.py` | compute_yoy_delta, yaxis_automargin, has_any_bar guard, marker_line_color |
| `dashboard/charts/trend_forecast.py` | yaxis_automargin, showlegend, increased margins |
| `dashboard/charts/kpi_sparklines.py` | margin autoexpand added |
| `dashboard/charts/signal_badges.py` | margin autoexpand added |
| `docs/LEARNINGS.md` | Added §97, §98 |

## DuckDB Data Shape (for reference)

- `wfp_marts.mart_price_trends_national`: 639 rows, 4 commodities, 2007-2024
- Month: `datetime64[us]` (TIMESTAMP in DuckDB)
- 2017-08 data gap (61 days). Cooking Oil has 1553-day gap ending 2024-06
- Forecast JSON: 819 rows, 4 commodities, dates 2007-01-01 to 2025-12-01

## References

| Artifact | Path |
|----------|------|
| Previous bug handoff | `docs/handoffs/HANDOFF-page1-bugs-remaining.md` |
| Original handoff | `docs/handoffs/HANDOFF-page1-bugs-and-learnings.md` |
| Page design | `docs/wireframes/wfp-wireframe-page1-price-trends-forecast.md` |
| LEARNINGS.md | `docs/LEARNINGS.md` (§97, §98) |
| Vizro Graph source | `.venv/lib/python3.13/site-packages/vizro/models/_components/graph.py` (see `__call__` L178, `_optimise_fig_layout_for_dashboard` L257) |
| Vizro update_graph_theme | `.venv/lib/python3.13/site-packages/vizro/static/js/models/dashboard.js` (L95-108) |
| Vizro light template | `.venv/lib/python3.13/site-packages/vizro/themes/vizro_light.json` |
| Vizro dark template | `.venv/lib/python3.13/site-packages/vizro/themes/vizro_dark.json` |
| Latest commit | `9c0c948` — "fix(page1): layout wrap, y-axis automargin, robust yoy" |
| Page build / wiring | `.venv/lib/python3.13/site-packages/vizro/actions/_actions_utils.py` (`_get_parametrized_config` L165, `_get_modified_page_figures` L252) |

## Suggested Skills

1. **`systematic-debugging`** — Use for P1 (hover). The root cause may be more nuanced than "missing hovertemplate" — Vizro's `update_graph_theme` shallow copy may strip Plotly internal hover state. Verify by adding a diagnostic `customdata` attribute to bar traces and checking if it survives the clientside callback. Do NOT assume the handoff's root cause analysis is complete.

2. **`dash-dashboard-framework`** — Use for P3 (wireframe). Apply DASH (Decision, Audience, Signal, Hierarchy) to evaluate each of the 5 YoY layout options. The wireframe should be decision-centered for the Category Manager audience, not just visually distinct.

3. **`frontend-design`** — Use for P3 (wireframe) layout sketches. Generate ASCII wireframes for each of the 5 options following the existing format in `docs/wireframes/wfp-wireframe-page1-price-trends-forecast.md`. Focus on information hierarchy and chart-appropriate encoding (bars vs lines vs heatmap for percentage data).

4. **`harden`** — Apply after P2 fix: verify `rgba(0,0,0,*)` colors do not appear in serialized figure JSON for any chart. This ensures the theme fix is complete and no other chart has baked-in dark text colors. Run: `python -c "from dashboard.pages.price_trends import price_trends_page; print('imports ok')"`.
