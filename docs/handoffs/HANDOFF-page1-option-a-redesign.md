# Handoff: Page 1 — Option A YoY Chart Redesign (Stuck)

**Timestamp:** 2026-06-04 11:44
**Previous:** `docs/handoffs/HANDOFF-page1-hover-theme-wireframe.md`
**Spec:** `docs/wireframes/wfp-wireframe-page1-yoy-redesign.md`

## State

The wireframe spec defines 5 layout options for Page 1's YoY inflation chart. The user asked to execute **Option A (Grouped Bar, Improved)** — same grouped bar layout as the baseline, with reference bands, thick zero line, hovertemplate, 12-year window, and theme-adaptive colors.

## What Was Done

1. Edited `dashboard/charts/yoy_bar.py` to add:
   - `+2σ band` annotation label (opacity 0.25)
   - Darker zero line color (`rgba(80,80,80,0.6)` → `rgba(64,64,64,0.8)`)
   - Comment annotations marking A1–A5 spec elements in source
2. Cleared `__pycache__` via WSL bash (`find ... -exec rm -rf {} +`)
3. Killed any stale Python process on port 7860
4. Verified `.pyc` bytecode contains the new strings (`+2σ`, `rgba(64,64,64,0.8)`)
5. Confirmed no duplicate `yoy_bar` files exist anywhere on the system
6. Confirmed `dashboard` is NOT installed as a package in site-packages
7. Confirmed Vizro's `@capture("graph")` stores a direct function-object reference — no figure caching at decorator level
8. Confirmed Vizro calls the captured function fresh on every render callback

## The Blocking Issue

**The user reports the chart hasn't changed.** They say they still see "small multiples version" (Option E from spec) despite:
- Source code being grouped bar (line 99: `barmode="group"`, 4 `go.Bar` traces)
- `.pyc` matching `.py` (verified via `strings` — contains `barmode`, no `subplots`/`make_subplots`)
- Server restarted, cache cleared, no stale process

The visual deltas from baseline are extremely subtle:
- Zero line: `rgba(80,80,80,0.6)` → `rgba(64,64,64,0.8)` (barely distinguishable)
- Annotation: `opacity=0.25` + `text="+2σ band"` (nearly invisible)

**Hypothesis:** The implementation is executing correctly but the changes are too subtle to notice. The baseline code already had reference bands, thick zero line, hovertemplate, and 12-year window — the Option A spec additions that were MISSING were:
- Horizontal reference **boundary lines** at ±10/20/30 (spec shows `────` at +30%). Currently only shaded `add_hrect` fill with `line_width=0`.
- Visible sigma labels (annotation at `opacity=0.25` is too faint)
- Year-level x-axis ticks (`dtick="M12"` / `tickformat="%Y"`) instead of month granularity
- Zero line visually dominant over reference lines (`line_width=3`)

## Root Cause

The edit scope was too narrow. It applied the "improvements" documented in the spec table but only at the most minimal level (color tweaks, subtle annotation). The wireframe's visual refinements (boundary lines, clear labels, year ticks) were never implemented, so the chart looks identical to baseline.

## Suggested Skills

- `systematic-debugging` — if the agent needs to verify that code changes actually execute at render time (e.g., inject a `print()` into `yoy_bar()`, watch server logs during page load)
- `cavecrew` — can spawn investigator/builder subagents to parallelize: one reads Vizro render flow while another edits the chart file
- `dash-dashboard-framework` — if the agent needs to understand how Vizro/Dash callbacks connect `vm.Parameter` controls to `@capture("graph")` chart functions

## Files Referenced

| File | Role |
|------|------|
| `dashboard/charts/yoy_bar.py` | Target — Option A implementation lives here |
| `dashboard/pages/price_trends.py` | Page definition — wires `yoy_bar` into `vm.Graph` at line 78 |
| `dashboard/charts/kpi_sparklines.py` | 2×2 subplot grid — potentially confused with "small multiples" |
| `docs/wireframes/wfp-wireframe-page1-yoy-redesign.md` | Spec — defines Options A–E |
| `.venv/bin/python` | Runs the app — WSL venv created by uv |
| `dashboard/data_access.py` | `compute_yoy_delta()` — YoY% calculation used by `yoy_bar` |

## Next Steps

1. **Verify the render path** — inject a `print("YOY_BAR_CALLED")` or use `loguru` to confirm `yoy_bar()` executes with the new code when the dashboard renders
2. **Implement spec-matching visual refinements:**
   - Add `add_hline` at ±10, ±20, ±30 with `rgba(128,128,128,0.3)` per spec A5
   - Set x-axis `dtick="M12"` and `tickformat="%Y"` for year-only labels
   - Raise annotation opacity to 0.6 and add `-2σ band` for symmetry
   - Bump zero line to `line_width=3`
3. **Hard refresh** — `Ctrl+Shift+R` in browser, or open incognito, after restart
4. **If still stuck:** check `uv run python -c "from dashboard.charts.yoy_bar import yoy_bar; print(yoy_bar)"` to confirm the function object is from the current file, not a cached import
