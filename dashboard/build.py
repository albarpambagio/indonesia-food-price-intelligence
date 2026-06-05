"""Build script — export Marimo notebook to WASM HTML and copy static assets."""

import shutil
import subprocess
from pathlib import Path

DIST_DIR = Path(__file__).resolve().parent / "dist"
NOTEBOOK = Path(__file__).resolve().parent / "app.py"
DATA_SRC = Path(__file__).resolve().parent / "public" / "data"
ASSETS_SRC = Path(__file__).resolve().parent / "assets"


def build():
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["uv", "run", "marimo", "export", "html-wasm",
         str(NOTEBOOK), "-o", str(DIST_DIR / "index.html"),
         "--mode", "run", "-f"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Export failed:\n{result.stderr}")
        raise SystemExit(1)
    print("WASM export succeeded")

    data_dest = DIST_DIR / "data"
    if DATA_SRC.exists():
        shutil.copytree(DATA_SRC, data_dest, dirs_exist_ok=True)
        print(f"Copied data to {data_dest}")

    assets_dest = DIST_DIR / "assets"
    if ASSETS_SRC.exists():
        shutil.copytree(ASSETS_SRC, assets_dest, dirs_exist_ok=True)
        print(f"Copied assets to {assets_dest}")

    print(f"Build complete: {DIST_DIR}")


if __name__ == "__main__":
    build()
