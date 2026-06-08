import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / ".." / "dist"

if __name__ == "__main__":
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "marimo",
            "export",
            "html-wasm",
            str(PROJECT_ROOT / "app.py"),
            "-o",
            str(DIST_DIR / "index.html"),
            "--mode",
            "run",
            "-f",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)
    print("WASM build complete:", DIST_DIR / "index.html")
