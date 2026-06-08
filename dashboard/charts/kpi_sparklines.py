import plotly.graph_objects as go


def sparkline_chart(series, height=60):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=series.values,
            mode="lines",
            line=dict(width=1.5),
            showlegend=False,
        )
    )
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, showticklabels=False),
        yaxis=dict(visible=False, showticklabels=False),
    )
    return fig
