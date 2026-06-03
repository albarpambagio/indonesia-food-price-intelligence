# Handoff: Wireframe Evaluation Resolution

## Context

Indonesia Food Price Intelligence project — Phase 6 Vizro dashboard migration. Phases 0–5f complete. Phase 6 spike (A) + data layer port (B) complete. The wireframe evaluation document (`docs/wireframes/wfp-vizro-wireframe-evaluation.md`, 602 lines) has been reviewed against the Vizro e2e-flow skills. The task is to **resolve all open items in the evaluation** before passing the wireframes to the `dashboard-build` phase.

## What Was Done This Session

1. Read and analyzed the full wireframe evaluation document (602 lines)
2. Fetched and studied all 6 Vizro e2e-flow skills from `github.com/mckinsey/vizro/tree/main/vizro-e2e-flow`
3. Verified existing project state: dashboard code (`dashboard/app.py` is raw Dash), GeoJSON asset (`dashboard/assets/indonesia_provinces.geojson` — province-level, not island-group-level), data access layer, spike files
4. Identified 5 files needing updates, ~24 edit operations
5. User confirmed approach: GeoJSON option A (create separate island-group GeoJSON), update wireframes + evaluation + LEARNINGS.md

## Key Findings

### GeoJSON Mismatch
- Evaluation references `indonesia_island_groups.geojson` but actual file is `indonesia_provinces.geojson` (province-level, `properties.PROVINSI`)
- Need to create a new 5-feature island-group GeoJSON with `properties.island_group`
- Path must be `assets/` not `public/` for Vizro

### Interaction Patterns Mapped
| Page | Interaction | Vizro Pattern |
|------|-------------|---------------|
| 1 | Sidebar filters | Standard `vm.Filter` (no advanced pattern) |
| 2 | Driver toggle → show/hide charts | Dash callback (not a named pattern) |
| 3 | Map click → filter table + highlight KPI | Pattern 4 (Multi-Dimensional Slice) adapted; bidirectional KPI→map needs manual callback |
| 4 | Matrix click → scatter + stability + implication | Pattern 4 (Multi-Dimensional Slice) — actions chain |

### Critical Vizro Constraint
`vm.Figure` (KPI cards) cannot be a dynamic `set_control` source — only `vm.Graph` and `vm.AgGrid` carry click-data. This means Page 3's bidirectional KPI↔map interaction requires manual Dash callbacks, not declarative `va.set_control`.

## Files to Update

| # | File | Edit Count | Summary |
|---|------|-----------|---------|
| 1 | `docs/wireframes/wfp-vizro-wireframe-evaluation.md` | ~10 | Resolve §10.1/10.2 items, add §7.7 CSS classes, add interaction pattern mapping, reclassify §10 |
| 2 | `docs/wireframes/wfp-wireframe-page1-price-trends-forecast.md` | 2 | Model selector note, filter persistence annotation |
| 3 | `docs/wireframes/wfp-wireframe-page2-seasonal-patterns.md` | 2 | TanStack→AG Grid, week_relative clarification |
| 4 | `docs/wireframes/wfp-wireframe-page3-geographic-disparity.md` | 4 | TanStack→AG Grid, GeoJSON path, animate state machine, empty states |
| 5 | `docs/wireframes/wfp-wireframe-page4-commodity-signals.md` | 3 | TanStack→AG Grid, divergence threshold, empty states |
| 6 | `docs/LEARNINGS.md` | 3 | Archive React/Next.js sections 1–34, add §92–96 Vizro learnings, update ToC |

## Execution Plan

### Step 1: Page Wireframes (source of truth)
Edit the 4 page wireframe files to resolve open items:
- Replace all "TanStack Table" → "AG Grid" (pages 2, 3, 4)
- Page 1: Add model selector relocation note + filter persistence annotation
- Page 2: Clarify `week_relative` as integer (-8 to +6) with formatted tick labels
- Page 3: Update GeoJSON path to `assets/indonesia_island_groups.geojson` with `featureidkey="properties.island_group"`; add animate button state machine (IDLE→PLAYING→COMPLETE); add empty states
- Page 4: Add divergence threshold `abs(pre_2022_r - post_2022_r) > 0.2`; add empty states

### Step 2: Evaluation Document
Update `wfp-vizro-wireframe-evaluation.md`:
- §1 verdict table: update Page 3 friction from "Highest" to "High"
- §5.1: Add Mapbox note (no token required, `px.choropleth` + `featureidkey`)
- §5.3: Correct GeoJSON path to `assets/`
- §7.7 (new): CSS class reference table
- §7.8 (new): Interaction pattern mapping table
- §9.2: Move resolved items to new "Resolved" subsection
- §10: Reclassify — move 7 resolved items to §10.4, keep 3 in §10.3

### Step 3: LEARNINGS.md
- Add `## Archived: React/Next.js Stack (deprecated 2026-06-02)` before Section 1
- Sections 1–34 move under this heading (content unchanged)
- Add §92–96: component mismatch assessment, assets/ convention, Source→Control→Target, vm.Figure source limitation, conditional visibility callback
- Update Table of Contents

### Step 4: GeoJSON Asset (if in scope)
Create `dashboard/assets/indonesia_island_groups.geojson` with 5 features, one per island group (Java, Sumatera, Kalimantan, Sulawesi, Eastern Indonesia). Each feature needs `properties.island_group` matching the data values. Source the geometry from the existing `indonesia_provinces.geojson` by grouping province polygons.

**Note**: The GeoJSON creation may be out of scope for this session — confirm with user.

## Verification After Execution

```bash
# 1. Check no TanStack references remain
rg "TanStack" docs/wireframes/
# → Should return 0 results

# 2. Check evaluation has all resolved items marked
rg "§10\.[12]" docs/wireframes/wfp-vizro-wireframe-evaluation.md
# → All items should have resolution notes

# 3. Check LEARNINGS.md has new sections
rg "§9[2-6]" docs/LEARNINGS.md
# → Should find 5 new sections

# 4. Check GeoJSON path consistency
rg "indonesia_island_groups" docs/wireframes/
# → All references should point to assets/

# 5. Check page 3 has animate state machine
rg "IDLE.*PLAYING.*COMPLETE" docs/wireframes/wfp-wireframe-page3-geographic-disparity.md
# → Should find the state machine spec
```

## References

- Wireframe evaluation: `docs/wireframes/wfp-vizro-wireframe-evaluation.md`
- Page wireframes: `docs/wireframes/wfp-wireframe-page{1-4}-*.md`
- LEARNINGS.md: `docs/LEARNINGS.md` (3649 lines, sections 1–91)
- Implementation plan: `docs/implementation-plan.md §6.STACK` and `§6.HISTORY`
- Previous handoff: `docs/handoffs/HANDOFF-vizro-phase6-spike-data.md`
- AGENTS.md: project structure, conventions, dashboard architecture
- Vizro e2e-flow skills: `github.com/mckinsey/vizro/tree/main/vizro-e2e-flow/skills`
  - `wiring-vizro-actions/SKILL.md` — Source → Control → Target, patterns 1–5
  - `designing-vizro-layouts/SKILL.md` — 12-col grid, component sizing
  - `dashboard-build/SKILL.md` — build patterns, example_app.py template
  - `selecting-vizro-charts/SKILL.md` — chart types, KPI cards

## Suggested Skills

- **wiring-vizro-actions** — for interaction pattern mapping (Section 7.8 of evaluation)
- **designing-vizro-layouts** — to verify grid layout suggestions in evaluation are correct
- **dashboard-build** — to confirm custom_charts patterns match evaluation's implementation guidance
- **audit** — to verify the evaluation document's completeness against Vizro's actual capabilities

## Gotchas

- **Do NOT type commands in the terminal where `app.py` is running** — it kills the process
- The evaluation document is 602 lines — edits must be precise, use line-number-aware replacement
- LEARNINGS.md is 3649 lines — the ToC update (lines 7–90) needs careful handling
- GeoJSON creation (if in scope) requires merging province polygons into 5 island-group features — verify geometry validity after merge
- The `wiring-vizro-actions` skill uses `va.set_control` which only works with `vm.Graph` and `vm.AgGrid` sources — `vm.Figure` (KPI cards) cannot be sources
