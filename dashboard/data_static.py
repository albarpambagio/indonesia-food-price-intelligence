from pathlib import Path


def _get_data_dir() -> Path:
    local_path = Path(__file__).resolve().parent / "public" / "data"
    if local_path.exists():
        return local_path
    return Path("data")


DATA_DIR = _get_data_dir()


def load_json(filename: str) -> list[dict]:
    import json
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def load_json_envelope(filename: str, key: str = "data") -> list[dict]:
    import json
    raw = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
    return raw[key]


def load_csv(filename: str):
    import pandas as pd
    return pd.read_csv(DATA_DIR / filename)
