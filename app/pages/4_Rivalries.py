import os
import sys

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.charts import apply_chart_theme
from utils.components import (
    leaderboard_card,
    page_header,
    rivalry_banner,
    section_header,
    sidebar_footer,
    sidebar_header,
    sidebar_label,
    spacer,
    stat_card,
)
from utils.theme import COLORS, inject_global_css

st.set_page_config(layout="wide", page_title="Head to Head | IPL Dashboard")
inject_global_css()


# ----------------------------------------------------------------
# DATA
# ----------------------------------------------------------------
@st.cache_data
def load():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import pandas as pd
    m = pd.read_csv(os.path.join(base, "data", "processed", "h2h_matches.csv"))
    p = pd.read_csv(os.path.join(base, "data", "processed", "h2hplayer_stats.csv"))
    return m, p


matches, players = load()
teams = sorted(set(matches["team1"]).union(set(matches["team2"])))
start_year = int(matches["season"].min())
end_year   = int(matches["season"].max())


# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
sidebar_header("Head to Head")

sidebar_label("Team 1")
default_t1 = "Royal Challengers Bengaluru"
default_t2 = "Chennai Super Kings"

team1 = st.sidebar.selectbox(
    "Team 1", teams,
    index=teams.index(default_t1) if default_t1 in teams else 0,
    label_visibility="collapsed",
    key="h2h_t1",
)

sidebar_label("Team 2")
team2 = st.sidebar.selectbox(
    "Team 2", teams,
    index=teams.index(default_t2) if default_t2 in teams else 1,
    label_visibility="collapsed",
    key="h2h_t2",
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
sidebar_footer(start_year, end_year)

if team1 == team2:
    st.warning("Please select two different teams.")
    st.stop()


# ----------------------------------------------------------------
# PAGE HEADER
# ----------------------------------------------------------------
page_header(
    f"<span style='color:#9ca3af;'>IPL Analytics Dashboard <br>Head to Head Analysis<br></span>",
    f"<span style='font-size:24px; font-weight:900; letter-spacing:0.02em; color:#ffffff;'>{team1} vs {team2}</span>"
)

# ----------------------------------------------------------------
# FILTER + DEDUPLICATE
# ----------------------------------------------------------------
h2h = matches[
    ((matches["team1"] == team1) & (matches["team2"] == team2)) |
    ((matches["team1"] == team2) & (matches["team2"] == team1))
].copy()

if h2h.empty:
    st.warning("No matches found for this fixture.")
    st.stop()

h2h = h2h.drop_duplicates(subset="match_id")
h2h["teamA"] = h2h[["team1", "team2"]].min(axis=1)
h2h["teamB"] = h2h[["team1", "team2"]].max(axis=1)

teamA = min(team1, team2)
teamB = max(team1, team2)

h2h_pair = h2h[(h2h["teamA"] == teamA) & (h2h["teamB"] == teamB)]
total    = len(h2h_pair)
wins_A   = (h2h_pair["winner"] == teamA).sum()
wins_B   = (h2h_pair["winner"] == teamB).sum()

w1, w2 = (wins_A, wins_B) if team1 == teamA else (wins_B, wins_A)


# ----------------------------------------------------------------
# RIVALRY BANNER
# ----------------------------------------------------------------
rivalry_banner(team1, team2, w1, w2)


# ----------------------------------------------------------------
# STAT CARDS
# ----------------------------------------------------------------
c1, c2, c3 = st.columns(3)
stat_card(c1, "Total Matches",   str(total), accent=COLORS["accent"])
stat_card(c2, f"{team1} Wins",   str(w1),    value_color=COLORS["green"],  accent=COLORS["green"])
stat_card(c3, f"{team2} Wins",   str(w2),    value_color=COLORS["amber"],  accent=COLORS["amber"])

spacer(16)


# ----------------------------------------------------------------
# WIN COMPARISON CHART
# ----------------------------------------------------------------
section_header("Win Comparison", COLORS["accent"])

fig = go.Figure(go.Bar(
    x=[team1, team2],
    y=[w1, w2],
    text=[w1, w2],
    textposition="outside",
    marker_color=[COLORS["green"], COLORS["amber"]],
    marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>Wins: %{y}<extra></extra>",
))
fig.update_layout(title="Wins by Team", yaxis=dict(title="Wins"))
apply_chart_theme(fig)
st.plotly_chart(fig, use_container_width=True, key="h2h_bar")


# ----------------------------------------------------------------
# TOP PERFORMERS
# ----------------------------------------------------------------
section_header("Top Performers", COLORS["amber"])

bat_data = players[players["player_team"].isin([team1, team2])]
top_bat  = bat_data.groupby("player")["runs_batter"].sum().sort_values(ascending=False).head(5)

st.components.v1.html(
    leaderboard_card("Top Run Scorers", top_bat, "runs", COLORS["amber"]),
    height=300, scrolling=False,
)


# ----------------------------------------------------------------
# MATCH HISTORY
# ----------------------------------------------------------------
section_header("Match History", COLORS["blue"])

st.dataframe(
    h2h_pair.sort_values("season", ascending=False)[["season", "team1", "team2", "winner", "venue"]],
    use_container_width=True,
    hide_index=True,
)