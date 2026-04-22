import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.charts import apply_chart_theme
from utils.components import (
    page_header,
    section_header,
    sidebar_footer,
    sidebar_header,
    sidebar_label,
    spacer,
    stat_card,
)
from utils.theme import COLORS, inject_global_css

st.set_page_config(layout="wide", page_title="Player Analysis | IPL Dashboard")
inject_global_css()


# ----------------------------------------------------------------
# DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bat  = pd.read_csv(os.path.join(base, "data", "processed", "player_batting.csv"))
    bowl = pd.read_csv(os.path.join(base, "data", "processed", "player_bowler.csv"))
    return bat, bowl


bat_df, bowl_df = load_data()

all_batters  = sorted(bat_df["batter"].unique())
all_bowlers  = sorted(bowl_df["bowler"].unique())
all_rounders = sorted(set(bat_df["batter"].unique()) & set(bowl_df["bowler"].unique()))
start_year = int(min(bat_df["season"].min(), bowl_df["season"].min()))
end_year   = int(max(bat_df["season"].max(), bowl_df["season"].max()))


# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
sidebar_header("Player Intelligence")

sidebar_label("Role")
role = st.sidebar.radio("Role", ["Batter", "Bowler", "All-rounder"], label_visibility="collapsed")

player_list = {"Batter": all_batters, "Bowler": all_bowlers, "All-rounder": all_rounders}[role]

sidebar_label("Search Player")
search = st.sidebar.text_input(
    "Search Player", placeholder="e.g. Kohli, Rohit...", label_visibility="collapsed"
)

filtered = [p for p in player_list if search.lower() in p.lower()] if search else player_list

if not filtered:
    st.sidebar.warning("No players match your search.")
    st.stop()

sidebar_label("Select Player")
defaults = {"Batter": "V Kohli", "Bowler": "JJ Bumrah", "All-rounder": "V Kohli"}
default_player = defaults[role]
default_index  = filtered.index(default_player) if default_player in filtered else 0

player = st.sidebar.selectbox(
    "Select Player", filtered, index=default_index, label_visibility="collapsed"
)

sidebar_label("Season Range")
s_min = int(min(bat_df["season"].min(), bowl_df["season"].min()))
s_max = int(max(bat_df["season"].max(), bowl_df["season"].max()))
season_range = st.sidebar.slider(
    "Season Range", s_min, s_max, (s_min, s_max), label_visibility="collapsed"
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
career_view = st.sidebar.toggle("Career View", value=False)
st.sidebar.caption("Aggregates all seasons into career totals")
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
sidebar_footer(start_year, end_year)


# ----------------------------------------------------------------
# FILTER DATA
# ----------------------------------------------------------------
bat = bat_df[
    (bat_df["batter"] == player) &
    (bat_df["season"] >= season_range[0]) &
    (bat_df["season"] <= season_range[1])
].copy()

bowl = bowl_df[
    (bowl_df["bowler"] == player) &
    (bowl_df["season"] >= season_range[0]) &
    (bowl_df["season"] <= season_range[1])
].copy()

has_bat  = not bat.empty
has_bowl = not bowl.empty

if not has_bat and not has_bowl:
    st.warning("No data found for this player in the selected range.")
    st.stop()

if career_view:
    if has_bat:
        bat = pd.DataFrame([{
            "season":          "Career",
            "runs_batter":     bat["runs_batter"].sum(),
            "balls_faced":     bat["balls_faced"].sum(),
            "is_wicket":       bat["is_wicket"].sum(),
            "is_four":         bat["is_four"].sum(),
            "is_six":          bat["is_six"].sum(),
            "strike_rate":     bat["strike_rate"].mean(),
            "batting_average": bat["batting_average"].mean(),
        }])
    if has_bowl:
        bowl = pd.DataFrame([{
            "season":          "Career",
            "runs_bowler":     bowl["runs_bowler"].sum(),
            "bowler_wicket":   bowl["bowler_wicket"].sum(),
            "ball_no":         bowl["ball_no"].sum(),
            "overs":           bowl["overs"].sum(),
            "economy":         bowl["economy"].mean(),
            "bowling_average": bowl["bowling_average"].mean(),
            "strike_rate":     bowl["strike_rate"].mean(),
        }])
initials     = "".join([x[0] for x in player.split()[:2]]).upper()
accent_color = COLORS["accent"] if role != "Bowler" else COLORS["amber"]
season_label = (
    "Career View" if career_view
    else f"Seasons {season_range[0]}\u2013{season_range[1]}"
)
page_header(
    f"<span style='display:block; line-height:1;'>IPL Analytics Dashboard</span>"
    f"<span style='display:block; line-height:1.1; margin-top:2px; color:{accent_color};'>{player.upper()}</span>",
    f"{role} · {season_label}",
    accent_color,
)
# ----------------------------------------------------------------
# PROFILE CARD
# ----------------------------------------------------------------
initials     = "".join([x[0] for x in player.split()[:2]]).upper()
accent_color = COLORS["accent"] if role != "Bowler" else COLORS["amber"]
season_label = (
    "Career View" if career_view
    else f"Seasons {season_range[0]}\u2013{season_range[1]}"
)

st.markdown(f"""
<div style="background:{COLORS['bg_surface']};padding:24px 28px;
            border:1px solid {COLORS['border']};border-left:4px solid {accent_color};
            border-radius:12px;display:flex;align-items:center;
            gap:20px;margin-bottom:24px;">
    <div style="width:72px;height:72px;border-radius:50%;
                background:{accent_color}22;border:2px solid {accent_color};
                color:{accent_color};display:flex;align-items:center;
                justify-content:center;
                font-family:'Barlow Condensed',sans-serif;
                font-size:26px;font-weight:800;flex-shrink:0;">
        {initials}
    </div>
    <div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:32px;font-weight:800;color:{COLORS['text_primary']};
                    letter-spacing:0.04em;line-height:1.1;">
            {player}
        </div>
        <div style="font-size:12px;color:{COLORS['text_dim']};
                    text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">
            {role} &middot; {season_label}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------
# BATTING SECTION
# ----------------------------------------------------------------
if has_bat and role in ["Batter", "All-rounder"]:
    section_header("Batting Stats", COLORS["accent"])

    total_runs = int(bat["runs_batter"].sum())
    avg        = float(bat["batting_average"].mean())
    sr         = float(bat["strike_rate"].mean())
    fours      = int(bat["is_four"].sum())
    sixes      = int(bat["is_six"].sum())
    seasons_p  = bat["season"].nunique() if not career_view else "All"

    bat_stats = [
        ("Runs",    str(total_runs),  COLORS["text_primary"], COLORS["accent"]),
        ("Average", f"{avg:.1f}",     COLORS["blue"],         COLORS["accent"]),
        ("SR",      f"{sr:.1f}",      COLORS["green"],        COLORS["accent"]),
        ("4s",      str(fours),       COLORS["text_primary"], COLORS["accent"]),
        ("6s",      str(sixes),       COLORS["amber"],        COLORS["accent"]),
        ("Seasons", str(seasons_p),   COLORS["text_muted"],   COLORS["accent"]),
    ]
    cols = st.columns(6)
    for col, (label, val, vc, ac) in zip(cols, bat_stats):
        stat_card(col, label, val, vc, ac)

    spacer(8)

    if not career_view:
        bat_plot = bat.groupby("season").agg(
            runs=("runs_batter", "sum"),
            avg=("batting_average", "mean"),
            sr=("strike_rate", "mean"),
        ).reset_index()

        fig_bat = go.Figure()
        fig_bat.add_trace(go.Scatter(
            x=bat_plot["season"].tolist(),
            y=bat_plot["runs"].tolist(),
            mode="lines+markers",
            name="Runs",
            line=dict(color=COLORS["accent"], width=3),
            marker=dict(size=8, color=COLORS["accent"],
                        line=dict(color=COLORS["bg_base"], width=2)),
            hovertemplate="<b>%{x}</b><br>Runs: %{y}<extra></extra>",
        ))
        apply_chart_theme(fig_bat, height=340)
        fig_bat.update_layout(title="Runs per Season")
        st.plotly_chart(fig_bat, use_container_width=True, key="bat_trend")

    with st.expander("Show detailed batting breakdown"):
        if not career_view:
            c1, c2, c3 = st.columns(3)

            fig_sr = px.bar(bat, x="season", y="strike_rate",
                            title="Strike Rate per Season",
                            color_discrete_sequence=[COLORS["blue"]])
            fig_sr.update_traces(marker_line_width=0)
            apply_chart_theme(fig_sr, height=280)
            c1.plotly_chart(fig_sr, use_container_width=True, key="bat_sr")

            fours_sixes = bat.groupby("season")[["is_four", "is_six"]].sum().reset_index()
            fig_fs = px.bar(
                fours_sixes, x="season", y=["is_four", "is_six"],
                barmode="group", title="4s and 6s per Season",
                color_discrete_map={"is_four": COLORS["green"], "is_six": COLORS["amber"]},
            )
            fig_fs.update_traces(marker_line_width=0)
            apply_chart_theme(fig_fs, height=280)
            c2.plotly_chart(fig_fs, use_container_width=True, key="bat_fs")

            fig_avg = px.bar(bat, x="season", y="batting_average",
                             title="Batting Average per Season",
                             color_discrete_sequence=[COLORS["accent"]])
            fig_avg.update_traces(marker_line_width=0)
            apply_chart_theme(fig_avg, height=280)
            c3.plotly_chart(fig_avg, use_container_width=True, key="bat_avg")

        bat_table = bat[["season", "runs_batter", "balls_faced",
                          "batting_average", "strike_rate", "is_four", "is_six"]].copy()
        bat_table.columns = ["Season", "Runs", "Balls", "Average", "SR", "4s", "6s"]
        bat_table["Average"] = bat_table["Average"].round(2)
        bat_table["SR"]      = bat_table["SR"].round(1)
        st.dataframe(bat_table, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------
# BOWLING SECTION
# ----------------------------------------------------------------
if has_bowl and role in ["Bowler", "All-rounder"]:
    section_header("Bowling Stats", COLORS["amber"])

    wickets   = int(bowl["bowler_wicket"].sum())
    avg_bowl  = float(bowl["bowling_average"].mean())
    eco       = float(bowl["economy"].mean())
    sr_bowl   = float(bowl["strike_rate"].mean())
    overs     = float(bowl["overs"].sum())
    seasons_b = bowl["season"].nunique() if not career_view else "All"

    bowl_stats = [
        ("Wickets", str(wickets),      COLORS["amber"],        COLORS["amber"]),
        ("Average", f"{avg_bowl:.1f}", COLORS["red"],          COLORS["amber"]),
        ("Economy", f"{eco:.2f}",      COLORS["blue"],         COLORS["amber"]),
        ("SR",      f"{sr_bowl:.1f}",  COLORS["green"],        COLORS["amber"]),
        ("Overs",   f"{overs:.1f}",    COLORS["text_primary"], COLORS["amber"]),
        ("Seasons", str(seasons_b),    COLORS["text_muted"],   COLORS["amber"]),
    ]
    cols = st.columns(6)
    for col, (label, val, vc, ac) in zip(cols, bowl_stats):
        stat_card(col, label, val, vc, ac)

    spacer(8)

    if not career_view:
        bowl_plot = bowl.groupby("season").agg(
            wickets=("bowler_wicket", "sum"),
            economy=("economy", "mean"),
        ).reset_index()

        fig_bowl = go.Figure()
        fig_bowl.add_trace(go.Scatter(
            x=bowl_plot["season"].tolist(),
            y=bowl_plot["wickets"].tolist(),
            mode="lines+markers",
            name="Wickets",
            line=dict(color=COLORS["amber"], width=3),
            marker=dict(size=8, color=COLORS["amber"],
                        line=dict(color=COLORS["bg_base"], width=2)),
            hovertemplate="<b>%{x}</b><br>Wickets: %{y}<extra></extra>",
        ))
        apply_chart_theme(fig_bowl, height=340)
        fig_bowl.update_layout(title="Wickets per Season")
        st.plotly_chart(fig_bowl, use_container_width=True, key="bowl_trend")

    with st.expander("Show detailed bowling breakdown"):
        if not career_view:
            c1, c2, c3 = st.columns(3)

            fig_eco = px.bar(bowl, x="season", y="economy",
                             title="Economy per Season",
                             color_discrete_sequence=[COLORS["red"]])
            fig_eco.update_traces(marker_line_width=0)
            apply_chart_theme(fig_eco, height=280)
            c1.plotly_chart(fig_eco, use_container_width=True, key="bowl_eco")

            fig_wk = px.bar(bowl, x="season", y="bowler_wicket",
                            title="Wickets per Season",
                            color_discrete_sequence=[COLORS["amber"]])
            fig_wk.update_traces(marker_line_width=0)
            apply_chart_theme(fig_wk, height=280)
            c2.plotly_chart(fig_wk, use_container_width=True, key="bowl_wk")

            fig_bsr = px.bar(bowl, x="season", y="strike_rate",
                             title="Bowling SR per Season",
                             color_discrete_sequence=[COLORS["accent"]])
            fig_bsr.update_traces(marker_line_width=0)
            apply_chart_theme(fig_bsr, height=280)
            c3.plotly_chart(fig_bsr, use_container_width=True, key="bowl_sr")

        bowl_table = bowl[["season", "bowler_wicket", "overs",
                            "economy", "bowling_average", "strike_rate"]].copy()
        bowl_table.columns = ["Season", "Wickets", "Overs", "Economy", "Average", "SR"]
        bowl_table["Overs"]   = bowl_table["Overs"].round(1)
        bowl_table["Economy"] = bowl_table["Economy"].round(2)
        bowl_table["Average"] = bowl_table["Average"].round(2)
        bowl_table["SR"]      = bowl_table["SR"].round(1)
        st.dataframe(bowl_table, use_container_width=True, hide_index=True)