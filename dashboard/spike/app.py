"""Minimal Vizro spike — 1 page, 1 custom chart, real DuckDB data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import vizro.models as vm
from vizro import Vizro

import dashboard.data_manager  # noqa: F401 — registers all data sources
from dashboard.spike.custom_charts import lag_heatmap

page = vm.Page(
    title="Spike — Lag Heatmap",
    components=[
        vm.Graph(figure=lag_heatmap(data_frame="mart_correlation_summary")),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run(port=7860, debug=True)
