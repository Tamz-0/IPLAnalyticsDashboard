import streamlit as st

# ----------------------------------------------------------------
# COLOR TOKENS
# ----------------------------------------------------------------
COLORS = {
    "bg_base":      "#080810",
    "bg_surface":   "#0d0d20",
    "bg_sidebar":   "#0a0a18",
    "bg_input":     "#111128",
    "border":       "#1e1e3a",
    "border_input": "#2a2a4a",
    "border_grid":  "#1a1a30",
    "text_primary": "#e8e8ff",
    "text_muted":   "#94a3b8",
    "text_dim":     "#5a5a8a",
    "text_faint":   "#3a3a6a",
    "accent":       "#7c3aed",
    "blue":         "#3b82f6",
    "amber":        "#f59e0b",
    "green":        "#22c55e",
    "red":          "#ef4444",
    "tick":         "#2a2a4a",
}

TEAM_COLORS = {
    "Chennai Super Kings":         "#f5c518",
    "Mumbai Indians":              "#004c93",
    "Royal Challengers Bengaluru": "#c8102e",
    "Kolkata Knight Riders":       "#6a0dad",
    "Sunrisers Hyderabad":         "#f26522",
    "Delhi Capitals":              "#0078bc",
    "Punjab Kings":                "#dd1f26",
    "Rajasthan Royals":            "#2d81c8",
    "Lucknow Super Giants":        "#00bcd4",
    "Gujarat Titans":              "#1d9e8f",
    "Rising Pune Supergiants":     "#7c3aed",
}


def get_team_color(team: str) -> str:
    return TEAM_COLORS.get(team, COLORS["accent"])


# ----------------------------------------------------------------
# GLOBAL CSS
# ----------------------------------------------------------------
_GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

.stApp {
    background: #080810;
}

header[data-testid="stHeader"] {
    background: transparent;
}
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: #0a0a18 !important;
    border-right: 1px solid #1e1e3a !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1rem !important;
}

[data-testid="stMetric"] {
    background: #0d0d20;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #5a5a8a !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #e8e8ff !important;
}

[data-testid="stSelectbox"] > div > div {
    background: #111128 !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
    color: #e8e8ff !important;
}

[data-testid="stMultiSelect"] > div {
    background: #111128 !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: #1e1e3a !important;
    border-radius: 4px !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
    color: #e8e8ff !important;
    font-size: 12px !important;
}

[data-testid="stPlotlyChart"] {
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1e1e3a !important;
    border-radius: 8px !important;
}

[data-testid="stExpander"] {
    background: #0d0d20 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 10px !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #0d0d20;
    border-bottom: 1px solid #1e1e3a;
    gap: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent;
    color: #5a5a8a;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 2px solid transparent;
    padding: 12px 20px;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #e8e8ff !important;
    border-bottom: 2px solid #7c3aed !important;
    background: transparent !important;
}

hr {
    border-color: #1e1e3a !important;
    margin: 1rem 0 !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 4px; }
"""


def inject_global_css() -> None:
    st.markdown(f"<style>{_GLOBAL_CSS}</style>", unsafe_allow_html=True)
    