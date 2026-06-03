# Handoff: Phase 6 Phase C — Port 3 Pages + Rebuild Page 1 (Vizro)

## Context

Indonesia Food Price Intelligence project — migrating from Dash 4.1.0 to Vizro 0.1.53 dashboard framework. Phases 0–5f are complete. Phase 6 spike (A) and data layer port (B) are complete. Wireframe evaluation (B1) is complete. **Next: Phase C — rebuild all 4 dashboard pages in Vizro.**

## Decision Gate — PASSED

Spike passed 2026-06-02. GO decision logged in `logs/migration.log`. Key learning: `@capture("graph")` must be called, not passed as ref.

**Why Vizro over Dash**: Cross-filtering requirement. 4 pages need "click chart → filter all" UX. Vizro's `set_control` action makes this declarative; Dash requires custom callbacks (~80 LOC × 6 pairs). This was the decisive criterion (+8 weighted in §6.STACK decision matrix).

**User chose option (A): Rewrite in place** — Dash pages in `dashboard/pages/*.py` are replaced with Vizro `vm.Page(...)` configs. Dash code preserved in git history.

## What's Complete (Do NOT Re-Do)

| Item | Status | Artifact |
|------|--------|----------|
| Phase 5g gaps (G1–G13) | ✅ All closed | `docs/implementation-plan.md` §5g |
| Phase 6.A Spike | ✅ GO | `dashboard/spike/` validated |
| Phase 6.B Data Layer | ✅ 7 keys registered | `dashboard/data_manager.py` |
| Phase 6.B1 Wireframe Eval | ✅ All resolved | `docs/wireframes/wfp-vizro-wireframe-evaluation.md` |
| LEARNINGS.md §87–96 | ✅ Exist | `docs/LEARNINGS.md` |
| Vendored GeoJSON | ✅ In place | `dashboard/assets/indonesia_provinces.geojson` |
| mart_price_trends_national | ✅ dbt model exists | `transform/models/marts/mart_price_trends_national.sql` |
| Pre/post 2022 correlation columns | ✅ In mart_correlation_summary | `transform/models/marts/mart_correlation_summary.sql` |
| Forecast metadata (dual-cooking-oil) | ✅ In forecast.json | `dashboard/public/data/forecast.json` |
| Date format normalization | ✅ `strftime("%Y-%m-%d")` | `export/export_json.py:78` |
| requirements.txt deleted | ✅ pyproject is source of truth | N/A |

## Current Dashboard State

**All 4 pages are still Dash** — they must be rewritten as Vizro:

| File | LOC | Framework | Status |
|------|-----|-----------|--------|
| `dashboard/app.py` | 45 | Dash | ⬜ Must rewrite to Vizro entry |
| `dashboard/pages/price_trends.py` | 323 | Dash | ⬜ Replace with Vizro vm.Page |
| `dashboard/pages/seasonal_patterns.py` | 222 | Dash | ⬜ Replace with Vizro vm.Page |
| `dashboard/pages/geographic_disparity.py` | 201 | Dash | ⬜ Replace with Vizro vm.Page |
| `dashboard/pages/commodity_signals.py` | 274 | Dash | ⬜ Replace with Vizro vm.Page |
| `dashboard/components/filters.py` | 69 | Dash | ⬜ Retire (Vizro has vm.Filter) |
| `dashboard/components/kpi_cards.py` | 62 | Dash | ⬜ Retire (custom @capture instead) |
| `dashboard/components/layout.py` | ~50 | Dash | ⬜ Retire (Vizro has vm.Container) |
| `dashboard/data_manager.py` | 23 | Vizro | ✅ Keep as-is |
| `dashboard/data_access.py` | ~120 | Framework-agnostic | ✅ Keep as-is |
| `dashboard/spike/app.py` | 25 | Vizro | ✅ Reference only |
| `dashboard/spike/custom_charts.py` | 22 | Vizro | ✅ Reference for @capture pattern |

**Key infrastructure gaps:**
- No `dashboard/charts/` directory (home for @capture("graph") functions)
- No Dockerfile (§6.8.3 all ⬜)
- No .dockerignore
- No README_HF.md

## Execution Plan (4 Days)

Full detailed plan is in the conversation history. Summary:

### Day 1: Infrastructure + Page 1
1. Rewrite `dashboard/app.py` as Vizro entry (~20 LOC)
2. Create `dashboard/charts/` directory
3. Create 4 custom chart files for Page 1:
   - `charts/trend_forecast.py` — main trend + forecast + CI area
   - `charts/yoy_bar.py` — YoY bar chart
   - `charts/kpi_sparkline.py` — KPI cards with sparklines
   - `charts/signal_badges.py` — BUY/HOLD/WATCH badges
4. Rewrite `dashboard/pages/price_trends.py` as Vizro vm.Page
5. Verify: `uv run python -c "from dashboard.app import dashboard_obj; print(len(dashboard_obj.pages))"`

### Day 2: Page 2 + Page 3
1. Create 3 custom chart files for Page 2:
   - `charts/seasonal_heatmap.py` — 12×4 matrix
   - `charts/seasonal_line.py` — monthly line + driver bands
   - `charts/ramadan_overlay.py` — T-3 to T+1 overlay
2. Rewrite `dashboard/pages/seasonal_patterns.py`
3. Create 2 custom chart files for Page 3:
   - `charts/choropleth.py` — Indonesia choropleth
   - `charts/island_comparison.py` — 5-trace line + Java baseline
4. Rewrite `dashboard/pages/geographic_disparity.py`
5. Implement cross-filter action (set_island_filter) — primary migration justification

### Day 3: Page 4 + Cross-page Filters
1. Create 3 custom chart files for Page 4:
   - `charts/correlation_heatmap.py` — 4×4 matrix
   - `charts/pair_scatter.py` — pre/post 2022 dots
   - `charts/rolling_correlation.py` — 36-month rolling + 2022 break
2. Rewrite `dashboard/pages/commodity_signals.py`
3. Add `show_in_url=True` to all vm.Filters across all 4 pages
4. Verify cross-page filter persistence

### Day 4: Docs + Deploy + Verify
1. Update LEARNINGS.md §75, §81-86 with SUPERSEDED banners
2. Update AGENTS.md Vizro conventions block
3. Remove Dash deps from pyproject.toml
4. Create Dockerfile (gunicorn app:app, port 7860)
5. Create .dockerignore, README_HF.md
6. Deploy to HF Spaces
7. Full verification suite

## Key Vizro Patterns (from LEARNINGS.md §87–96)

| Pattern | Ref | Notes |
|---------|-----|-------|
| `@capture("graph")` on custom chart functions | §88 | Must be called, not passed as ref |
| `vm.Filter` is per-page, not cross-page | §87 | Cross-page via `show_in_url=True` (§89) |
| `vm.Parameter` for non-data controls | §88 | Driver toggle, lag selector |
| `data_manager["key"]` for DataFrame access | §90 | Lazy load via lambda |
| `vm.Figure` cannot be `set_control` source | §95 | Use vm.Card with actions instead |
| Conditional visibility needs Dash callback | §96 | Ramadan overlay show/hide |
| `dashboard/charts/` for custom functions | §88 | One file per chart type |
| `dashboard/assets/` for static files | §93 | GeoJSON lives here |

## Wireframe Specs (Reference)

| Page | Spec | Key Components |
|------|------|----------------|
| 1 — Price Trends | `docs/wireframes/wfp-wireframe-page1-price-trends-forecast.md` | Trend+forecast chart, KPI sparklines, signal badges, YoY bar, model card, limitations footnote |
| 2 — Seasonal | `docs/wireframes/wfp-wireframe-page2-seasonal-patterns.md` | Heatmap, monthly line, Ramadan overlay, driver toggle, summary table |
| 3 — Geographic | `docs/wireframes/wfp-wireframe-page3-geographic-disparity.md` | Choropleth, 5 island KPI cards (click-to-filter), comparison line, province table, data warning |
| 4 — Signals | `docs/wireframes/wfp-wireframe-page4-commodity-signals.md` | Correlation matrix, pair scatter, rolling correlation, lag selector, leading indicator cards |

## Open Items (§10.3 of Wireframe Eval)

| # | Item | Status | Action Needed |
|---|------|--------|---------------|
| 1 | Mapbox token requirement | Open | Confirm `px.choropleth` (no token) is target |
| 2 | `post_2022_r` divergence threshold | Open | Confirm `abs(pre_2022_r - post_2022_r) > 0.2` |
| 3 | GeoJSON island-groups merge | Open | May need `dashboard/assets/indonesia_island_groups.geojson` (5 features) |

## Implementation Plan Reference

Full implementation plan: `docs/implementation-plan.md` §6.PAGES (lines 433–490)

Phase 6 sections:
- §6.STACK — Vizro decision rationale
- §6.SPIKE — Phase A (complete)
- §6.DATA — Phase B (complete)
- §6.WIREFRAME — Phase B1 (complete)
- §6.PAGES — Phase C (this handoff)
- §6.FILTERS — Phase D (after Phase C)
- §6.DEPLOY — Phase E (after Phase D)
- §6.DOCS — Phase F (parallel with Phase E)
- §6.HISTORY — Superseded Dash plan

## Verification Checklist

After Phase C completion:

```bash
# 1. Smoke test — 4 pages load
uv run python -c "from dashboard.app import dashboard_obj; print(len(dashboard_obj.pages))"

# 2. Local dev — all pages render
uv run python dashboard/app.py
# Visit http://localhost:7860, navigate all 4 pages

# 3. dbt build — 77 tests pass
cd transform && dbt build

# 4. Export verification — 0 mismatches
uv run python export/export_json.py

# 5. Cross-page filter persistence
# Navigate Page 1 → Page 2, confirm filter values in URL and on page

# 6. Page 3 cross-filter
# Click island KPI card → choropleth and table update

# 7. Page 4 lag selector
# Change lag → matrix and leading indicator cards update
```

## Suggested Skills

The agent continuing this work should invoke these skills:

1. **`frontend-design`** — For building distinctive, production-grade Vizro page layouts with intentional aesthetics. Use when designing vm.Layout grid specs and vm.Card styling.

2. **`impeccable`** — For crafting polished custom chart functions with high design quality. Use when implementing @capture("graph") functions that need to look professional.

3. **`audit`** — After completing all 4 pages, run a comprehensive audit of interface quality across accessibility, performance, and responsive design.

4. **`polish`** — Final quality pass before deployment. Fix alignment, spacing, consistency, and detail issues.

5. **`harden`** — Improve interface resilience: error handling for empty data states, edge cases in filter combinations, loading states.

6. **`optimize`** — Performance review: ensure cold start < 3s, chart render times acceptable, no unnecessary re-renders.

7. **`clarify`** — Review UX copy: error messages, data limitation callouts, forecast footnotes. Make sure all text is clear for the Procurement Analyst audience.

8. **`verify`** — Run verification-before-completion skill before claiming Phase C is done. Evidence before assertions.

## Do NOT Touch

| Item | Reason |
|------|--------|
| `dashboard/data_access.py` | Framework-agnostic, works in any stack |
| `dashboard/data_manager.py` | Already correct for Vizro |
| `transform/` (dbt models) | Complete, tested, 77 tests pass |
| `export/export_json.py` | Complete, verified |
| `forecast/run_forecast.py` | Complete |
| `analysis/` (Marimo notebooks) | Complete |
| `docs/wireframes/` | Reference only, do not modify |
| `docs/LEARNINGS.md` §87–96 | Already written, only add §81-86 supersession banners |

## Sensitive Info (Redacted)

- HF Spaces URL: `https://albarpambagio-wfp-food-price.hf.space/`
- HF token: stored in `~/.cache/huggingface/credentials` (not in code)
- DuckDB path: `data/wfp.duckdb` (relative to project root)
