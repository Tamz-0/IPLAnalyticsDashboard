import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.charts import apply_theme

st.set_page_config(layout="wide", page_title="Season Deep Dive | IPL Dashboard")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
.stApp { background: #080810; }

section[data-testid="stSidebar"] {
    background: #0a0a18 !important;
    border-right: 1px solid #1e1e3a !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1rem !important; }

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
[data-testid="stPlotlyChart"] {
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stDataFrame"] {
    border: 1px solid #1e1e3a !important;
    border-radius: 8px !important;
}
hr { border-color: #1e1e3a !important; margin: 1rem 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

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

def get_team_color(team):
    return TEAM_COLORS.get(team, "#7c3aed")

# ----------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------
def apply_chart_theme(fig, height=380):
    fig.update_layout(
        plot_bgcolor="#0d0d20",
        paper_bgcolor="#0d0d20",
        font=dict(color="#94a3b8", family="Barlow, sans-serif"),
        title_font=dict(color="#e8e8ff", size=14,
                        family="Barlow Condensed, sans-serif"),
        xaxis=dict(gridcolor="#1a1a30", linecolor="#1a1a30",
                   tickcolor="#2a2a4a", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#1a1a30", linecolor="#1a1a30",
                   tickcolor="#2a2a4a", tickfont=dict(size=11)),
        margin=dict(l=16, r=16, t=40, b=16),
        hoverlabel=dict(bgcolor="#111128", bordercolor="#2a2a4a",
                        font=dict(color="#e8e8ff", size=13)),
        legend=dict(bgcolor="#111128", bordercolor="#1e1e3a",
                    borderwidth=1, font=dict(color="#94a3b8", size=12)),
        height=height
    )
    return fig

def section_header(title, color="#7c3aed"):
    st.markdown(f"""
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:18px;
                font-weight:700;letter-spacing:0.06em;text-transform:uppercase;
                color:#e8e8ff;margin:20px 0 16px;padding-left:10px;
                border-left:3px solid {color};">
        {title}
    </div>""", unsafe_allow_html=True)

def sidebar_label(text):
    st.sidebar.markdown(
        f"<p style='font-size:11px;text-transform:uppercase;letter-spacing:0.08em;"
        f"color:#5a5a8a;font-weight:600;margin:14px 0 4px;'>{text}</p>",
        unsafe_allow_html=True
    )

def stat_card(col, label, value, color="#e8e8ff", top_color="#7c3aed"):
    col.markdown(f"""
    <div style="background:#0d0d20;border:1px solid #1e1e3a;
                border-top:3px solid {top_color};border-radius:10px;
                padding:14px 16px;">
        <div style="font-size:10px;text-transform:uppercase;
                    letter-spacing:0.1em;color:#5a5a8a;margin-bottom:6px;">
            {label}
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:26px;font-weight:800;color:{color};">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)

def leaderboard_card(title, data, value_label, accent="#f59e0b"):
    rows = ""
    for i, (name, val) in enumerate(data.items(), start=1):
        is_first  = i == 1
        name_color = accent if is_first else "#e8e8ff"
        val_color  = accent if is_first else "#94a3b8"
        rank_style = (
            f"font-family:'Barlow Condensed',sans-serif;font-size:16px;"
            f"font-weight:800;color:{accent};"
            if is_first else
            "font-size:13px;color:#3a3a6a;"
        )
        border = "border-bottom:1px solid #1e1e3a;" if i < len(data) else ""
        rows += f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:10px 0;{border}">
            <span style="{rank_style}min-width:24px;">#{i}</span>
            <span style="color:{name_color};font-size:14px;
                         flex:1;padding:0 12px;font-weight:{'700' if is_first else '400'};">
                {name}
            </span>
            <span style="color:{val_color};font-family:'Barlow Condensed',sans-serif;
                         font-size:18px;font-weight:700;">
                {int(val)}
                <span style="font-size:11px;color:#5a5a8a;font-weight:400;">
                    {value_label}
                </span>
            </span>
        </div>
        """

    return f"""
    <div style="background:#0d0d20;border:1px solid #1e1e3a;
                border-top:3px solid {accent};border-radius:10px;
                padding:16px 20px;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:14px;
                    font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
                    color:#5a5a8a;margin-bottom:12px;">{title}</div>
        {rows}
    </div>
    """.strip()

# ----------------------------------------------------------------
# LOAD
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    season_path = os.path.join(BASE_DIR, "data", "processed", "season_stats.csv")
    bat_path = os.path.join(BASE_DIR, "data", "processed", "player_batting.csv")
    bowl_path = os.path.join(BASE_DIR, "data", "processed", "player_bowler.csv")
    team_path = os.path.join(BASE_DIR, "data", "processed", "team_stats.csv")
    season = pd.read_csv(season_path)
    bat    = pd.read_csv(bat_path)
    bowl   = pd.read_csv(bowl_path)
    team   = pd.read_csv(team_path)

    season["season"] = season["season"].astype(int)
    bat["season"]    = bat["season"].astype(int)
    bowl["season"]   = bowl["season"].astype(int)
    team["season"]   = team["season"].astype(int)
    team["wins"]     = team["wins"].astype(int)
    team["matches"]  = team["matches"].astype(int)

    return season, bat, bowl, team

# ================================================================
# MAIN
# ================================================================
def main():
    season_df, bat_df, bowl_df, team_df = load_data()

    seasons = sorted(season_df["season"].unique(), reverse=True)

    # ----------------------------------------------------------------
    # SIDEBAR
    # ----------------------------------------------------------------
    st.sidebar.markdown("""
    <div style="padding:8px 4px 16px;border-bottom:1px solid #1e1e3a;
                margin-bottom:16px;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:22px;
                    font-weight:800;color:#e8e8ff;letter-spacing:0.06em;">
            🏏 IPL ANALYTICS
        </div>
        <div style="font-size:11px;color:#5a5a8a;letter-spacing:0.1em;
                    text-transform:uppercase;margin-top:4px;">
            Season Deep Dive
        </div>
    </div>
    """, unsafe_allow_html=True)

    sidebar_label("Select Season")
    default_year = 2025
    default_index = seasons.index(default_year) if default_year in seasons else 0

    selected = st.sidebar.selectbox(
        "Select Season",
        seasons,
        index=default_index,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<p style='font-size:11px;color:#2a2a4a;text-align:center;"
        "letter-spacing:0.06em;'>DATA · IPL 2008–2025</p>",
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------------
    # FILTER
    # ----------------------------------------------------------------
    season_row = season_df[season_df["season"] == selected].iloc[0]
    bat        = bat_df[bat_df["season"] == selected]
    bowl       = bowl_df[bowl_df["season"] == selected]
    teams      = team_df[team_df["season"] == selected].copy()

    # ----------------------------------------------------------------
    # CHAMPION BANNER
    # ----------------------------------------------------------------
    winner = str(season_row["title_winner"]) \
             if "title_winner" in season_row.index \
             and pd.notna(season_row["title_winner"]) \
             else "Unknown"

    winner_color = get_team_color(winner)

    st.markdown(f"""
    <div style="background:#0d0d20;border:1px solid #1e1e3a;
                border-left:6px solid {winner_color};
                border-radius:12px;padding:24px 28px;
                display:flex;align-items:center;gap:20px;
                margin-bottom:28px;">
        <div style="font-size:36px;">🏆</div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:36px;font-weight:800;
                        color:{winner_color};letter-spacing:0.04em;
                        line-height:1;">
                {winner.upper()}
            </div>
            <div style="font-size:12px;color:#5a5a8a;
                        letter-spacing:0.1em;text-transform:uppercase;
                        margin-top:4px;">
                IPL {selected} Champions
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # SEASON STAT STRIP
    # ----------------------------------------------------------------
    total_matches = int(season_row["total_matches"]) \
                    if "total_matches" in season_row.index else "N/A"
    total_runs    = f"{int(season_row['total_runs']):,}" \
                    if "total_runs" in season_row.index else "N/A"
    total_sixes    = int(season_row["total_sixes"]) \
                    if "total_sixes" in season_row.index else "N/A"
    highest_score = int(season_row["highest_score"]) \
                    if "highest_score" in season_row.index else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    stat_card(c1, "Total Matches",  str(total_matches), "#e8e8ff", winner_color)
    stat_card(c2, "Total Runs",     str(total_runs),    "#3b82f6", winner_color)
    stat_card(c3, "Total Sixes",    str(total_sixes),    "#f59e0b", winner_color)
    stat_card(c4, "Highest Score",  str(highest_score), "#22c55e", winner_color)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # SECTION 1 — TOP PERFORMERS
    # ----------------------------------------------------------------
    
    section_header("Top Performers", "#f59e0b")

    top_runs = bat.groupby("batter")["runs_batter"] \
                  .sum().sort_values(ascending=False).head(5)
    top_wkts = bowl.groupby("bowler")["bowler_wicket"] \
                   .sum().sort_values(ascending=False).head(5)

    lc, rc = st.columns(2)
    with lc:
        st.components.v1.html(
            leaderboard_card("Top Run Scorers", top_runs, "runs", "#7c3aed"),
            height=300,
            scrolling=False
        )

    with rc:
        st.components.v1.html(
            leaderboard_card("Top Wicket Takers", top_wkts, "wkts", "#f59e0b"),
            height=300,
            scrolling=False
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    
    # ----------------------------------------------------------------
    # SECTION 2 — TEAM STANDINGS
    # ----------------------------------------------------------------
    
    section_header("Team Standings", "#7c3aed")

    teams["win_pct"] = (teams["wins"] / teams["matches"] * 100).round(1)
    teams_sorted     = teams.sort_values("wins", ascending=False)

    # Color each bar by team color
    team_colors_list = [
        get_team_color(t) for t in teams_sorted["team"]
    ]

    fig_teams = go.Figure(go.Bar(
        x=teams_sorted["team"].tolist(),
        y=teams_sorted["wins"].tolist(),
        marker_color=team_colors_list,
        marker_line_width=0,
        customdata=teams_sorted[["win_pct", "matches"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Wins: %{y}<br>"
            "Win%%: %{customdata[0]:.1f}%%<br>"
            "Matches: %{customdata[1]}<extra></extra>"
        )
    ))
    fig_teams.update_layout(title="Wins per Team")
    apply_chart_theme(fig_teams, height=380)
    fig_teams.update_layout(
        xaxis=dict(tickangle=-30, gridcolor="#1a1a30", linecolor="#1a1a30")
    )
    st.plotly_chart(fig_teams, use_container_width=True, key="team_standings")

    # ----------------------------------------------------------------
    # SECTION 3 — THREE INSIGHT CHARTS
    # ----------------------------------------------------------------
    section_header("Season Insights", "#22c55e")

    ci1, ci2, ci3 = st.columns(3)

    # NRR chart
    if "nrr" in teams.columns:
        nrr_sorted = teams.sort_values("nrr", ascending=False)
        nrr_colors = [
            "#22c55e" if v >= 0 else "#ef4444"
            for v in nrr_sorted["nrr"]
        ]
        fig_nrr = go.Figure(go.Bar(
            x=nrr_sorted["team"].tolist(),
            y=nrr_sorted["nrr"].round(3).tolist(),
            marker_color=nrr_colors,
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>NRR: %{y:.3f}<extra></extra>"
        ))
        fig_nrr.update_layout(title="Net Run Rate")
        apply_chart_theme(fig_nrr, height=320)
        fig_nrr.update_layout(
            xaxis=dict(tickangle=-30, gridcolor="#1a1a30",
                       linecolor="#1a1a30")
        )
        ci1.plotly_chart(fig_nrr, use_container_width=True, key="nrr_chart")
    else:
        ci1.info("NRR data unavailable")

    # Toss decisions from team_stats
    if "bat" in teams.columns and "field" in teams.columns:
        bat_total   = int(teams["bat"].sum())
        field_total = int(teams["field"].sum())

        fig_toss = go.Figure(go.Pie(
            values=[bat_total, field_total],
            labels=["Bat First", "Field First"],
            hole=0.55,
            marker=dict(
                colors=["#3b82f6", "#f59e0b"],
                line=dict(color="#080810", width=3)
            ),
            textinfo="label+percent",
            textfont=dict(size=12, color="#e8e8ff"),
            hovertemplate="%{label}: %{value}<extra></extra>"
        ))
        fig_toss.update_layout(
            title="Toss Decisions",
            showlegend=False
        )
        apply_chart_theme(fig_toss, height=320)
        ci2.plotly_chart(fig_toss, use_container_width=True, key="toss_pie")
    else:
        ci2.info("Toss data unavailable")

    # Runs scored per team
    if "runs_scored" in teams.columns:
        runs_sorted  = teams.sort_values("runs_scored", ascending=False)
        runs_colors  = [get_team_color(t) for t in runs_sorted["team"]]
        fig_runs = go.Figure(go.Bar(
            x=runs_sorted["team"].tolist(),
            y=runs_sorted["runs_scored"].tolist(),
            marker_color=runs_colors,
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Runs: %{y:,}<extra></extra>"
        ))
        fig_runs.update_layout(title="Runs Scored per Team")
        apply_chart_theme(fig_runs, height=320)
        fig_runs.update_layout(
            xaxis=dict(tickangle=-30, gridcolor="#1a1a30",
                       linecolor="#1a1a30")
        )
        ci3.plotly_chart(fig_runs, use_container_width=True, key="runs_chart")
    else:
        ci3.info("Runs data unavailable")

    # ----------------------------------------------------------------
    # SECTION 4 — FULL TEAM STATS TABLE
    # ----------------------------------------------------------------
    section_header("Full Team Stats", "#3b82f6")

    display_cols = ["team", "matches", "wins", "losses", "win_pct"]
    extra        = ["nrr", "runs_scored", "runs_conceded",
                    "chasing_wins", "defending_wins"]
    display_cols += [c for c in extra if c in teams.columns]

    table = teams[display_cols].sort_values(
        "wins", ascending=False
    ).copy()

    rename_map = {
        "team":            "Team",
        "matches":         "M",
        "wins":            "W",
        "losses":          "L",
        "win_pct":         "Win%",
        "nrr":             "NRR",
        "runs_scored":     "Runs For",
        "runs_conceded":   "Runs Against",
        "chasing_wins":    "Chase W",
        "defending_wins":  "Defend W",
    }
    table = table.rename(columns=rename_map)

    if "Win%" in table.columns:
        table["Win%"] = table["Win%"].round(1)
    if "NRR" in table.columns:
        table["NRR"]  = table["NRR"].round(3)

    st.dataframe(table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()