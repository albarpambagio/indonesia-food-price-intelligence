"""Vizro dashboard entry point — Indonesia Food Price Intelligence.

Replaces Dash multi-page app with Vizro vm.Dashboard.
Gunicorn target: app:app (per LEARNINGS.md §91).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vizro.models as vm
from vizro import Vizro

import dashboard.data_manager  # noqa: F401 — registers all data sources
from dashboard.pages.price_trends import price_trends_page

dashboard = vm.Dashboard(
    pages=[price_trends_page],
)

app = Vizro().build(dashboard)

if __name__ == "__main__":
    app.run(port=7860, debug=True)
