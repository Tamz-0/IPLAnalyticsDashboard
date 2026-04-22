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
    split_bar,
    stat_card,
)
from utils.theme import COLORS, get_team_color, inject_global_css

st.set_page_config(layout="wide", page_title="Team Analysis | IPL Dashboard")
inject_global_css()


# ----------------------------------------------------------------
# DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return pd.read_csv(os.path.join(base, "data", "processed", "team_stats.csv"))


df = load_data()
df["season"]  = df["season"].astype(int)
df["wins"]    = df["wins"].astype(int)
df["losses"]  = df["losses"].astype(int)
df["matches"] = df["matches"].astype(int)

teams = sorted(df["team"].unique())

start_year = int(df["season"].min())
end_year   = int(df["season"].max())

# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
sidebar_header("Team Intelligence")

sidebar_label("Analyse Team")
main_team = st.sidebar.selectbox("Analyse Team", teams, label_visibility="collapsed")

sidebar_label("Season Range")
season_range = st.sidebar.slider(
    "Season Range",
    min_value=int(df["season"].min()),
    max_value=int(df["season"].max()),
    value=(int(df["season"].min()), int(df["season"].max())),
    label_visibility="collapsed",
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

sidebar_label("Filter Teams Shown")
selected_teams = st.sidebar.multiselect(
    "Filter Teams Shown", teams, default=teams,
    label_visibility="collapsed", placeholder="All teams selected",
)
if not selected_teams:
    selected_teams = teams

st.sidebar.markdown(
    f"<p style='font-size:11px;color:{COLORS['text_faint']};margin-top:4px;'>"
    f"{len(selected_teams)}/{len(teams)} teams</p>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

compare_mode = st.sidebar.toggle("Compare Mode", value=False)
compare_team = None

if compare_mode:
    other_teams = [t for t in teams if t != main_team]
    if other_teams:
        sidebar_label("Compare Against")
        compare_team = st.sidebar.selectbox(
            "Compare Against", other_teams, label_visibility="collapsed"
        )
    else:
        compare_mode = False

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
sidebar_footer(start_year, end_year)


# ----------------------------------------------------------------
# FILTER
# ----------------------------------------------------------------
df_filtered = df[
    (df["season"] >= season_range[0]) &
    (df["season"] <= season_range[1]) &
    (df["team"].isin(selected_teams))
]
team_df = df_filtered[df_filtered["team"] == main_team].copy()

if team_df.empty:
    st.warning("No data for the selected filters.")
    st.stop()


# ----------------------------------------------------------------
# COMPUTED
# ----------------------------------------------------------------
total_matches = int(team_df["matches"].sum())
total_wins    = int(team_df["wins"].sum())
total_losses  = int(team_df["losses"].sum())
win_pct       = (total_wins / total_matches * 100) if total_matches else 0.0
avg_nrr       = float(team_df["nrr"].mean()) if "nrr" in team_df.columns else None
team_color    = get_team_color(main_team)
win_color     = COLORS["green"] if win_pct >= 50 else COLORS["red"]
nrr_display   = f"{avg_nrr:+.3f}" if avg_nrr is not None else "N/A"
nrr_color     = COLORS["green"] if (avg_nrr or 0) >= 0 else COLORS["red"]


# ----------------------------------------------------------------
# PAGE HEADER
# ----------------------------------------------------------------
import colorsys

def hex_to_hsl(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return int(h*360), int(s*100), int(l*100)
h, s, l = hex_to_hsl(team_color)

main_color   = f"hsl({h}, {s}%, {l}%)"
light_color  = f"hsl({h}, {s}%, {min(l+20, 90)}%)"
dim_color    = f"hsl({h}, {max(s-20, 30)}%, {min(l+30, 85)}%)"
page_header(
    f"<span style='display:block; line-height:1;'>IPL Analytics Dashboard</span>"
    f"<span style='display:block; line-height:1.1; margin-top:2px; color:{light_color}; font-weight:800;'>{main_team.upper()}</span>",
    f"Season {season_range[0]}–{season_range[1]} · Team Analysis",
    team_color,
)


# ----------------------------------------------------------------
# STAT STRIP
# ----------------------------------------------------------------
stats = [
    ("Matches Played", str(total_matches), COLORS["text_primary"]),
    ("Wins",           str(total_wins),    COLORS["green"]),
    ("Losses",         str(total_losses),  COLORS["red"]),
    ("Win Rate",       f"{win_pct:.1f}%",  win_color),
    ("Avg NRR",        nrr_display,        nrr_color),
]
cols = st.columns(5)
for col, (label, value, vc) in zip(cols, stats):
    stat_card(col, label, value, vc, team_color)

spacer(14)

if all(c in team_df.columns for c in ["runs_scored", "runs_conceded", "chasing_wins", "defending_wins"]):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Runs Scored",    f"{int(team_df['runs_scored'].sum()):,}")
    c2.metric("Runs Conceded",  f"{int(team_df['runs_conceded'].sum()):,}")
    c3.metric("Chasing Wins",   int(team_df["chasing_wins"].sum()))
    c4.metric("Defending Wins", int(team_df["defending_wins"].sum()))
    spacer(8)


# ----------------------------------------------------------------
# SECTION — WIN % TREND
# ----------------------------------------------------------------
section_header("Win % Over Seasons", COLORS["accent"])

team_df_s = team_df.sort_values("season")
fig_line  = go.Figure()
fig_line.add_trace(go.Scatter(
    x=team_df_s["season"].tolist(),
    y=team_df_s["win_pct"].round(1).tolist(),
    mode="lines+markers",
    line=dict(color=team_color, width=3),
    marker=dict(size=8, color=team_color, line=dict(color=COLORS["bg_base"], width=2)),
    name=main_team,
    hovertemplate="<b>Season %{x}</b><br>Win%%: %{y:.1f}%%<extra></extra>",
))

if compare_mode and compare_team:
    df_ct = df[
        (df["team"] == compare_team) &
        (df["season"] >= season_range[0]) &
        (df["season"] <= season_range[1])
    ].sort_values("season")
    ct_color = get_team_color(compare_team)
    fig_line.add_trace(go.Scatter(
        x=df_ct["season"].tolist(),
        y=df_ct["win_pct"].round(1).tolist(),
        mode="lines+markers",
        line=dict(color=ct_color, width=3, dash="dot"),
        marker=dict(size=8, color=ct_color, line=dict(color=COLORS["bg_base"], width=2)),
        name=compare_team,
        hovertemplate="<b>Season %{x}</b><br>Win%%: %{y:.1f}%%<extra></extra>",
    ))

fig_line.add_hline(
    y=50, line_dash="dash", line_color=COLORS["border_input"],
    annotation_text="50%", annotation_font_color=COLORS["text_faint"],
    annotation_position="right",
)
apply_chart_theme(fig_line, height=360)
st.plotly_chart(fig_line, use_container_width=True, key="win_pct_trend")


# ----------------------------------------------------------------
# SECTION — WIN / LOSS BREAKDOWN
# ----------------------------------------------------------------
section_header("Win / Loss Breakdown", COLORS["accent"])

left, right = st.columns([3, 2])

fig_wl = px.bar(
    team_df_s, x="season", y=["wins", "losses"],
    barmode="group",
    color_discrete_map={"wins": COLORS["green"], "losses": COLORS["red"]},
    title="Wins vs Losses per Season",
)
fig_wl.update_traces(marker_line_width=0)
apply_chart_theme(fig_wl, height=340)
left.plotly_chart(fig_wl, use_container_width=True, key="wl_bar")

fig_donut = go.Figure(go.Pie(
    values=[total_wins, total_losses],
    labels=["Wins", "Losses"],
    hole=0.65,
    marker=dict(colors=[COLORS["green"], COLORS["red"]],
                line=dict(color=COLORS["bg_base"], width=3)),
    textinfo="label+percent",
    textfont=dict(size=13, color=COLORS["text_primary"]),
    hovertemplate="%{label}: %{value}<extra></extra>",
))
fig_donut.update_layout(
    title="Overall Ratio",
    showlegend=False,
    annotations=[dict(
        text=f"<b>{win_pct:.0f}%</b>",
        x=0.5, y=0.5,
        font=dict(size=26, color=COLORS["text_primary"],
                  family="Barlow Condensed, sans-serif"),
        showarrow=False,
    )],
)
apply_chart_theme(fig_donut, height=340)
right.plotly_chart(fig_donut, use_container_width=True, key="donut")


# ----------------------------------------------------------------
# SECTION — TOSS ANALYSIS
# ----------------------------------------------------------------
section_header("Toss Analysis", COLORS["amber"])

has_toss     = "toss_wins" in team_df.columns and "toss_win_match_win_pct" in team_df.columns
has_decision = "bat" in team_df.columns and "field" in team_df.columns

if has_toss:
    toss_win_pct   = (float(team_df["toss_wins"].sum()) / total_matches * 100) if total_matches else 0
    win_after_toss = float(team_df["toss_win_match_win_pct"].mean())
    tc1, tc2 = st.columns(2)
    tc1.metric("Toss Win %",           f"{toss_win_pct:.1f}%")
    tc2.metric("Win % after Toss Win", f"{win_after_toss:.1f}%")
else:
    st.info("Toss win data unavailable.")

if has_decision:
    bat_count   = int(team_df["bat"].sum())
    field_count = int(team_df["field"].sum())
    total_dec   = bat_count + field_count
    pct_bat     = bat_count / total_dec if total_dec else 0.5

    tl, tr = st.columns([2, 3])
    with tl:
        split_bar(
            f"Bat First ({bat_count})",
            f"Field First ({field_count})",
            pct_bat,
            COLORS["blue"],
            COLORS["amber"],
        )

    decision_df = pd.DataFrame({
        "Decision": ["Bat First", "Field First"],
        "Count":    [bat_count, field_count],
    })
    fig_toss = px.bar(
        decision_df, x="Count", y="Decision", orientation="h",
        title="Toss Decision Count", color="Decision",
        color_discrete_map={"Bat First": COLORS["blue"], "Field First": COLORS["amber"]},
    )
    fig_toss.update_traces(marker_line_width=0)
    apply_chart_theme(fig_toss, height=220)
    tr.plotly_chart(fig_toss, use_container_width=True, key="toss_bar")
else:
    st.info("Toss decision data unavailable.")


# ----------------------------------------------------------------
# SECTION — CHASING vs DEFENDING
# ----------------------------------------------------------------
if all(c in team_df.columns for c in ["chasing_wins", "defending_wins"]):
    section_header("Chasing vs Defending", COLORS["green"])

    chase_w  = int(team_df["chasing_wins"].sum())
    defend_w = int(team_df["defending_wins"].sum())
    cd_total = chase_w + defend_w
    pct_ch   = chase_w / cd_total if cd_total else 0.5

    cl, cr = st.columns([2, 3])
    with cl:
        split_bar(
            f"Chasing ({chase_w})",
            f"Defending ({defend_w})",
            pct_ch,
            COLORS["blue"],
            COLORS["accent"],
        )

    cd_df = pd.DataFrame({
        "Type":  ["Chasing Wins", "Defending Wins"],
        "Count": [chase_w, defend_w],
    })
    fig_cd = px.bar(
        cd_df, x="Type", y="Count", color="Type",
        color_discrete_map={"Chasing Wins": COLORS["blue"], "Defending Wins": COLORS["accent"]},
        title="Chasing vs Defending Wins",
    )
    fig_cd.update_traces(marker_line_width=0)
    apply_chart_theme(fig_cd, height=260)
    cr.plotly_chart(fig_cd, use_container_width=True, key="chase_defend")


# ----------------------------------------------------------------
# SECTION — TEAM COMPARISON
# ----------------------------------------------------------------
section_header("Team Comparison", COLORS["blue"])
st.caption(f"Overall performance · Seasons {season_range[0]}\u2013{season_range[1]} · Not direct H2H")

df_comp = df[(df["season"] >= season_range[0]) & (df["season"] <= season_range[1])]

colA, colB = st.columns(2)
teamA = colA.selectbox("Team A", teams, index=0, key="comp_a")
teamB = colB.selectbox("Team B", teams, index=min(1, len(teams) - 1), key="comp_b")

df_A      = df_comp[df_comp["team"] == teamA]
df_B      = df_comp[df_comp["team"] == teamB]
wins_A    = int(df_A["wins"].sum())
wins_B    = int(df_B["wins"].sum())
matches_A = int(df_A["matches"].sum())
matches_B = int(df_B["matches"].sum())
wpct_A    = (wins_A / matches_A * 100) if matches_A else 0
wpct_B    = (wins_B / matches_B * 100) if matches_B else 0
color_A   = get_team_color(teamA)
color_B   = get_team_color(teamB)
combined  = wins_A + wins_B
pct_A_bar = wins_A / combined if combined else 0.5

card_l, card_mid, card_r = st.columns([5, 1, 5])

card_l.markdown(f"""
<div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
            border-top:3px solid {color_A};border-radius:10px;padding:20px 22px;">
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:18px;
                font-weight:800;color:{COLORS['text_primary']};margin-bottom:8px;">
        {teamA}
    </div>
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:38px;
                font-weight:800;color:{color_A};line-height:1;">{wins_A}</div>
    <div style="font-size:11px;color:{COLORS['text_dim']};margin-top:4px;
                text-transform:uppercase;letter-spacing:0.08em;">Wins</div>
    <div style="font-size:13px;color:{COLORS['text_muted']};margin-top:10px;">
        {wpct_A:.1f}% win rate &middot; {matches_A} matches
    </div>
</div>
""", unsafe_allow_html=True)

card_mid.markdown(f"""
<div style="display:flex;align-items:center;justify-content:center;
            height:100%;padding-top:36px;
            font-family:'Barlow Condensed',sans-serif;
            font-size:16px;font-weight:800;
            color:{COLORS['text_faint']};letter-spacing:0.1em;">
    VS
</div>
""", unsafe_allow_html=True)

card_r.markdown(f"""
<div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
            border-top:3px solid {color_B};border-radius:10px;padding:20px 22px;">
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:18px;
                font-weight:800;color:{COLORS['text_primary']};margin-bottom:8px;">
        {teamB}
    </div>
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:38px;
                font-weight:800;color:{color_B};line-height:1;">{wins_B}</div>
    <div style="font-size:11px;color:{COLORS['text_dim']};margin-top:4px;
                text-transform:uppercase;letter-spacing:0.08em;">Wins</div>
    <div style="font-size:13px;color:{COLORS['text_muted']};margin-top:10px;">
        {wpct_B:.1f}% win rate &middot; {matches_B} matches
    </div>
</div>
""", unsafe_allow_html=True)

spacer(12)
split_bar(
    f"{teamA}",
    f"{teamB}",
    pct_A_bar,
    color_A,
    color_B,
)