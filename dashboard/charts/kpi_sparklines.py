import plotly.graph_objects as go


def sparkline_chart(series, height=48):
    fig = go.Figure()
    vals = series.values
    fig.add_trace(
        go.Scatter(
            y=vals,
            mode="lines",
            line=dict(width=1.5),
            showlegend=False,
            hovertemplate="%{y:,.0f}<extra></extra>",
        )
    )
    if len(vals) >= 2:
        _min_idx = int(vals.argmin())
        _max_idx = int(vals.argmax())
        _min_val = vals[_min_idx]
        _max_val = vals[_max_idx]
        fig.add_annotation(
            x=_min_idx,
            y=_min_val,
            text=f"{_min_val:,.0f}",
            showarrow=False,
            font=dict(size=9, color="#888"),
            yshift=-12,
        )
        fig.add_annotation(
            x=_max_idx,
            y=_max_val,
            text=f"{_max_val:,.0f}",
            showarrow=False,
            font=dict(size=9, color="#888"),
            yshift=10,
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
