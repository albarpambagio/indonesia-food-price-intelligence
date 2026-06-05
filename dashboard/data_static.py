"""Static JSON data loader for Marimo dashboard.

Reads JSON files from public/data/ via filesystem.
"""

import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "public" / "data"


def load_json(name: str, key: str | None = None) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return pd.DataFrame()
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if key is not None and isinstance(raw, dict):
        raw = raw.get(key, {})
    if isinstance(raw, list):
        return pd.DataFrame(raw)
    if isinstance(raw, dict):
        return pd.DataFrame([raw])
    return pd.DataFrame()
