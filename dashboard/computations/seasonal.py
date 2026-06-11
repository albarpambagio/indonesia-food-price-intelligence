import numpy as np
import pandas as pd


def compute_price_index(df: pd.DataFrame) -> pd.DataFrame:
    """Add price_index column (100 = annual avg) to monthly price DataFrame."""
    df = df.copy()
    df["year"] = df["month"].dt.year
    df["month_of_year"] = df["month"].dt.month
    annual_avg = (
        df.groupby(["year", "commodity_consolidated"])["avg_price_idr"]
        .mean()
        .reset_index()
        .rename(columns={"avg_price_idr": "ann_avg"})
    )
    df = df.merge(annual_avg, on=["year", "commodity_consolidated"], how="left")
    df["price_index"] = (df["avg_price_idr"] / df["ann_avg"]) * 100
    return df


def compute_seasonal_data(
    df: pd.DataFrame, cal: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Derive heatmap, Ramadan overlay, action windows, summary from price data."""
    df = compute_price_index(df)

    # Heatmap: mean premium % vs annual avg by commodity × month
    monthly_avg = (
        df.groupby(["commodity_consolidated", "month_of_year"])["avg_price_idr"]
        .mean()
        .reset_index()
    )
    overall_avg = (
        df.groupby("commodity_consolidated")["avg_price_idr"]
        .mean()
        .reset_index()
        .rename(columns={"avg_price_idr": "overall_avg"})
    )
    monthly_avg = monthly_avg.merge(overall_avg, on="commodity_consolidated", how="left")
    monthly_avg["premium_pct"] = (
        (monthly_avg["avg_price_idr"] / monthly_avg["overall_avg"]) - 1
    ) * 100
    heatmap_df = monthly_avg[["commodity_consolidated", "month_of_year", "premium_pct"]]

    # Ramadan overlay: month_relative T-2 to T+1
    cal = cal[["year", "eid_date"]].copy()
    cal["eid_month_num"] = cal["eid_date"].dt.month
    cal["eid_year"] = cal["eid_date"].dt.year
    ramadan_rows = []
    for _, row in cal.iterrows():
        eid_ym = row["eid_year"] * 12 + row["eid_month_num"]
        for comm in df["commodity_consolidated"].unique():
            for mr in [-2, -1, 0, 1]:
                target_ym = eid_ym + mr
                target_year = target_ym // 12
                target_month = target_ym % 12
                if target_month == 0:
                    target_month = 12
                    target_year -= 1
                match = df[
                    (df["commodity_consolidated"] == comm)
                    & (df["year"] == target_year)
                    & (df["month_of_year"] == target_month)
                ]
                if not match.empty:
                    ramadan_rows.append(
                        {
                            "commodity": comm,
                            "year": row["year"],
                            "month_relative": mr,
                            "price_index": match["price_index"].mean(),
                        }
                    )
    ramadan_df = pd.DataFrame(ramadan_rows)

    # Action windows
    driver_months = {
        "Ramadan / Lebaran": None,
        "Harvest Season": [3, 4, 8, 9],
        "Year-End": [11, 12],
    }
    action_rows = []
    for driver_name, months in driver_months.items():
        for comm in df["commodity_consolidated"].unique():
            comm_df = df[df["commodity_consolidated"] == comm]
            if driver_name == "Ramadan / Lebaran":
                comm_ram = ramadan_df[ramadan_df["commodity"] == comm]
                if comm_ram.empty:
                    continue
                yearly_spikes_ram = []
                for yr in comm_ram["year"].unique():
                    yr_data = comm_ram[comm_ram["year"] == yr]
                    driver_idx = yr_data[yr_data["month_relative"].isin([0, 1])][
                        "price_index"
                    ].mean()
                    non_driver_idx = yr_data[yr_data["month_relative"].isin([-2, -1])][
                        "price_index"
                    ].mean()
                    if pd.notna(driver_idx) and pd.notna(non_driver_idx) and non_driver_idx > 0:
                        yearly_spikes_ram.append((driver_idx / non_driver_idx - 1) * 100)
                if not yearly_spikes_ram:
                    continue
                avg_spike = np.mean(yearly_spikes_ram)
                above = sum(1 for s in yearly_spikes_ram if s > 0)
                action_rows.append(
                    {
                        "driver": driver_name,
                        "commodity": comm,
                        "spike_pct": round(avg_spike, 1),
                        "consistency": above,
                        "total_years": len(yearly_spikes_ram),
                        "lead_months": "2 months before Eid",
                    }
                )
            else:
                driver_data = comm_df[comm_df["month_of_year"].isin(months)]
                non_driver_data = comm_df[~comm_df["month_of_year"].isin(months)]
                if driver_data.empty or non_driver_data.empty:
                    continue
                driver_avg = driver_data.groupby("year")["price_index"].mean()
                non_driver_avg = non_driver_data.groupby("year")["price_index"].mean()
                yearly_spikes_hv = []
                for yr in driver_avg.index:
                    if yr in non_driver_avg.index:
                        d_val = driver_avg[yr]
                        nd_val = non_driver_avg[yr]
                        if pd.notna(d_val) and pd.notna(nd_val) and nd_val > 0:
                            yearly_spikes_hv.append((d_val / nd_val - 1) * 100)
                if not yearly_spikes_hv:
                    continue
                avg_spike = np.mean(yearly_spikes_hv)
                above = sum(1 for s in yearly_spikes_hv if s > 0)
                lead = (
                    "Mar\u2013Apr / Aug\u2013Sep"
                    if driver_name == "Harvest Season"
                    else "Nov\u2013Dec"
                )
                action_rows.append(
                    {
                        "driver": driver_name,
                        "commodity": comm,
                        "spike_pct": round(avg_spike, 1),
                        "consistency": above,
                        "total_years": len(yearly_spikes_hv),
                        "lead_months": lead,
                    }
                )
    action_windows_df = pd.DataFrame(action_rows)

    summary_df = action_windows_df.copy()
    summary_df["data_scope"] = "national"

    return heatmap_df, ramadan_df, action_windows_df, summary_df
