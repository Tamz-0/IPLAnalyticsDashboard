import plotly.graph_objects as go


def apply_theme(fig):
    fig.update_layout(
        plot_bgcolor="#16213e",
        paper_bgcolor="#16213e",
        font=dict(color="#94a3b8"),
        title_font=dict(color="#f1f5f9", size=16),
        xaxis=dict(
            gridcolor="#1e293b",
            linecolor="#1e293b",
            tickcolor="#475569"
        ),
        yaxis=dict(
            gridcolor="#1e293b",
            linecolor="#1e293b",
            tickcolor="#475569"
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(
            bgcolor="#1a1a2e",
            bordercolor="#7c3aed",
            font=dict(color="#f1f5f9")
        ),
        legend=dict(
            bgcolor="#1a1a2e",
            bordercolor="#1e293b",
            borderwidth=1,
            font=dict(color="#94a3b8")
        )
    )
    return fig