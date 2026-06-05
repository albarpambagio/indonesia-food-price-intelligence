# Handoff: Page 1 & Page 2 Explainer Feature Gap Fixes

**Generated:** 2026-06-05 13:33
**Session mode:** Plan → Build (transitioned mid-session after evaluation + planning)
**Next session focus:** Execute the implementation plan to close Page 1 / Page 2 explainer feature gaps in `docs/implementation-plan.md:439-490`.

---

## TL;DR

Evaluated the "Page Explainer" promises for Page 1 (Price Trends & Forecast) and Page 2 (Seasonal Patterns) against the actual Vizro code in `dashboard/pages/`. Identified **6 gaps** spanning both pages. User confirmed: plan fixes for all gaps, with **dynamic** action cards on Page 2 (via existing `compute_action_windows()` in `dashboard/data_access.py:218`). Plan organised into **6 commits**, ~3.5 hours total effort. Three user-input decisions are still open (B-1, B-2, B-3) — defaults provided, awaiting confirmation.

---

## Conversation Summary

### What was done in this session

1. **Read** `docs/implementation-plan.md` (full Phase 6 §6.PAGES) and `AGENTS.md`.
2. **Read** all Vizro source files: 2 page modules, 9 chart modules, `data_access.py`, `data_manager.py`, `app.py`.
3. **Read** 2 existing handoffs: `HANDOFF-page1-bugs-remaining.md` and `HANDOFF-page2-seasonal-patterns-implementation.md` (first 200 lines).
4. **Produced evaluation** comparing the "Page Explainer" text in the plan to the actual code (see "Gaps Identified" below).
5. **Asked the user 2 questions**; user answered: "Plan fixes for all gaps" + "Dynamic via `compute_action_windows()`".
6. **Produced implementation plan** with 6 commits, decision points, validation, risks. Plan lives only in this conversation — not yet saved elsewhere.

### Decisions made (binding for next session)

| Decision | Choice | Source |
|----------|--------|--------|
| Fix scope | **All gaps** (Island + Year filters on both pages, 3 dynamic action cards, harvest_chart bug, doc reconciliation) | User Q1 |
| Action cards | **Dynamic** via `compute_action_windows()` in `dashboard/data_access.py:218` | User Q2 |
| Plan structure | 6 sequential commits, each independently testable | Inferred from AGENTS.md commit pattern |

---

## Gaps Identified (not in any other artifact)

| # | Gap | Location | Severity |
|---|-----|----------|----------|
| **G1** | Page 1 missing Island filter + Year Range filter (only commodity implemented; AGENTS.md:347-348 promises all 3) | `dashboard/pages/price_trends.py:94-109` (controls list) | High — AGENTS.md contradiction |
| **G2** | Page 2 missing Island + Year Range filters (plan §6.C.2.5c promised all 3) | `dashboard/pages/seasonal_patterns.py:84-111` | High — plan task incomplete |
| **G3** | Page 2 action cards: plan + explainer promise **3 distinct cards** (Action Now / Upcoming Spikes / Safe to Lock), only **1 static card** implemented | `dashboard/pages/seasonal_patterns.py:16-29` (`_build_action_cards`) | High — explainer contradiction |
| **G4** | Page 2 `harvest_chart` missing from `s2-param-commodity.targets` list — copy-paste bug, harvest chart does not respond to commodity filter | `dashboard/pages/seasonal_patterns.py:88-91` | Medium |
| **G5** | `docs/implementation-plan.md` has **two contradictory Page 2 explainers** (lines 464-468 and 488-490); first describes a single driver-filtered line chart, second describes 3 separate driver charts. Code follows the second. | `docs/implementation-plan.md:464-490` | Low — doc-only |
| **G6** | `AGENTS.md:341` Dashboard Architecture table still lists Page 2 data source as `seasonal_patterns.json`. Plan was corrected to `mart_price_trends_national` + `int_islamic_calendar` in LEARNINGS §99, but AGENTS.md is stale. | `AGENTS.md:341` | Low — doc-only |

**Other observations** (not gaps, but worth knowing):
- `dashboard/charts/harvest_chart.py:49` hardcodes `"Rice"` regardless of `commodity_filter` — with G3 fix, this will visibly affect only Rice. Add a "no harvest signal" notice for other commodities.
- `kpi_sparklines` and `signal_badges` show "latest price" semantics. Adding a year-range filter requires deciding what "latest" means (range-end vs always-current). See open question B-1.
- Page 1 known Vizro 0.1.53 bug: sidebar-toggle workaround (LEARNINGS §98). Adding 3 controls instead of 1 may exacerbate — observe in smoke test, do not "fix" the workaround pattern.

---

## Plan Summary (commit-by-commit)

> **Full commit details, code diffs, and validation commands live in the implementation plan — not reproduced here to avoid duplication. See "Reference Artifacts" §A.1 for the full plan.**

| # | Commit | Files touched | Effort | Risk |
|---|--------|---------------|--------|------|
| 1 | `fix: Page 1 — add Island + Year Range filters (closes 6.C.1.4)` | `pages/price_trends.py` + 4 chart files + `data_access.py` + LEARNINGS §101 | 50 min | Low |
| 2 | `fix: Page 2 — fix harvest_chart commodity target` | `pages/seasonal_patterns.py` (1 line) | 2 min | None |
| 3 | `fix: Page 2 — add Island + Year Range filters (closes 6.C.2.5c)` | `pages/seasonal_patterns.py` + 4 chart files | 45 min | Low |
| 4 | `feat: Page 2 — dynamic 3 action cards via compute_action_windows` | New `charts/action_cards.py` + helper in `data_access.py` + page wiring + LEARNINGS §102 | 80 min | Medium |
| 5 | `fix: harvest_chart — Rice-only with data-availability notice` | `charts/harvest_chart.py` | 15 min | None |
| 6 | `docs: reconcile Page 2 explainers + update AGENTS.md Page 2 data source` | `docs/implementation-plan.md`, `AGENTS.md` | 30 min | None |

Commits 2 + 3 are independently mergeable; 4 + 5 depend on 3 (need island filter in place first to test action cards across all filter combinations).

---

## Open Questions (require user input before commit 1)

> **Defaults provided below — if the user accepts all defaults, proceed without asking.**

| ID | Question | Default |
|----|----------|---------|
| **B-1** | KPI cards with year-range filter — re-interpret "latest" as range-end? | **Yes** — implement (a), add LEARNINGS §101 documenting the semantic |
| **B-2** | Page 2 action cards driver-toggle mechanism — `vm.Card` static vs `@capture("graph")` 3-panel subplot | **`@capture("graph")` figure with 3 subplot panels** (rendered as one Vizro component, swapped via Pattern A empty-swap already used by other driver charts) |
| **B-3** | Island filter on Page 1 — no-op for national data (Page 1 reads from `mart_price_trends_national` which has no `island_group` column) | **Inert with data-availability notice** (matches the existing pattern on Page 2) |
| B-4 | Harvest chart commodity handling | Rice-only with notice (chart name says "harvest" = Rice's domain) |
| B-5 | Sidebar-toggle workaround (LEARNINGS §98) with 3 controls | No mitigation; document observation in handoff |
| B-6 | Year-range `vm.Filter` semantic on `kpi_sparklines` / `signal_badges` | Accept the semantic shift per B-1 |
| B-7 | Action card copy ("Action Now / Upcoming / Safe to Lock") | Draft from `compute_action_windows()` output; flag for stakeholder review (not blocking) |

**If any default is rejected**, the implementation approach changes — re-confirm before commit 4 (action cards) and commit 1 (KPI semantic).

---

## Pre-work Validation

Run these BEFORE making any code changes. If any fails, stop and report.

```bash
# 1. Confirm Vizro smoke test passes (do not run dashboard/app.py — blocks forever)
uv run python -c "from dashboard.app import app; print(f'Pages: {len(dashboard.pages)}')"
# Expected: Pages: 2

# 2. Confirm compute_action_windows returns the columns the plan needs
uv run python -c "
from dashboard.data_access import compute_action_windows, load_mart, load_islamic_calendar
df = load_mart('mart_price_trends_national')
cal = load_islamic_calendar()
w = compute_action_windows(df, 'Ramadan', cal)
print('Columns:', w.columns.tolist())
print('Expected: [commodity, spike_pct, consistency_score, total_years, lead_months, data_scope]')
print('Rows:', len(w))
print(w)
"

# 3. Confirm harvest_chart current behaviour (Rice only)
uv run python -c "
from dashboard.data_access import load_mart
from dashboard.charts.harvest_chart import harvest_chart
df = load_mart('mart_price_trends_national')
fig = harvest_chart(df, driver='Harvest')
print('Harvest chart commodity (Rice only?):', sorted(set(t.x[0] for t in fig.data)))
"
# Expected: ['Jan', 'Feb', ..., 'Dec'] (all 12 month labels) — Rice only

# 4. Lint + format baseline
ruff check .
ruff format --check .
```

---

## Reference Artifacts (read these, do not duplicate)

| Path | Purpose |
|------|---------|
| `docs/implementation-plan.md:439-490` | Page 1 + Page 2 explainer text + task lists (§6.C.1, §6.C.2) |
| `docs/implementation-plan.md:341-356` | Vizro stack decision rationale |
| `docs/LEARNINGS.md:§87-100` | Vizro patterns (show_in_url, custom_charts, data_manager, Pydantic scoping, vm.Figure limitation, conditional visibility, vm.Filter "All" bug, first-render timing, Page 2 data source mismatch, month_relative reframing) |
| `docs/LEARNINGS.md:§101` | **TO ADD** — `vm.Filter(column="month")` year-range pattern + island_filter no-op caveat |
| `docs/LEARNINGS.md:§102` | **TO ADD** — Page 2 dynamic action cards pattern (`@capture("graph")` 3-panel subplot) |
| `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md:124-138` | Island filter per-commodity override logic (Cooking Oil only — copy this pattern into Page 2 chart functions) |
| `docs/handoffs/HANDOFF-page1-bugs-remaining.md` | Page 1 known sidebar-toggle workaround + root cause hypotheses |
| `AGENTS.md:345-352` | Global filter spec (Commodity / Island / Year — all 3 are promised on every page) |
| `AGENTS.md:378-388` | Vizro code style conventions (custom_charts wrapper, data_manager registration, plotly_white template) |
| `dashboard/pages/price_trends.py` | Page 1 current state — add 2 controls to `controls=[...]` list at line 94 |
| `dashboard/pages/seasonal_patterns.py` | Page 2 current state — add 2 controls, fix harvest target, replace 1 card with 3 |
| `dashboard/data_access.py:218-333` | `compute_action_windows()` — already returns columns the plan needs |
| `dashboard/data_access.py:120-132` | `load_islamic_calendar()` — already cached, ready to use |

---

## Suggested Skills

The next session should invoke these skills (in this order) before writing code:

1. **`systematic-debugging`** — Before commit 1, verify whether G1 (missing Island + Year filters on Page 1) has the same root cause as the known Page 1 sidebar-toggle bug (LEARNINGS §98). If the bug is timing-related and the missing filters would interact with the first-render race, debug first. Do not "fix" the workaround pattern — it's a documented Vizro limitation.

2. **`tdd`** — For commits 1, 3, 4 (the non-trivial changes), write the smoke test in §5 of the original plan first. Watch it fail (filters not wired / cards not rendering 3), then implement, watch it pass. The 5 smoke tests in the plan are the red→green loop.

3. **`brainstorming`** — Before commit 4 (3 dynamic action cards), confirm B-2 with the user: `vm.Card` text vs `vm.Graph` 3-panel subplot. The choice changes the wireframe layout fundamentally. Also confirm the helper function signatures in `dashboard/data_access.py`.

4. **`frontend-design`** — For commit 4's card layout: `vm.Container` grid spec, `vm.Flex` row/column, matching Page 1's visual rhythm (see `dashboard/pages/price_trends.py:31-56` for the `_build_model_info_card` Container pattern).

5. **`verification-before-completion`** — Run all 5 smoke tests in the plan after each commit. Do NOT run `dashboard/app.py` (blocks forever per AGENTS.md).

6. **`polish`** — Final pass after commit 6: color consistency with Page 1's `COMMODITY_COLORS` map (4-color palette #4C72B0/#DD8452/#55A868/#C44E52), heatmap scale, action card typography, no `== True` lint violations (ruff E712 — 7 instances flagged in AGENTS.md).

7. **`clarify`** — Review UX copy on the 3 action cards. Card titles "Action Now / Upcoming Spikes / Safe to Lock" are placeholders — flag for stakeholder review (Procurement Analyst, Category Manager) per the project's audience model in `AGENTS.md:23-30`.

---

## What NOT to Do

- Do **not** edit `docs/handoffs/HANDOFF-page2-seasonal-patterns-implementation.md` (it is reference-only). The Page 2 island override pattern at lines 124-138 should be copied into a NEW helper in `dashboard/data_access.py` (not modified in place).
- Do **not** add `commodity_filter="commodity_filter"` literal-string defaults in any new `vm.Graph(figure=fn(...))` call (LEARNINGS §98 bug).
- Do **not** use `vm.Filter` for any control with an "All" sentinel in its options (LEARNINGS §97 bug). Use `vm.Parameter` instead. The Year Range filter is the only one that can use `vm.Filter` (it uses numeric min/max bounds, not an "All" option).
- Do **not** run `uv run python dashboard/app.py` for verification — blocks forever (AGENTS.md:539).
- Do **not** modify the data access layer's pre-computation logic (`compute_heatmap_matrix`, `compute_ramadan_overlay`, `compute_action_windows`) — extend with new helpers, do not refactor.
- Do **not** touch `transform/` dbt models, `forecast/`, or `analysis/` notebooks — out of scope for Phase 6 dashboard fixes.
- Do **not** amend or force-push any commits. Follow AGENTS.md commit style (`feat:`, `fix:`, `docs:` prefixes).
- Do **not** "fix" the known Page 1 sidebar-toggle workaround in commits 1-3 — observe whether adding 2 more controls changes the symptom, but do not change the workaround pattern itself.

---

## Execution Order (recommended)

1. Confirm B-1 / B-2 / B-3 with user (or accept defaults).
2. Run pre-work validation block.
3. Commit 2 (1-line fix) — trivial, gets a quick win.
4. Commit 1 (Page 1 filters) — low risk, well-understood.
5. Commit 5 (harvest chart Rice-only) — depends on commit 1's chart-fn signature pattern.
6. Commit 3 (Page 2 filters) — same pattern as commit 1, but 5 chart functions.
7. Commit 4 (3 dynamic action cards) — highest complexity, last.
8. Commit 6 (docs) — final.
9. After all 6 commits: run §5.1-§5.6 smoke tests, then update `docs/implementation-plan.md` task status rows (§6.C.1.4 → ✅, §6.C.2.5b → ✅, §6.C.1.6 → ⚠ Requires manual verification).

---

## Session Metadata

- **Operating mode at handoff:** Build (transitioned from Plan mid-session)
- **Phase:** Phase 6 §6.PAGES (Phase C)
- **Working directory:** `\\wsl.localhost\Debian\home\tomioka\PROJECTS\food price dashboard`
- **Stack:** Python → DuckDB → dbt → statsforecast → Marimo → Static JSON → Vizro 0.1.53 → Hugging Face Spaces
- **Last committed state:** 4 Page 1 bugfix sessions documented in `HANDOFF-page1-bugs-*.md`; Page 2 implementation complete per `HANDOFF-page2-seasonal-patterns-implementation.md`; Pages 3-4 not yet built
- **Sensitive info:** None in this handoff. No API keys, tokens, or PII were encountered.
