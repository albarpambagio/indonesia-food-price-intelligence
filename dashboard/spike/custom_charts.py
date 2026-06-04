import pandas as pd
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def lag_heatmap(data_frame: pd.DataFrame):
    pivot = data_frame.pivot(index="commodity_pair", columns="lag_months", values="pearson_r")
    fig = px.imshow(
        pivot,
        text_auto=".3f",
        color_continuous_scale="RdBu_r",
        title="Lagged Correlation — All Pairs (Lags 0–3)",
        template="plotly_white",
        aspect="auto",
        zmin=0.5,
        zmax=1,
    )
    fig.update_layout(xaxis_title="Lag (months)", yaxis_title="Commodity Pair")
    return fig
