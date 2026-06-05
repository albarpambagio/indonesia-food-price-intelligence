# WSL

rm -rf .venv

uv sync   # creates venv at $HOME/.cache/uv/venv-wsl-food-price

uv run python dashboard/[app.py](http://app.py)   # instant

# PowerShell (after setting var, restart terminal)

rm .venv -Recurse -Force

uv sync   # creates venv at $HOMEcache\uv\venv-win-food-price

uv run python dashboard/[app.py](http://app.py)   # instant