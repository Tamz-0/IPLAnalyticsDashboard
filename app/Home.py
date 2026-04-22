import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    layout="wide",
    page_title="IPL Analytics Dashboard",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# LOAD
# ----------------------------------------------------------
@st.cache_data
def load_data():
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return pd.read_csv(os.path.join(BASE_DIR, "../data/processed/season_stats.csv"))

df = load_data().sort_values("season", ascending=False)
def format_value(v):
    return f"{int(v):,}" if isinstance(v, (int, float)) else v



# ----------------------------------------------------------
# GLOBAL STYLES
# ----------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }

.stApp { background: #080810; }

header[data-testid="stHeader"] {
    background: transparent;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

section[data-testid="stSidebar"] {
    background: #0a0a18 !important;
    border-right: 1px solid #1e1e3a !important;
}

[data-testid="stSelectbox"] > div > div {
    background: #111128 !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 20px !important;
    color: #e8e8ff !important;
}

[data-testid="stPlotlyChart"] {
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    background: #0d0d20;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1e1e3a !important;
    border-radius: 12px !important;
}

hr { border-color: #1e1e3a !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 12px;">
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:32px;font-weight:800;color:#f59e0b;
                    letter-spacing:0.05em;">
            IPL
        </div>
        <div style="font-size:11px;color:#5a5a8a;letter-spacing:0.15em;
                    text-transform:uppercase;margin-top:2px;">
            Analytics Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#1e1e3a;margin:0 0 16px;">', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:10px;color:#5a5a8a;letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:8px;">
        Navigate
    </div>
    """, unsafe_allow_html=True)

    st.page_link("Home.py",                    label="Overview",        icon="🏠")
    st.page_link("pages/1_Overview.py",        label="Season Stats",    icon="📊")
    st.page_link("pages/2_Team_Analysis.py",   label="Team Analysis",   icon="🏏")
    st.page_link("pages/3_Player_Analysis.py", label="Player Analysis", icon="👤")
    st.page_link("pages/4_Head_to_Head.py",    label="Head to Head",    icon="⚔️")
    st.page_link("pages/5_Venue_Stats.py",     label="Venue Stats",     icon="🏟️")
    st.page_link("pages/6_player_h2h.py",      label="Player H2H",      icon="🎯")

    st.markdown("""
    <div style="position:relative;bottom:20px;left:0;width:240px;
                text-align:center;font-size:10px;color:#2a2a4a;
                letter-spacing:0.05em;">
        Data: 2008–2025 | Kaggle
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------
def apply_chart_theme(fig):
    fig.update_layout(
        plot_bgcolor="#0d0d20",
        paper_bgcolor="#0d0d20",
        font=dict(color="#94a3b8", family="Barlow"),
        title_font=dict(color="#e8e8ff", size=15, family="Barlow Condensed"),
        xaxis=dict(gridcolor="#1a1a30", showgrid=True),
        yaxis=dict(gridcolor="#1a1a30", showgrid=True),
        margin=dict(l=16, r=16, t=44, b=16),
    )
    return fig

def section_header(title, color="#7c3aed"):
    st.markdown(f"""
    <div style="font-family:'Barlow Condensed',sans-serif;
                font-size:18px;font-weight:700;
                letter-spacing:0.06em;text-transform:uppercase;
                color:#e8e8ff;margin:28px 0 16px;
                padding-left:10px;border-left:3px solid {color};">
        {title}
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# HEADER BAR
# ----------------------------------------------------------
col_title, col_season = st.columns([8, 2])

with col_title:
    st.markdown("""
    <div style="font-family:'Barlow Condensed',sans-serif;
                font-size:34px;font-weight:800;
                color:#e8e8ff;letter-spacing:0.04em;
                padding-top:8px;">
        IPL ANALYTICS DASHBOARD
    </div>
    <div style="font-size:11px;color:#5a5a8a;
                letter-spacing:0.12em;text-transform:uppercase;
                margin-top:2px;">
        Season Overview
    </div>
    """, unsafe_allow_html=True)

with col_season:
    seasons = sorted(df["season"].unique(), reverse=True)

    default_index = seasons.index(2025) if 2025 in seasons else 0

    selected = st.selectbox(
        "",
        seasons,
        index=default_index,
        key="home_season"
    )

season = df[df["season"] == selected].iloc[0]

# ----------------------------------------------------------
# CHAMPION BANNER
# ----------------------------------------------------------
champion = str(season["title_winner"]).upper() if pd.notna(season["title_winner"]) else "UNKNOWN"

st.markdown(f"""
<div style="width:100%;background:#16213e;
            border-left:4px solid #f59e0b;
            border-radius:12px;
            padding:28px 36px;
            margin:20px 0 28px;
            display:flex;align-items:center;gap:20px;">
    <div style="font-size:36px;line-height:1;">&#x1F3C6;</div>
    <div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:36px;font-weight:800;
                    color:#f59e0b;letter-spacing:0.04em;
                    line-height:1.1;">
            {champion}
        </div>
        <div style="font-size:12px;color:#5a5a8a;
                    letter-spacing:0.12em;text-transform:uppercase;
                    margin-top:4px;">
            IPL {selected} Champions
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# METRIC CARDS — 5 in a row
# ----------------------------------------------------------
total_fours = int(season.get("total_fours", 0)) if "total_fours" in season else "N/A"

metrics = [
    ("Total Matches",    int(season["total_matches"]),  "#7c3aed"),
    ("Total Runs",       int(season["total_runs"]),     "#3b82f6"),
    ("Total Sixes",       int(season["total_sixes"]),     "#f59e0b"),
    ("Highest Score",    int(season["highest_score"]),  "#10b981"),
    ("Total Fours",      total_fours,                   "#ef4444"),
]

cols = st.columns(5)
for col, (label, value, accent) in zip(cols, metrics):
    value_display = format_value(value)
    col.markdown(f"""
    <div style="background:#1a1a2e;
                border:1px solid #1e1e3a;
                border-top:3px solid {accent};
                border-radius:12px;
                padding:18px 20px;">
        <div style="font-size:11px;text-transform:uppercase;
                    letter-spacing:0.1em;color:#94a3b8;
                    margin-bottom:6px;">
            {label}
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:30px;font-weight:800;color:#f1f5f9;
                    line-height:1;">
            {value_display}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# CHARTS
# ----------------------------------------------------------
section_header("Season Trends")

df_sorted = df.sort_values("season")

left, right = st.columns([3, 2])

# Runs per season — bar + trend line
fig_runs = go.Figure()
fig_runs.add_bar(
    x=df_sorted["season"],
    y=df_sorted["total_runs"],
    marker_color="#7c3aed",
    name="Runs",
    hovertemplate="%{x}: %{y:,}<extra></extra>"
)
fig_runs.add_scatter(
    x=df_sorted["season"],
    y=df_sorted["total_runs"],
    mode="lines",
    line=dict(color="#3b82f6", width=3),
    name="Trend",
    hoverinfo="skip"
)
fig_runs.update_layout(
    title="Runs Scored Per Season",
    showlegend=False,
    xaxis_title="Season",
    yaxis_title="Total Runs"
)
apply_chart_theme(fig_runs)
left.plotly_chart(fig_runs, use_container_width=True)

# Sixes per season
fig_sixes = px.bar(
    df_sorted, x="season", y="total_sixes",
    color_discrete_sequence=["#f59e0b"],
    title="Sixes Per Season",
    labels={"season": "Season", "total_sixes": "Sixes"}
)
fig_sixes.update_traces(hovertemplate="%{x}: %{y}<extra></extra>")
apply_chart_theme(fig_sixes)
right.plotly_chart(fig_sixes, use_container_width=True)

# ----------------------------------------------------------
# ALL SEASONS TABLE
# ----------------------------------------------------------
section_header("All Seasons", color="#f59e0b")

display_df = df[[
    "season", "title_winner", "total_matches", "total_runs", "highest_score"
]].rename(columns={
    "season":        "Season",
    "title_winner":  "Champion",
    "total_matches": "Matches",
    "total_runs":    "Runs",
    "highest_score": "Highest"
})

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Champion": st.column_config.TextColumn(
            "Champion",
            help="IPL Season Winner",
            width="medium",
        ),
        "Runs": st.column_config.NumberColumn(
            "Runs",
            format="%d",
        ),
        "Season": st.column_config.NumberColumn(
            "Season",
            format="%d",
        ),
    }
)
