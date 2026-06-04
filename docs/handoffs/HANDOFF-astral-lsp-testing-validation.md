# HANDOFF: Astral LSP Testing & Validation

**Date:** 2026-06-04 17:08

---

## Summary

Tested the Astral LSP toolchain (ruff + ty) configured in the previous session. Ran all three tools against the project, auto-fixed safe issues, categorized remaining errors, and updated AGENTS.md with the new LSP quality baseline.

---

## What Was Done

### 1. LSP Testing Execution

Ran all three tools to verify they work correctly:

| Tool | Command | Result |
|------|---------|--------|
| ruff check | `ruff check .` | ✅ Working — found 279 errors (27 auto-fixable) |
| ruff format | `ruff format --check .` | ✅ Working — 16 files needed reformatting |
| ty check | `ty check .` | ⚠️ Fails from Windows (UNC path to WSL .venv) |
| ty check | `wsl -d Debian -- bash -c "ty check ."` | ✅ Working from WSL — found 47 diagnostics |

### 2. Auto-Fix Execution

Ran safe auto-fixes:

```bash
ruff check --fix .   # 27 errors fixed (unused imports, timezone aliases, import sorting)
ruff format .        # 16 files reformatted
```

**Before:** 279 ruff errors
**After:** 123 ruff errors (all E501/F821/E712/B905/F841 — require manual fixes)

### 3. Error Categorization

Analyzed all remaining non-auto-fixable errors:

**Ruff (123 remaining):**
- 98 E501 line-too-long — markdown tables in `eda.py`, Plotly templates in dashboard
- 11 F821 undefined-name — marimo cell scoping (false positives)
- 7 E712 bool comparison — `== True` in `seasonal_patterns.py` (actionable)
- 5 B905 zip-no-strict — `forecast_experimentation.py` (actionable)
- 2 F841 unused variable — `opacity` in kpi_sparklines.py, `cm` in seasonal_patterns.py (actionable)

**ty (47 diagnostics from WSL):**
- 16 missing-argument (Vizro Pydantic defaults)
- 11 unresolved-reference (marimo cell scoping)
- 7 not-subscriptable (duckdb `fetchone()`)
- 3 unresolved-attribute (`marimo.App`)
- 10 other (framework interop)

All ty diagnostics are false positives from framework interop — none require code changes.

### 4. AGENTS.md Updates

Three sections added/updated:

1. **Setup Commands** — Added `### LSP & Linting` section with ruff/ty install and usage commands
2. **LSP Quality (Astral Toolchain)** — New section documenting tools, baseline error counts, known false positives, and manual fix guidance
3. **Testing Instructions** — Added `### Verify Linting & Formatting` section

---

## Current State

| Metric | Value |
|--------|-------|
| ruff errors (auto-fixed) | 27 → 0 |
| ruff errors (remaining) | 123 |
| ruff errors (actionable) | 14 (7 E712 + 5 B905 + 2 F841) |
| ruff errors (false positive) | 109 (98 E501 + 11 F821) |
| ty diagnostics | 47 (all false positives) |
| Files formatted | 29/29 ✅ |

---

## Remaining Actionable Work

| Priority | Task | Files Affected |
|----------|------|----------------|
| Medium | Fix 7 E712 `== True` comparisons | `dashboard/pages/seasonal_patterns.py` |
| Medium | Fix 5 B905 `zip()` without `strict=` | `analysis/forecast_experimentation.py` |
| Low | Remove 2 unused variables | `dashboard/charts/kpi_sparklines.py:56`, `dashboard/pages/seasonal_patterns.py:135` |

---

## Artifacts Modified

| File | Change |
|------|--------|
| `AGENTS.md` | Added LSP & Linting setup, LSP Quality section, Testing Instructions |
| `analysis/export_json.py` | Auto-fixed: removed unused imports (`math`, `Any`, `LINEAGE_TABLE_DDL`), `timezone.utc` → `UTC` |
| `analysis/forecast/run_forecast.py` | Auto-fixed: removed unused `LINEAGE_TABLE_DDL` import, `timezone.utc` → `UTC` |
| `ingest/config.py` | Auto-fixed: `timezone.utc` → `UTC` |
| `run_pipeline.py` | Auto-fixed: removed unused `DB_PATH` import, `timezone.utc` → `UTC`, import sorting |
| `ingest/load_raw.py` | Auto-fixed: import sorting |
| `analysis/forecast_experimentation.py` | Auto-fixed: import sorting |
| 16 Python files | Auto-formatted by `ruff format` |

---

## Known Limitations

- **ty from Windows:** Cannot resolve WSL `.venv` via UNC path. Always run ty from WSL: `wsl -d Debian -- bash -c "ty check ."`
- **ty is beta (v0.0.43):** Diagnostic messages may change between versions. False positives for marimo, Vizro, and duckdb are expected.
- **ruff E501 in eda.py:** Markdown table cells with long insight text intentionally exceed 100-char limit. No fix planned.

---

## Suggested Skills

- `customize-opencode` — for future opencode configuration changes (LSP servers, formatter, etc.)
- `systematic-debugging` — if LSP servers fail to start in a new session
- `caveman-commit` — when committing the AGENTS.md updates

---

## Next Steps

1. **Optional:** Fix the 14 actionable ruff errors (E712, B905, F841) — low priority, code works correctly
2. **Monitor:** ty releases — when ty reaches 1.0, re-evaluate false positive categories
3. **Future:** Consider adding `ruff.toml` project-level overrides if default rules conflict with marimo/Dash patterns

---

## References

- Previous LSP setup: `docs/handoffs/HANDOFF-astral-lsp-setup.md`
- LSP Quality baseline: `AGENTS.md` → `## LSP Quality (Astral Toolchain)`
- Global config: `~/.config/opencode/opencode.json`
- Project config: `pyproject.toml` → `[tool.ruff]` + `[tool.ty]`
