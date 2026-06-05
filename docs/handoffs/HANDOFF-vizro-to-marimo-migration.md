# Handoff: Vizro → Marimo Migration

**Generated:** 2026-06-05 14:04
**Context:** Decision to abandon Vizro/Dash dashboard framework in favor of a single Marimo notebook + WASM HTML export deployed to Cloudflare Pages. Previous framework migration (Dash → Vizro) was in progress but only 2 of 4 pages were wired; remaining Vizro bugs and two-framework burden led to the pivot.

---

## Migration Decision

**Chosen approach:**
- Single Marimo notebook (`dashboard/app.py`) with `mo.ui.tabs()` for 4-page navigation
- Static JSON data files (no DuckDB at dashboard runtime)
- Exported as WASM HTML via `marimo export html-wasm` → Cloudflare Pages
- Chart functions kept in `dashboard/charts/*.py` with `@capture` decorators stripped

**Rejected alternatives:**
- Multi-notebook MPA via `create_asgi_app()` — per-page Pyodide reload in WASM mode
- `mo.routes()` SPA — more complex than needed; `mo.ui.tabs()` is simpler

**Why Marimo over Vizro:**
- Vizro 0.1.x bugs: first-render timing, "All" filter as literal, conditional visibility hack
- Two frameworks coexisting (Vizro Pages 1-2, Dash Pages 3-4) — 22 files, ~2,224 LOC
- Marimo already in stack (`marimo>=0.23.0`), reactive (no callbacks), pure Python (no Pydantic configs)

**Why WASM HTML over server mode:**
- Static hosting on Cloudflare Pages (free tier, fast CDN)
- No server to manage
- `urllib.request` works in Pyodide for loading JSON data at runtime

---

## Suggested Skills

The next agent should load these skills in the first invocation:

| Skill | When to Use |
|-------|-------------|
| `handoff` | Already loaded (this document) |
| `marimo-notebook` | When creating/charting Marimo `.py` notebook files — provides cell structure, reactivity, UI component reference, script mode patterns |
| `cloudflare-pages-deploy` | When setting up Cloudflare Pages deployment, `wrangler.toml`, GitHub Actions, build command config |
| `systematic-debugging` | If any Marimo notebook fails `marimo check`, WASM export errors, or chart rendering issues on Cloudflare Pages |

Note: `marimo-notebook` is a community skill hosted at `https://github.com/marimo-team/skills` — use `websearch` to fetch its content or reference the raw URL `https://raw.githubusercontent.com/marimo-team/skills/main/skills/marimo-notebook/SKILL.md`. The DEPLOYMENT, EXPORTS, UI, and EXPENSIVE reference docs under that skill are critical.

---

## What Exists (Do NOT Re-Do)

| Item | Location |
|------|----------|
| Full project context | `AGENTS.md` — 300+ lines covering stack, schema, conventions, QA checks |
| Data validation strategy | `AGENTS.md` §Data Traceability & Validation |
| dbt model architecture | `AGENTS.md` §Data Schema + §dbt Implementation Evaluation |
| Export pipeline | `export/export_json.py` — generates all 7 JSON files in `dashboard/public/data/` |
| Forecast pipeline | `forecast/run_forecast.py` — generates `forecast.json` |
| Compute helpers | `dashboard/data_access.py` — `get_latest_prices()`, `compute_yoy_delta()`, `compute_heatmap_matrix()`, `compute_ramadan_overlay()`, `compute_action_windows()` — these are pure pandas and **must be kept** |
| GeoJSON for choropleth | `dashboard/assets/indonesia_provinces.geojson` |
| LSP/linting setup | `AGENTS.md` §LSP Quality — ruff + ty, known false positives |

**Chart functions (10 files in `dashboard/charts/`) — to be kept and modified:**
| File | LOC | Change Needed |
|------|-----|--------------|
| `trend_forecast.py` | 114 | Strip `@capture`, remove internal `load_forecast_data()` → add `forecast_df` param, remove try/except |
| `kpi_sparklines.py` | 133 | Strip `@capture` only |
| `yoy_bar.py` | 74 | Strip `@capture` only |
| `signal_badges.py` | 95 | Strip `@capture` only |
| `action_cards.py` | 178 | Strip `@capture`, remove internal `load_islamic_calendar()` → add `islamic_cal` param |
| `seasonal_heatmap.py` | 61 | Strip `@capture`, change `import vizro.plotly.express as px` → `import plotly.express as px` |
| `ramadan_overlay.py` | 95 | Strip `@capture` only (already takes `islamic_cal` as param) |
| `harvest_chart.py` | 108 | Strip `@capture` only |
| `yearend_chart.py` | 68 | Strip `@capture` only |
| `seasonal_summary_table.py` | 58 | Strip `@capture("ag_grid")`, return `pd.DataFrame` instead of AG Grid format |

---

## What to Create

### 1. `dashboard/data_static.py` — JSON data layer

Reads `dashboard/public/data/*.json` via filesystem (local) or `urllib.request` (WASM). Single function:

```python
def load_json(name: str, key: str | None = None) -> pd.DataFrame:
```

JSON file names (without `.json`): `price_trends`, `price_trends_national`, `forecast` (key="data" for records, key="metadata" for metadata dict), `seasonal_patterns`, `geographic_disparity`, `commodity_correlation`, `correlation_summary`.

### 2. `dashboard/app.py` — Single Marimo notebook

Structure (6 cells):

| Cell | Purpose | Depends On | Returns |
|------|---------|-----------|---------|
| Cell 1: `setup()` | Imports — all chart functions, pandas, marimo, data_static | nothing | All module references |
| Cell 2: `load_data()` | Load all 8 JSON datasets via `load_json()` | `load_json` | 8 DataFrames |
| Cell 3: `global_filters()` | `mo.ui.dropdown` (commodity, island), `mo.ui.range_slider` (year) | `mo` | 3 reactive widgets |
| Cell 4: `tab_trends()` | Page 1 charts — `kpi_sparklines`, `trend_forecast`, `yoy_bar`, `signal_badges` | data, filters, chart fns | `mo.vstack` of `mo.ui.plotly` |
| Cell 5: `tab_seasonal()` | Page 2 charts + `mo.ui.radio` for driver + `mo.ui.table` for action windows | data, filters, chart fns | `mo.vstack` |
| Cell 6: `dashboard()` | `mo.ui.tabs({...})` tying all tabs together | 4 tab outputs | Final layout |

Remaining pages (Geographic Disparity, Commodity Signals) are placeholders until their chart functions are migrated from Dash — see `dashboard/pages/geographic_disparity.py` and `dashboard/pages/commodity_signals.py` for the old implementations.

### 3. `dashboard/build.py` — WASM export script

```python
subprocess.run(["uv", "run", "marimo", "export", "html-wasm",
    "app.py", "-o", "dist/index.html", "--mode", "run", "-f"])
shutil.copytree("public/data", "dist/data")
shutil.copytree("assets", "dist/assets")
```

---

## What to Delete (11 files, ~944 LOC)

| File | LOC | Reason |
|------|-----|--------|
| `dashboard/app.py` (current Vizro one) | 18 | Replace with Marimo notebook |
| `dashboard/data_manager.py` | 23 | Vizro `data_manager` registration — obsolete |
| `dashboard/pages/price_trends.py` | 122 | Vizro `vm.Page` config |
| `dashboard/pages/seasonal_patterns.py` | 119 | Vizro `vm.Page` config |
| `dashboard/pages/geographic_disparity.py` | 206 | Dash page (chart logic to extract first) |
| `dashboard/pages/commodity_signals.py` | 285 | Dash page (chart logic to extract first) |
| `dashboard/components/filters.py` | 64 | Dash filter bar |
| `dashboard/components/layout.py` | 37 | Dash layout helpers |
| `dashboard/components/kpi_cards.py` | 54 | Dash KPI cards |
| `dashboard/spike/app.py` | 18 | Vizro test artifact |
| `dashboard/spike/custom_charts.py` | 18 | Vizro test artifact |

**Ordering:** Delete Pages 3/4 last — their chart logic (choropleth map, correlation heatmap, etc.) should be extracted into `dashboard/charts/*.py` first to avoid losing them.

---

## What to Modify

### `dashboard/data_access.py`
- **Remove:** `_connect()`, `load_mart()`, `load_forecast_data()`, `load_forecast_metadata()`, `load_islamic_calendar()` — all DuckDB-specific
- **Keep:** `get_latest_prices()`, `compute_yoy_delta()`, `compute_heatmap_matrix()`, `compute_ramadan_overlay()`, `compute_action_windows()` — pure pandas helpers

### `dashboard/charts/*.py` (10 files)
- Strip `@capture("graph")` / `@capture("ag_grid")` decorator from each exported function
- Fix imports in `seasonal_heatmap.py`
- Remove internal data loading in `trend_forecast.py` and `action_cards.py` — accept data as parameters instead
- Remove try/except blocks in `trend_forecast.py`

---

## Dependencies to Remove from `pyproject.toml`

```toml
# Remove these:
vizro, dash, dash-bootstrap-components, dash-ag-grid, chart-studio, gunicorn
```

These are safe to remove after the migration is complete and verified.

---

## Deployment

**Target:** Cloudflare Pages (static WASM HTML)
**Build:** `uv run python dashboard/build.py` → output `dist/`
**Cloudflare config:**
- Build command: `uv run python dashboard/build.py`
- Output directory: `dist`
- No framework preset
- One-time setup: `npx wrangler login && npx wrangler pages project create food-price-dashboard --production-branch main`

**WASM caveat:** Each page load downloads ~4MB of Pyodide WASM runtime. Cloudflare edge caching makes this a once-per-session cost (~5s initial, then instant). Data files (`dist/data/*.json`) are cached aggressively.

---

## Validation Checklist for Next Agent

- [ ] `marimo check dashboard/app.py` passes with no errors
- [ ] `uv run python dashboard/app.py` (script mode) exits cleanly
- [ ] `marimo export html-wasm dashboard/app.py -o /tmp/test.html --mode run` succeeds
- [ ] `ruff check dashboard/` — only pre-existing E501/F821 false positives
- [ ] All 10 chart functions render without `@capture`
- [ ] `dist/index.html` + `dist/data/*.json` deploy to Cloudflare Pages preview
- [ ] Tabs switch instantly in browser
- [ ] Filter dropdowns update charts reactively
- [ ] DuckDB is no longer needed at dashboard runtime (pipeline still needs it)
- [ ] `dashboard/pages/geographic_disparity.py` chart logic extracted before deletion
- [ ] `dashboard/pages/commodity_signals.py` chart logic extracted before deletion

---

## Open Questions / Future Work

1. **Pages 3-4 chart migration:** The Dash implementations in `dashboard/pages/geographic_disparity.py` and `dashboard/pages/commodity_signals.py` need their Plotly chart functions extracted into `dashboard/charts/` before deletion. Their data sources (`geographic_disparity.json`, `commodity_correlation.json`, `correlation_summary.json`) are ready.
2. **Cross-page filter state:** `mo.ui.tabs()` doesn't share URL state. If the user wants permalink-able filter settings, add `mo.query_params()` for filter serialization.
3. **AG Grid replacement:** `mo.ui.table()` is the replacement. The `seasonal_summary_table` chart function needs to return a plain `pd.DataFrame` instead of the AG Grid `columnDefs`/`rowData` format.
