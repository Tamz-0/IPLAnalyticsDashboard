import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.charts import apply_chart_theme
from utils.components import (
    champion_banner,
    leaderboard_card,
    page_header,
    section_header,
    sidebar_footer,
    sidebar_header,
    sidebar_label,
    spacer,
    stat_card,
)
from utils.theme import COLORS, get_team_color, inject_global_css

st.set_page_config(layout="wide", page_title="Season Stats | IPL Dashboard")
inject_global_css()


# ----------------------------------------------------------------
# DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   
    return (
        pd.read_csv(os.path.join(base, "data", "processed", "season_stats.csv")),
        pd.read_csv(os.path.join(base, "data", "processed", "player_batting.csv")),
        pd.read_csv(os.path.join(base, "data", "processed", "player_bowler.csv")),
        pd.read_csv(os.path.join(base, "data", "processed", "team_stats.csv")),
    )


season_df, bat_df, bowl_df, team_df = load_data()

for _df in [season_df, bat_df, bowl_df, team_df]:
    _df["season"] = _df["season"].astype(int)

team_df["wins"]    = team_df["wins"].astype(int)
team_df["matches"] = team_df["matches"].astype(int)

seasons = sorted(season_df["season"].unique(), reverse=True)


# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
start_year = int(season_df["season"].min())
end_year   = int(season_df["season"].max())
sidebar_header("Season Deep Dive")

sidebar_label("Select Season")
default_index = seasons.index(2025) if 2025 in seasons else 0
selected = st.sidebar.selectbox(
    "Select Season", seasons, index=default_index, label_visibility="collapsed"
)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
sidebar_footer(start_year, end_year)


# ----------------------------------------------------------------
# FILTER
# ----------------------------------------------------------------
season_row = season_df[season_df["season"] == selected].iloc[0]
bat        = bat_df[bat_df["season"] == selected]
bowl       = bowl_df[bowl_df["season"] == selected]
teams      = team_df[team_df["season"] == selected].copy()

winner       = str(season_row["title_winner"]) if pd.notna(season_row.get("title_winner")) else "Unknown"
winner_color = get_team_color(winner)


# ----------------------------------------------------------------
# PAGE HEADER + STAT STRIP
# ----------------------------------------------------------------
page_header(f"IPL {selected}", "Season Deep Dive", winner_color)

# ----------------------------------------------------------------
# CHAMPION BANNER
# ----------------------------------------------------------------
champion_banner(winner, selected, winner_color)


total_matches = int(season_row["total_matches"]) if "total_matches" in season_row.index else "N/A"
total_runs    = f"{int(season_row['total_runs']):,}" if "total_runs" in season_row.index else "N/A"
total_sixes   = int(season_row["total_sixes"]) if "total_sixes" in season_row.index else "N/A"
highest_score = int(season_row["highest_score"]) if "highest_score" in season_row.index else "N/A"

c1, c2, c3, c4 = st.columns(4)
stat_card(c1, "Total Matches", str(total_matches), accent=winner_color)
stat_card(c2, "Total Runs",    str(total_runs),    value_color=COLORS["blue"],  accent=winner_color)
stat_card(c3, "Total Sixes",   str(total_sixes),   value_color=COLORS["amber"], accent=winner_color)
stat_card(c4, "Highest Score", str(highest_score), value_color=COLORS["green"], accent=winner_color)

spacer(8)


# ----------------------------------------------------------------
# SECTION — TOP PERFORMERS
# ----------------------------------------------------------------
section_header("Top Performers", COLORS["amber"])

top_runs = bat.groupby("batter")["runs_batter"].sum().sort_values(ascending=False).head(5)
top_wkts = bowl.groupby("bowler")["bowler_wicket"].sum().sort_values(ascending=False).head(5)

lc, rc = st.columns(2)
with lc:
    st.components.v1.html(
        leaderboard_card("Top Run Scorers",   top_runs, "runs", COLORS["accent"]),
        height=300, scrolling=False,
    )
with rc:
    st.components.v1.html(
        leaderboard_card("Top Wicket Takers", top_wkts, "wkts", COLORS["amber"]),
        height=300, scrolling=False,
    )

spacer(8)


# ----------------------------------------------------------------
# SECTION — TEAM STANDINGS
# ----------------------------------------------------------------
section_header("Team Standings", COLORS["accent"])

teams["win_pct"]    = (teams["wins"] / teams["matches"] * 100).round(1)
teams_sorted        = teams.sort_values("wins", ascending=False)
team_colors_list    = [get_team_color(t) for t in teams_sorted["team"]]

fig_teams = go.Figure(go.Bar(
    x=teams_sorted["team"].tolist(),
    y=teams_sorted["wins"].tolist(),
    marker_color=team_colors_list,
    marker_line_width=0,
    customdata=teams_sorted[["win_pct", "matches"]].values,
    hovertemplate=(
        "<b>%{x}</b><br>Wins: %{y}<br>"
        "Win%%: %{customdata[0]:.1f}%%<br>"
        "Matches: %{customdata[1]}<extra></extra>"
    ),
))
fig_teams.update_layout(
    title="Wins per Team",
    xaxis=dict(tickangle=-30),
)
apply_chart_theme(fig_teams, height=380)
st.plotly_chart(fig_teams, use_container_width=True, key="team_standings")


# ----------------------------------------------------------------
# SECTION — SEASON INSIGHTS
# ----------------------------------------------------------------
section_header("Season Insights", COLORS["green"])

ci1, ci2, ci3 = st.columns(3)

if "nrr" in teams.columns:
    nrr_sorted = teams.sort_values("nrr", ascending=False)
    nrr_colors = [COLORS["green"] if v >= 0 else COLORS["red"] for v in nrr_sorted["nrr"]]
    fig_nrr = go.Figure(go.Bar(
        x=nrr_sorted["team"].tolist(),
        y=nrr_sorted["nrr"].round(3).tolist(),
        marker_color=nrr_colors,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>NRR: %{y:.3f}<extra></extra>",
    ))
    fig_nrr.update_layout(title="Net Run Rate", xaxis=dict(tickangle=-30))
    apply_chart_theme(fig_nrr, height=320)
    ci1.plotly_chart(fig_nrr, use_container_width=True, key="nrr_chart")
else:
    ci1.info("NRR data unavailable")

if "bat" in teams.columns and "field" in teams.columns:
    bat_total   = int(teams["bat"].sum())
    field_total = int(teams["field"].sum())
    fig_toss = go.Figure(go.Pie(
        values=[bat_total, field_total],
        labels=["Bat First", "Field First"],
        hole=0.55,
        marker=dict(colors=[COLORS["blue"], COLORS["amber"]],
                    line=dict(color=COLORS["bg_base"], width=3)),
        textinfo="label+percent",
        textfont=dict(size=12, color=COLORS["text_primary"]),
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig_toss.update_layout(title="Toss Decisions", showlegend=False)
    apply_chart_theme(fig_toss, height=320)
    ci2.plotly_chart(fig_toss, use_container_width=True, key="toss_pie")
else:
    ci2.info("Toss data unavailable")

if "runs_scored" in teams.columns:
    runs_sorted = teams.sort_values("runs_scored", ascending=False)
    fig_runs = go.Figure(go.Bar(
        x=runs_sorted["team"].tolist(),
        y=runs_sorted["runs_scored"].tolist(),
        marker_color=[get_team_color(t) for t in runs_sorted["team"]],
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Runs: %{y:,}<extra></extra>",
    ))
    fig_runs.update_layout(title="Runs Scored per Team", xaxis=dict(tickangle=-30))
    apply_chart_theme(fig_runs, height=320)
    ci3.plotly_chart(fig_runs, use_container_width=True, key="runs_chart")
else:
    ci3.info("Runs data unavailable")


# ----------------------------------------------------------------
# SECTION — FULL TEAM STATS TABLE
# ----------------------------------------------------------------
section_header("Full Team Stats", COLORS["blue"])

display_cols = ["team", "matches", "wins", "losses", "win_pct"]
extra        = ["nrr", "runs_scored", "runs_conceded", "chasing_wins", "defending_wins"]
display_cols += [c for c in extra if c in teams.columns]

table = teams[display_cols].sort_values("wins", ascending=False).copy()
table = table.rename(columns={
    "team": "Team", "matches": "M", "wins": "W", "losses": "L",
    "win_pct": "Win%", "nrr": "NRR", "runs_scored": "Runs For",
    "runs_conceded": "Runs Against", "chasing_wins": "Chase W",
    "defending_wins": "Defend W",
})

if "Win%" in table.columns:
    table["Win%"] = table["Win%"].round(1)
if "NRR" in table.columns:
    table["NRR"]  = table["NRR"].round(3)

st.dataframe(table, use_container_width=True, hide_index=True)