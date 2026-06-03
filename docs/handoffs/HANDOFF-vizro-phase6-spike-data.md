# Handoff: Phase 6 Spike (A) + Data Layer Port (B)

## Context

Indonesia Food Price Intelligence project — migrating from Dash 4.1.0 to Vizro 0.1.54 dashboard framework. Phases 0–5f are complete. Phase 6 is the dashboard implementation. The user wants to execute **Phase A (0.5-day feasibility spike)** and **Phase B (data layer port)** from the implementation plan.

## Decision Gate

The spike is a **go/no-go gate**. If it passes (≤0.5 day, <50 LOC per custom chart), proceed to Phase C (page implementation). If it fails, revert to the Dash plan preserved in `docs/implementation-plan.md §6.HISTORY`.

**Why Vizro over Dash**: Cross-filtering requirement. 4 pages need "click chart → filter all" UX. Vizro's `va.set_control` makes this declarative; Dash requires custom callbacks (~80 LOC × 6 pairs). This was the decisive criterion (+8 weighted).

## Current State

| Item | Status |
|------|--------|
| Vizro installed | `vizro==0.1.54` in `pyproject.toml` and installed |
| Dashboard currently | Raw Dash 4.1.0 + DBC 2.0.4, 4 pages in `dashboard/pages/` |
| `dashboard/data_manager.py` | Does NOT exist yet |
| `dashboard/spike/` | Does NOT exist yet |
| `dashboard/data_access.py` | Working, queries DuckDB `wfp_marts` schema directly, `lru_cache(maxsize=32)` |
| JSON exports | 7 files in `dashboard/public/data/` (only `forecast.json` consumed) |

## Execution Plan

### Phase A: Spike

1. **6.A.1** — Confirm version: `uv run python -c "import vizro; print(vizro.__version__)"` (already 0.1.54)
2. **6.A.2** — Create `dashboard/spike/app.py` (~30 LOC): minimal 1-page Vizro app with `vm.Page`, one `vm.Graph`, one `vm.Filter`, real data via `data_manager`
3. **6.A.3** — Create `dashboard/spike/custom_charts.py` (~15 LOC): wrap lag heatmap (`analysis/eda.py` line 623, `px.imshow` on `mart_correlation_summary`) with `@capture("graph")` decorator
4. **6.A.4** — Wire to DuckDB: `data_manager["correlation_summary"] = lambda: load_mart("mart_correlation_summary")`
5. **6.A.5** — Run `uv run python dashboard/spike/app.py`, load `http://localhost:7860`, verify chart renders
6. **6.A.6** — Decision gate: log to `logs/migration.log`

### Phase B: Data Layer Port

1. **6.B.1** — Create `dashboard/data_manager.py`: register all 5 marts + forecast as dynamic data via `data_manager["name"] = load_fn` (function ref, NOT call)
2. **6.B.2** — Verify export pipeline unchanged: `uv run python export/export_json.py`
3. **6.B.3** — Smoke test: verify 8 keys in data_manager

## Key Vizro Conventions (from vizro-e2e-flow skills)

These are CRITICAL — deviating causes blank charts or runtime errors:

```python
# IMPORTS — always use vizro.plotly.express, not plotly.express
import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture
import plotly.graph_objects as go  # OK — no vizro wrapper for go

# DATA REGISTRATION — function reference, NOT function call
data_manager["my_data"] = load_my_data  # CORRECT
# data_manager["my_data"] = load_my_data()  # WRONG — static, won't refresh

# CUSTOM CHART — strict contract
@capture("graph")
def my_chart(data_frame):  # MUST accept data_frame as first arg
    fig = go.Figure()      # or px.* calls
    # ... all data from data_frame, no external lookups
    return fig             # MUST return go.Figure

# APP ENTRY — build first, then run
app = Vizro().build(dashboard)
app.run(port=7860, debug=True)  # NOT Vizro().build(dashboard).run()
```

## Files to Create

| File | Purpose | LOC |
|------|---------|-----|
| `dashboard/spike/app.py` | Minimal spike app | ~30 |
| `dashboard/spike/custom_charts.py` | `@capture("graph")` lag heatmap | ~15 |
| `dashboard/data_manager.py` | Register 8 data sources | ~20 |

## Files NOT Modified

- `dashboard/data_access.py` — kept as-is, wrapped by data_manager
- `dashboard/app.py` — Dash app preserved until Phase C replaces it
- `dashboard/pages/*.py` — Dash pages preserved until Phase C
- `export/export_json.py` — must remain unchanged
- `pyproject.toml` — vizro already listed

## References

- Implementation plan: `docs/implementation-plan.md §6.SPIKE` (L390-403) and `§6.DATA` (L403-414)
- AGENTS.md: project structure, conventions, dashboard architecture
- Vizro e2e flow skills: `github.com/mckinsey/vizro/tree/main/vizro-e2e-flow/skills`
  - `dashboard-build/SKILL.md` — build patterns, example_app.py template
  - `writing-vizro-yaml/SKILL.md` — component syntax, common pitfalls
  - `designing-vizro-layouts/SKILL.md` — 12-col grid, sizing rules
  - `wiring-vizro-actions/SKILL.md` — `va.set_control` cross-filter pattern
  - `custom_charts_guide.md` — `@capture("graph")` contract
  - `data_management.md` — static vs dynamic, caching, registration

## Suggested Skills

- **dashboard-build** — for Phase C page implementation patterns
- **wiring-vizro-actions** — for cross-filter `va.set_control` when building interactive pages
- **designing-vizro-layouts** — for 12-col grid layout of each page
- **selecting-vizro-charts** — for chart type decisions and KPI card patterns
- **writing-vizro-yaml** — for component syntax and pitfalls

## Verification After Execution

```bash
# Phase A smoke test
uv run python dashboard/spike/app.py
# → Load http://localhost:7860, chart must render with real DuckDB data

# Phase B smoke test
uv run python -c "from dashboard.data_manager import *; from vizro.managers import data_manager; print(list(data_manager._data_manager._data.keys()))"
# → Expected: 8 keys

# Export pipeline check (must still work)
uv run python export/export_json.py
# → Must log to pipeline.lineage.export_status
```

## Gotchas

- **Do NOT type commands in the terminal where `app.py` is running** — it kills the process
- `@capture("graph")` functions must NOT call `data_manager[data_frame]` internally — use the `data_frame` arg directly
- Filter `targets:` should be omitted unless you need to limit which components are affected
- `show_in_url=True` is NOT needed in Phase A/B — only for cross-page filters in Phase C
