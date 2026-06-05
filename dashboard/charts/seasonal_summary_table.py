"""Seasonal summary table — Page 2. Action windows across all drivers."""

import pandas as pd

from dashboard.data_access import compute_action_windows


def seasonal_summary_table(
    data_frame: pd.DataFrame,
    islamic_cal: pd.DataFrame,
    commodity_filter: str = "All",
) -> pd.DataFrame:
    all_windows = []
    for driver in ["Ramadan", "Harvest", "Year-End"]:
        windows = compute_action_windows(data_frame, driver, islamic_cal)
        if not windows.empty:
            windows["driver"] = driver
            all_windows.append(windows)

    if not all_windows:
        return pd.DataFrame(
            columns=["Driver", "Commodity", "Spike %", "Consistency", "Lead Time", "Data Scope"]
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

    return result
