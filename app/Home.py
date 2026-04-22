import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.charts import apply_chart_theme
from utils.components import (
    champion_banner,
    page_header,
    section_header,
    sidebar_footer,
    sidebar_header,
    sidebar_label,
    spacer,
    stat_card,
)
from utils.theme import COLORS, get_team_color, inject_global_css

st.set_page_config(
    layout="wide",
    page_title="IPL Analytics Dashboard",
    initial_sidebar_state="expanded",
)

inject_global_css()


# ----------------------------------------------------------------
# DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return pd.read_csv(os.path.join(base, "data", "processed", "season_stats.csv"))

df = load_data().sort_values("season", ascending=False)


# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
start_year = int(df["season"].min())
end_year   = int(df["season"].max())
with st.sidebar:
    sidebar_header("Season Overview")

    st.markdown(f"""
    <div style="font-size:10px;color:{COLORS['text_dim']};letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:8px;">
        Navigate
    </div>
        """, unsafe_allow_html=True)
    st.page_link("Home.py",                    label="Overview",        icon="🏠")
    st.page_link("pages/1_Season Overview.py",        label="Season Overview",    icon="📊")
    st.page_link("pages/2_Team Intelligence.py",   label="Team Intelligence",   icon="🏏")
    st.page_link("pages/3_Player Insights.py", label="Player Insights", icon="👤")
    st.page_link("pages/4_Rivalries.py",    label="Rivalries",    icon="⚔️")
    st.page_link("pages/5_Venue Intelligence.py",     label="Venue Intelligence",     icon="📍")
    st.page_link("pages/6_Player Matchups.py",      label="Player Matchups",      icon="🤝")

    sidebar_footer(start_year, end_year)


# ----------------------------------------------------------------
# SEASON SELECTOR
# ----------------------------------------------------------------
seasons = sorted(df["season"].unique(), reverse=True)
default_index = seasons.index(2025) if 2025 in seasons else 0

col_title, col_season = st.columns([8, 2])

with col_title:
    page_header("IPL Analytics Dashboard", "Season Overview")

with col_season:
    selected = st.selectbox("", seasons, index=default_index, key="home_season")

season = df[df["season"] == selected].iloc[0]
winner_color = get_team_color(str(season.get("title_winner", "")))


# ----------------------------------------------------------------
# CHAMPION BANNER
# ----------------------------------------------------------------
champion = str(season["title_winner"]).upper() if pd.notna(season.get("title_winner")) else "UNKNOWN"
champion_banner(champion, selected, winner_color)


# ----------------------------------------------------------------
# METRIC CARDS
# ----------------------------------------------------------------
total_fours = int(season["total_fours"]) if "total_fours" in season and pd.notna(season["total_fours"]) else "N/A"

metrics = [
    ("Total Matches", str(int(season["total_matches"])),               COLORS["text_primary"], COLORS["accent"]),
    ("Total Runs",    f"{int(season['total_runs']):,}",                COLORS["blue"],         COLORS["blue"]),
    ("Total Sixes",   str(int(season["total_sixes"])),                 COLORS["amber"],        COLORS["amber"]),
    ("Highest Score", str(int(season["highest_score"])),               COLORS["green"],        COLORS["green"]),
    ("Total Fours",   str(total_fours),                                COLORS["red"],          COLORS["red"]),
]

cols = st.columns(5)
for col, (label, value, vc, ac) in zip(cols, metrics):
    stat_card(col, label, value, vc, ac)

spacer(16)


# ----------------------------------------------------------------
# SECTION — SEASON TRENDS
# ----------------------------------------------------------------
section_header("Season Trends", COLORS["accent"])

df_sorted = df.sort_values("season")
left, right = st.columns([3, 2])

fig_runs = go.Figure()
fig_runs.add_bar(
    x=df_sorted["season"],
    y=df_sorted["total_runs"],
    marker_color=COLORS["accent"],
    name="Runs",
    hovertemplate="%{x}: %{y:,}<extra></extra>",
)
fig_runs.add_scatter(
    x=df_sorted["season"],
    y=df_sorted["total_runs"],
    mode="lines",
    line=dict(color=COLORS["blue"], width=3),
    name="Trend",
    hoverinfo="skip",
)
fig_runs.update_layout(title="Runs Scored Per Season", showlegend=False,
                       xaxis_title="Season", yaxis_title="Total Runs")
apply_chart_theme(fig_runs)
left.plotly_chart(fig_runs, use_container_width=True)

fig_sixes = px.bar(
    df_sorted, x="season", y="total_sixes",
    color_discrete_sequence=[COLORS["amber"]],
    title="Sixes Per Season",
    labels={"season": "Season", "total_sixes": "Sixes"},
)
fig_sixes.update_traces(hovertemplate="%{x}: %{y}<extra></extra>", marker_line_width=0)
apply_chart_theme(fig_sixes)
right.plotly_chart(fig_sixes, use_container_width=True)


# ----------------------------------------------------------------
# SECTION — ALL SEASONS TABLE
# ----------------------------------------------------------------
section_header("All Seasons", COLORS["amber"])

display_df = df[["season", "title_winner", "total_matches", "total_runs", "highest_score"]].rename(
    columns={
        "season":        "Season",
        "title_winner":  "Champion",
        "total_matches": "Matches",
        "total_runs":    "Runs",
        "highest_score": "Highest",
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Season":  st.column_config.NumberColumn("Season",  format="%d"),
        "Runs":    st.column_config.NumberColumn("Runs",    format="%d"),
        "Champion": st.column_config.TextColumn("Champion", width="medium"),
    },
)