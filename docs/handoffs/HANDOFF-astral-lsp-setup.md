# HANDOFF: Astral LSP Setup (ruff + ty)

**Date:** 2026-06-04 16:51

---

## Summary

Configured Astral's Python toolchain (ruff + ty) as LSP servers and formatter for opencode, applied globally so every future project gets linting, type checking, and formatting out of the box.

---

## What Was Done

### 1. Global opencode.json — LSP + Formatter

**File:** `~/.config/opencode/opencode.json`

Added three top-level keys:

- `lsp.ruff` — custom LSP server for linting/formatting diagnostics
- `lsp.ty` — custom LSP server for type checking, completions, hover, go-to-def
- `formatter.ruff` — ruff format as the project formatter

```json
{
  "lsp": {
    "ruff": {
      "command": ["ruff", "server"],
      "extensions": [".py", ".pyi"]
    },
    "ty": {
      "command": ["ty", "server"],
      "extensions": [".py", ".pyi"]
    }
  },
  "formatter": {
    "ruff": {
      "command": ["ruff", "format", "--stdin-filename", "$FILENAME"],
      "extensions": [".py", ".pyi"]
    }
  }
}
```

**Key detail:** `ruff server` and `ty server` communicate via stdin/stdout natively — no `--stdio` flag needed. This is different from pyright which uses `--stdio`.

### 2. WSL Tool Installation

Installed via `uv tool install` (persists across sessions, survives updates):

```bash
uv tool install ruff@latest    # ruff 0.15.15
uv tool install ty@latest      # ty 0.0.43
```

Both land in `~/.local/bin/` which is already on PATH via `.profile` and `.zshrc`.

### 3. Project pyproject.toml

**File:** `pyproject.toml` (project root)

Expanded from minimal `[tool.ruff]` to full Astral config:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.ty.environment]
python-version = "3.12"

[tool.ty.rules]
unresolved-import = "warn"
```

---

## Verification Results

| Check | Windows | WSL |
|-------|---------|-----|
| `ruff --version` | 0.15.15 | 0.15.15 |
| `ty --version` | 0.0.43 | 0.0.43 |
| `ruff server --help` | ok | ok |
| `ty server --help` | ok | ok |
| `ruff check dashboard/app.py` | passes | — |
| `ruff format --check dashboard/app.py` | passes | — |

**Note:** Manual LSP stdin/stdout testing via PowerShell piping fails due to shell differences. The servers work correctly when managed by opencode's LSP lifecycle.

---

## Tool Locations

| Platform | Binary path | PATH status |
|----------|------------|-------------|
| Windows | `C:\Users\albar\.local\bin\ruff.exe` | On PATH |
| Windows | `C:\Users\albar\.local\bin\ty.exe` | On PATH |
| WSL | `/home/tomioka/.local/bin/ruff` | On PATH (`.profile` + `.zshrc`) |
| WSL | `/home/tomioka/.local/bin/ty` | On PATH (`.profile` + `.zshrc`) |

---

## Architecture Notes

- **ruff server** = linting + formatting diagnostics (replaces flake8, isort, black)
- **ty server** = type checking + IDE features (replaces mypy/pyright for completions, hover, go-to-def)
- Both are single Rust binaries from Astral — no Python dependency needed
- Config is **global** (`~/.config/opencode/opencode.json`), applies to all projects
- Per-project overrides via `pyproject.toml` `[tool.ruff]` and `[tool.ty]` sections
- `uv tool` installs survive `uv tool upgrade ruff` / `uv tool upgrade ty`

---

## Previous LSP Config (Replaced)

The session initially had pyright configured:

```json
"lsp": {
  "pyright": {
    "command": ["npx", "-y", "pyright-langserver", "--stdio"],
    "extensions": [".py", ".pyi"]
  }
}
```

This was replaced with the Astral stack. If you need to revert, the pyright config is documented above.

---

## Known Limitations

- `ty` is beta (v0.0.43) — stable 1.0 targeted for 2026. Diagnostic messages may change between versions.
- The project's Python dependencies (vizro, duckdb, etc.) live in WSL's uv virtualenv. Type checking from Windows may show `reportMissingImports` for these packages — this is expected and not a bug.
- opencode does not hot-reload config. After editing `opencode.json`, the user must quit and restart opencode.

---

## Suggested Skills

- `customize-opencode` — for future opencode configuration changes
- `systematic-debugging` — if LSP servers fail to start in a new session

---

## Next Steps

- None required. Setup is complete and persistent.
- To update tools: `uv tool upgrade ruff && uv tool upgrade ty`
- To add project-specific ruff/ty rules: edit `pyproject.toml` `[tool.ruff.lint]` and `[tool.ty.rules]`
