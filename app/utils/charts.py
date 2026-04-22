import plotly.graph_objects as go
from utils.theme import COLORS


def apply_chart_theme(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        plot_bgcolor=COLORS["bg_surface"],
        paper_bgcolor=COLORS["bg_surface"],
        font=dict(color=COLORS["text_muted"], family="Barlow, sans-serif"),
        title_font=dict(
            color=COLORS["text_primary"],
            size=14,
            family="Barlow Condensed, sans-serif",
        ),
        xaxis=dict(
            gridcolor=COLORS["border_grid"],
            linecolor=COLORS["border_grid"],
            tickcolor=COLORS["tick"],
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor=COLORS["border_grid"],
            linecolor=COLORS["border_grid"],
            tickcolor=COLORS["tick"],
            tickfont=dict(size=11),
        ),
        margin=dict(l=16, r=16, t=40, b=16),
        hoverlabel=dict(
            bgcolor=COLORS["bg_input"],
            bordercolor=COLORS["border_input"],
            font=dict(color=COLORS["text_primary"], size=13),
        ),
        legend=dict(
            bgcolor=COLORS["bg_input"],
            bordercolor=COLORS["border"],
            borderwidth=1,
            font=dict(color=COLORS["text_muted"], size=12),
        ),
        height=height,
    )
    return fig