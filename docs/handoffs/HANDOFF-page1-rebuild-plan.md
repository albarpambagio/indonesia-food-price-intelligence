# Handoff: Page 1 Dashboard Rebuild — Plan Approved, Ready for Execution

**Generated:** 2026-06-08 11:07
**Trigger:** Agent was asked to plan Page 1 (Price Trends & Forecast) development for the Marimo-native dashboard rewrite after the `dashboard/` directory was deleted for a clean rebuild.

---

## Context Snapshot

The dashboard code was deleted 2026-06-08 for a clean rebuild. All pipeline layers (dbt marts, DuckDB, forecast, export) remain intact. The architecture blueprint is preserved in `docs/handoffs/HANDOFF-dashboard-marimo-rewrite.md` (data schemas, cross-cell scoping, dual-path resolution, Page 4 sync, failure-mode validation).

This handoff covers only **Page 1** — the other 3 pages have placeholders and will be built in subsequent sessions.

---

## Key Decisions Made (2026-06-08)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data source for Page 1 | `price_trends_national.json` (national avg) | `price_trends.json` only has Cooking Oil province data; Page 1 must show all 4 commodities |
| Island filter on Page 1 | No effect — callout explains | Island group only meaningful for Cooking Oil province data; national-level trend page doesn't need it |
| Non-Page-1 tabs | `mo.md("Coming soon")` placeholders | Clean skeleton; pages built incrementally |
| Buy signal logic | Simple 3-tier: forecast avg vs current price (<98% = BUY, >102% = WATCH, else HOLD) | Per user request |
| YoY computation | Annual average price change (12-month avg per year) | Per user request |
| marimo-notebook skill | Install at project level during implementation | Handoff's suggested skill; marginal gain since patterns already in AGENTS.md |

---

## Build Plan (Pending Execution)

### Prerequisites — Generate Data

The `dashboard/` directory and all its contents need to be created from scratch. Before writing any code, generate the data files:

```bash
uv sync
uv run python forecast/run_forecast.py     # → dashboard/public/data/forecast.json
uv run python export/export_json.py        # → dashboard/public/data/*.json (7 files)
```

Also copy the Islamic calendar CSV:
```bash
cp transform/seeds/islamic_calendar.csv dashboard/public/data/
```

### Files to Create

| File | Purpose |
|------|---------|
| `dashboard/__init__.py` | Package marker |
| `dashboard/data_static.py` | Dual-path JSON/CSV loader (`Path(__file__)` anchor) |
| `dashboard/build.py` | WASM build script (`marimo export html-wasm`) |
| `dashboard/charts/__init__.py` | Package marker |
| `dashboard/charts/kpi_sparklines.py` | `sparkline_chart()` — tiny `go.Figure` ~60px, axes hidden |
| `dashboard/app.py` | ~20-cell Marimo notebook (see cell layout below) |

### `dashboard/app.py` Cell Layout

Referenced from: `docs/handoffs/HANDOFF-dashboard-marimo-rewrite.md` (full cross-cell scoping model, data contract)

| Cell | Exports | Key Dependencies |
|------|---------|-----------------|
| PEP 723 header | — | marimo, pandas, plotly, numpy |
| `imports` | `mo, go, px, pd, np, Path, json` | — |
| `data_loading` | `price_df, forecast_df` | `data_static.py` helpers |
| `global_filters` | `commodity_dd, island_dd, year_slider` | `mo.ui.dropdown`, `mo.ui.range_slider` |
| `page1_derived_data` | `filtered_df, latest_prices_df, yoy_df, buy_signals_df` | Global filters, forecast_df |
| `kpi_cards_page1` | `kpi_cards_output` | `mo.stat()` × 4 with sparklines |
| `chart_commodity_radio` | `chart_commodity_radio` | Local `mo.ui.radio` for trend chart |
| `trend_chart` | `trend_chart_output` | `mo.ui.plotly(go.Figure)` actuals + forecast + CI |
| `buy_signal_monitor` | `buy_signal_output` | `mo.md()` with ● colored dots |
| `yoy_table` | `yoy_table_output` | `mo.ui.table` with 🔴 🟢 emoji flags |
| `footnote` | `footnote_output` | `mo.callout(kind="info")` |
| `page1_tab_content` | `page1_content` | `mo.vstack` assembly of all above |
| `page2_placeholder` | `page2_content` | `mo.md("Coming soon")` |
| `page3_placeholder` | `page3_content` | `mo.md("Coming soon")` |
| `page4_placeholder` | `page4_content` | `mo.md("Coming soon")` |
| `tab_assembly` | — (final expression) | `mo.ui.tabs({"Price Trends": page1_content, ...})` |

### Verification

```bash
ruff check dashboard/
marimo check dashboard/app.py
uv run python dashboard/app.py          # script mode, exits cleanly
marimo export html-wasm dashboard/app.py -o /tmp/test.html --mode run -f
```

---

## Reference Artifacts (Do Not Duplicate)

| Artifact | Path | What It Contains |
|----------|------|-----------------|
| Architecture bluepr. | `docs/handoffs/HANDOFF-dashboard-marimo-rewrite.md` | Full cross-cell scoping, data contracts, dual-path resolution, Page 4 sync, failure-mode validation |
| Page 1 wireframe | `docs/wireframes/marimo-wireframe-page1-price-trends.md` | Detailed cell-level design, code snippets, layout mockups |
| Architecture overview | `docs/wireframes/marimo-wireframe-architecture.md` | Global filter behavior per page, tab assembly pattern |
| Project conventions | `AGENTS.md` | Marimo conventions (§378–413), LSP false positives, key conventions |
| Implementation plan | `docs/implementation-plan.md` | Phase 6 rebuild context (§6.MARIMO), full pipeline status |
| Data shapes | `HANDOFF-dashboard-marimo-rewrite.md` Data Contract § | All 8 DataFrame schemas with columns, types, sources |

---

## Suggested Skills

| Skill | When to Use |
|-------|-------------|
| `marimo-notebook` | Writing/editing `dashboard/app.py` — cell structure patterns, UI component reference, script mode patterns, `mo.stop()` usage. Install at project level via `.opencode/skills/marimo-notebook/SKILL.md` if not already available. |
| `systematic-debugging` | If `marimo check` fails, chart rendering issues in WASM mode, or `mo.ui.plotly()` displays incorrectly |
| `handoff` | When transitioning to Pages 2–4 after Page 1 is verified |
