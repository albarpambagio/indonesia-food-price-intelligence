"""Seasonal summary table — Page 2. Action windows across all drivers."""

import dash_ag_grid as dag
import pandas as pd
from vizro.models.types import capture

from dashboard.data_access import compute_action_windows, load_islamic_calendar


@capture("ag_grid")
def seasonal_summary_table(
    data_frame: pd.DataFrame,
    commodity_filter: str = "All",
) -> dag.AgGrid:
    islamic_cal = load_islamic_calendar()

    all_windows = []
    for driver in ["Ramadan", "Harvest", "Year-End"]:
        windows = compute_action_windows(data_frame, driver, islamic_cal)
        if not windows.empty:
            windows["driver"] = driver
            all_windows.append(windows)

    empty_cols = ["Driver", "Commodity", "Spike %", "Consistency", "Lead Time", "Data Scope"]
    if not all_windows:
        return dag.AgGrid(
            columnDefs=[{"field": c} for c in empty_cols],
            rowData=[],
            className="ag-theme-vizro",
            defaultColDef={"resizable": True, "sortable": True, "filter": True},
        )

    result = pd.concat(all_windows, ignore_index=True)
    result = result.rename(
        columns={
            "driver": "Driver",
            "commodity": "Commodity",
            "spike_pct": "Spike %",
            "consistency_score": "Consistency",
            "lead_months": "Lead Time",
            "data_scope": "Data Scope",
        }
    )

    if commodity_filter != "All":
        result = result[result["Commodity"] == commodity_filter]

    result = result.sort_values("Spike %", ascending=False).reset_index(drop=True)
    result = result[["Driver", "Commodity", "Spike %", "Consistency", "Lead Time", "Data Scope"]]

    return dag.AgGrid(
        columnDefs=[{"field": col} for col in result.columns],
        rowData=result.to_dict("records"),
        className="ag-theme-vizro",
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
        },
        dashGridOptions={
            "animateRows": False,
            "domLayout": "autoHeight",
            "pagination": True,
            "paginationPageSize": 20,
        },
        columnSize="responsiveSizeToFit",
    )
