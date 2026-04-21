import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.charts import apply_theme

st.set_page_config(layout="wide", page_title="Team Analysis | IPL Dashboard")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

.stApp { background: #080810; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1e1e3a !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1rem !important;
}

/* Metric cards */
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

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #111128 !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
    color: #e8e8ff !important;
}

/* Multiselect */
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

/* Chart containers */
[data-testid="stPlotlyChart"] {
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    overflow: hidden;
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

@st.cache_data
def load_data():
    return pd.read_csv("../../data/processed/team_stats.csv")

def apply_chart_theme(fig, height=380):
    fig.update_layout(
        plot_bgcolor="#0d0d20",
        paper_bgcolor="#0d0d20",
        font=dict(color="#94a3b8", family="Barlow, sans-serif"),
        title_font=dict(color="#e8e8ff", size=15,
                        family="Barlow Condensed, sans-serif"),
        xaxis=dict(gridcolor="#1a1a30", linecolor="#1a1a30",
                   tickcolor="#2a2a4a", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#1a1a30", linecolor="#1a1a30",
                   tickcolor="#2a2a4a", tickfont=dict(size=11)),
        margin=dict(l=16, r=16, t=44, b=16),
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
        f"color:#5a5a8a;font-weight:600;margin:12px 0 4px;'>{text}</p>",
        unsafe_allow_html=True
    )

def main():
    df = load_data()
    df["season"]  = df["season"].astype(int)
    df["wins"]    = df["wins"].astype(int)
    df["losses"]  = df["losses"].astype(int)
    df["matches"] = df["matches"].astype(int)

    teams = sorted(df["team"].unique())

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
            Team Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- ANALYSE TEAM (primary selector — show this first) ---
    sidebar_label("Analyse Team")
    main_team = st.sidebar.selectbox(
        "Analyse Team",
        teams,
        label_visibility="collapsed"
    )

    # --- SEASON RANGE ---
    sidebar_label("Season Range")
    season_range = st.sidebar.slider(
        "Season Range",
        min_value=int(df["season"].min()),
        max_value=int(df["season"].max()),
        value=(int(df["season"].min()), int(df["season"].max())),
        label_visibility="collapsed"
    )

    # --- COMPARE TEAMS (simple multiselect, not checkbox maze) ---
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    sidebar_label("Filter Teams Shown")
    selected_teams = st.sidebar.multiselect(
        "Filter Teams Shown",
        teams,
        default=teams,
        label_visibility="collapsed",
        placeholder="All teams selected"
    )
    if not selected_teams:
        selected_teams = teams  # fallback to all if cleared

    st.sidebar.markdown(
        f"<p style='font-size:11px;color:#3a3a6a;margin-top:4px;'>"
        f"{len(selected_teams)}/{len(teams)} teams</p>",
        unsafe_allow_html=True
    )

    # --- COMPARE MODE ---
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    compare_mode = st.sidebar.toggle("Compare Mode", value=False)
    compare_team = None

    if compare_mode:
        other_teams = [t for t in teams if t != main_team]
        if other_teams:
            sidebar_label("Compare Against")
            compare_team = st.sidebar.selectbox(
                "Compare Against",
                other_teams,
                label_visibility="collapsed"
            )
        else:
            st.sidebar.caption("No other teams available")
            compare_mode = False

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<p style='font-size:11px;color:#2a2a4a;text-align:center;"
        "letter-spacing:0.06em;'>DATA · IPL 2008–2025</p>",
        unsafe_allow_html=True
    )

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
    win_pct       = (total_wins / total_matches * 100) if total_matches else 0
    avg_nrr       = float(team_df["nrr"].mean()) if "nrr" in team_df.columns else None
    team_color    = get_team_color(main_team)
    win_color     = "#22c55e" if win_pct >= 50 else "#ef4444"
    nrr_display   = f"{avg_nrr:+.3f}" if avg_nrr is not None else "N/A"
    nrr_color     = "#22c55e" if (avg_nrr or 0) >= 0 else "#ef4444"

    # ----------------------------------------------------------------
    # PAGE TITLE
    # ----------------------------------------------------------------
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;
                margin-bottom:28px;padding-bottom:20px;
                border-bottom:1px solid #1e1e3a;">
        <div style="width:6px;height:52px;background:{team_color};
                    border-radius:3px;flex-shrink:0;"></div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:34px;font-weight:800;color:#e8e8ff;
                        letter-spacing:0.04em;line-height:1;">
                {main_team.upper()}
            </div>
            <div style="font-size:12px;color:#5a5a8a;letter-spacing:0.1em;
                        text-transform:uppercase;margin-top:3px;">
                Season {season_range[0]} – {season_range[1]} · Team Analysis
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # STAT STRIP
    # ----------------------------------------------------------------
    stats = [
        ("Matches Played", str(total_matches), "#e8e8ff"),
        ("Wins",           str(total_wins),    "#22c55e"),
        ("Losses",         str(total_losses),  "#ef4444"),
        ("Win Rate",       f"{win_pct:.1f}%",  win_color),
        ("Avg NRR",        nrr_display,        nrr_color),
    ]
    cols = st.columns(5)
    for col, (label, value, color) in zip(cols, stats):
        col.markdown(f"""
        <div style="background:#0d0d20;border:1px solid #1e1e3a;
                    border-top:3px solid {team_color};border-radius:10px;
                    padding:16px 18px;">
            <div style="font-size:10px;text-transform:uppercase;
                        letter-spacing:0.1em;color:#5a5a8a;
                        margin-bottom:6px;">{label}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:28px;font-weight:800;color:{color};">
                {value}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # EXTRA METRICS
    # ----------------------------------------------------------------
    extra_cols = ["runs_scored","runs_conceded","chasing_wins","defending_wins"]
    if all(c in team_df.columns for c in extra_cols):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Runs Scored",   f"{int(team_df['runs_scored'].sum()):,}")
        c2.metric("Runs Conceded", f"{int(team_df['runs_conceded'].sum()):,}")
        c3.metric("Chasing Wins",  int(team_df["chasing_wins"].sum()))
        c4.metric("Defending Wins",int(team_df["defending_wins"].sum()))
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # SECTION 1 — WIN % TREND
    # ----------------------------------------------------------------
    section_header("Win % Over Seasons", "#7c3aed")

    team_df_s = team_df.sort_values("season")
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=team_df_s["season"].tolist(),
        y=team_df_s["win_pct"].round(1).tolist(),
        mode="lines+markers",
        line=dict(color=team_color, width=3),
        marker=dict(size=8, color=team_color,
                    line=dict(color="#080810", width=2)),
        name=main_team,
        hovertemplate="<b>Season %{x}</b><br>Win%%: %{y:.1f}%%<extra></extra>"
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
            marker=dict(size=8, color=ct_color,
                        line=dict(color="#080810", width=2)),
            name=compare_team,
            hovertemplate="<b>Season %{x}</b><br>Win%%: %{y:.1f}%%<extra></extra>"
        ))

    fig_line.add_hline(y=50, line_dash="dash", line_color="#2a2a4a",
                       annotation_text="50%", annotation_font_color="#3a3a6a",
                       annotation_position="right")
    apply_chart_theme(fig_line, height=360)
    st.plotly_chart(fig_line, use_container_width=True, key="win_pct_trend")

    # ----------------------------------------------------------------
    # SECTION 2 — WINS VS LOSSES + DONUT
    # ----------------------------------------------------------------
    section_header("Win / Loss Breakdown", "#7c3aed")

    left, right = st.columns([3, 2])

    fig_wl = px.bar(
        team_df_s, x="season", y=["wins","losses"],
        barmode="group",
        color_discrete_map={"wins":"#22c55e","losses":"#ef4444"},
        title="Wins vs Losses per Season"
    )
    fig_wl.update_traces(marker_line_width=0)
    apply_chart_theme(fig_wl, height=340)
    left.plotly_chart(fig_wl, use_container_width=True, key="wl_bar")

    fig_donut = go.Figure(go.Pie(
        values=[total_wins, total_losses],
        labels=["Wins","Losses"],
        hole=0.65,
        marker=dict(colors=["#22c55e","#ef4444"],
                    line=dict(color="#080810", width=3)),
        textinfo="label+percent",
        textfont=dict(size=13, color="#e8e8ff"),
        hovertemplate="%{label}: %{value}<extra></extra>"
    ))
    fig_donut.update_layout(
        title="Overall Ratio", showlegend=False,
        annotations=[dict(
            text=f"<b>{win_pct:.0f}%</b>",
            x=0.5, y=0.5,
            font=dict(size=26, color="#e8e8ff",
                      family="Barlow Condensed, sans-serif"),
            showarrow=False
        )]
    )
    apply_chart_theme(fig_donut, height=340)
    right.plotly_chart(fig_donut, use_container_width=True, key="donut")

    # ----------------------------------------------------------------
    # SECTION 3 — TOSS
    # ----------------------------------------------------------------
    section_header("Toss Analysis", "#f59e0b")

    has_toss     = "toss_wins" in team_df.columns and \
                   "toss_win_match_win_pct" in team_df.columns
    has_decision = "bat" in team_df.columns and "field" in team_df.columns

    if has_toss:
        toss_win_pct   = (float(team_df["toss_wins"].sum()) / total_matches * 100) \
                          if total_matches else 0
        win_after_toss = float(team_df["toss_win_match_win_pct"].mean())
        c1, c2 = st.columns(2)
        c1.metric("Toss Win %",           f"{toss_win_pct:.1f}%")
        c2.metric("Win % after Toss Win", f"{win_after_toss:.1f}%")
    else:
        st.info("Toss win data unavailable.")

    if has_decision:
        bat_count   = int(team_df["bat"].sum())
        field_count = int(team_df["field"].sum())
        total_dec   = bat_count + field_count
        pct_bat     = bat_count / total_dec if total_dec else 0.5

        tl, tr = st.columns([2, 3])
        tl.markdown(f"""
        <div style="background:#0d0d20;border:1px solid #1e1e3a;
                    border-radius:10px;padding:20px 22px;margin-top:12px;">
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;
                        color:#5a5a8a;margin-bottom:14px;">Toss Decision Split</div>
            <div style="display:flex;justify-content:space-between;
                        font-size:13px;color:#94a3b8;margin-bottom:8px;">
                <span>Bat First ({bat_count})</span>
                <span>Field First ({field_count})</span>
            </div>
            <div style="display:flex;height:10px;border-radius:5px;
                        overflow:hidden;background:#1a1a30;">
                <div style="width:{pct_bat*100:.1f}%;background:#3b82f6;"></div>
                <div style="width:{(1-pct_bat)*100:.1f}%;background:#f59e0b;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;
                        font-size:20px;font-weight:700;margin-top:10px;
                        font-family:'Barlow Condensed',sans-serif;">
                <span style="color:#3b82f6;">{pct_bat*100:.0f}%</span>
                <span style="color:#f59e0b;">{(1-pct_bat)*100:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        decision_df = pd.DataFrame({
            "Decision": ["Bat First","Field First"],
            "Count":    [bat_count, field_count]
        })
        fig_toss = px.bar(
            decision_df, x="Count", y="Decision", orientation="h",
            title="Toss Decision Count", color="Decision",
            color_discrete_map={"Bat First":"#3b82f6","Field First":"#f59e0b"}
        )
        fig_toss.update_traces(marker_line_width=0)
        apply_chart_theme(fig_toss, height=220)
        tr.plotly_chart(fig_toss, use_container_width=True, key="toss_bar")
    else:
        st.info("Toss decision data unavailable.")

    # ----------------------------------------------------------------
    # SECTION 4 — CHASING VS DEFENDING
    # ----------------------------------------------------------------
    if all(c in team_df.columns for c in ["chasing_wins","defending_wins"]):
        section_header("Chasing vs Defending", "#22c55e")

        chase_w  = int(team_df["chasing_wins"].sum())
        defend_w = int(team_df["defending_wins"].sum())
        cd_total = chase_w + defend_w
        pct_ch   = chase_w / cd_total if cd_total else 0.5

        cl, cr = st.columns([2, 3])
        cl.markdown(f"""
        <div style="background:#0d0d20;border:1px solid #1e1e3a;
                    border-radius:10px;padding:20px 22px;">
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;
                        color:#5a5a8a;margin-bottom:14px;">Win Style Split</div>
            <div style="display:flex;justify-content:space-between;
                        font-size:13px;color:#94a3b8;margin-bottom:8px;">
                <span>Chasing ({chase_w})</span>
                <span>Defending ({defend_w})</span>
            </div>
            <div style="display:flex;height:10px;border-radius:5px;
                        overflow:hidden;background:#1a1a30;">
                <div style="width:{pct_ch*100:.1f}%;background:#3b82f6;"></div>
                <div style="width:{(1-pct_ch)*100:.1f}%;background:#7c3aed;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;
                        font-size:20px;font-weight:700;margin-top:10px;
                        font-family:'Barlow Condensed',sans-serif;">
                <span style="color:#3b82f6;">{pct_ch*100:.0f}%</span>
                <span style="color:#7c3aed;">{(1-pct_ch)*100:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cd_df = pd.DataFrame({
            "Type":  ["Chasing Wins","Defending Wins"],
            "Count": [chase_w, defend_w]
        })
        fig_cd = px.bar(
            cd_df, x="Type", y="Count", color="Type",
            color_discrete_map={
                "Chasing Wins":"#3b82f6","Defending Wins":"#7c3aed"
            },
            title="Chasing vs Defending Wins"
        )
        fig_cd.update_traces(marker_line_width=0)
        apply_chart_theme(fig_cd, height=260)
        cr.plotly_chart(fig_cd, use_container_width=True, key="chase_defend")

    # ----------------------------------------------------------------
    # SECTION 5 — TEAM COMPARISON
    # ----------------------------------------------------------------
    section_header("Team Comparison", "#3b82f6")
    st.caption(
        f"Overall performance · Seasons {season_range[0]}–{season_range[1]} · Not direct H2H"
    )

    df_comp_base = df[
        (df["season"] >= season_range[0]) &
        (df["season"] <= season_range[1])
    ]

    colA, colB = st.columns(2)
    teamA = colA.selectbox("Team A", teams, index=0, key="comp_a")
    teamB = colB.selectbox(
        "Team B", teams,
        index=1 if len(teams) > 1 else 0,
        key="comp_b"
    )

    df_A      = df_comp_base[df_comp_base["team"] == teamA]
    df_B      = df_comp_base[df_comp_base["team"] == teamB]
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
    <div style="background:#0d0d20;border:1px solid #1e1e3a;
                border-top:3px solid {color_A};border-radius:10px;
                padding:20px 22px;">
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:18px;font-weight:800;color:#e8e8ff;
                    margin-bottom:8px;">{teamA}</div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:38px;font-weight:800;color:{color_A};
                    line-height:1;">{wins_A}</div>
        <div style="font-size:11px;color:#5a5a8a;margin-top:4px;
                    text-transform:uppercase;letter-spacing:0.08em;">Wins</div>
        <div style="font-size:13px;color:#94a3b8;margin-top:10px;">
            {wpct_A:.1f}% win rate · {matches_A} matches
        </div>
    </div>
    """, unsafe_allow_html=True)

    card_mid.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;
                height:100%;padding-top:36px;font-family:'Barlow Condensed',sans-serif;
                font-size:16px;font-weight:800;color:#3a3a6a;letter-spacing:0.1em;">
        VS
    </div>
    """, unsafe_allow_html=True)

    card_r.markdown(f"""
    <div style="background:#0d0d20;border:1px solid #1e1e3a;
                border-top:3px solid {color_B};border-radius:10px;
                padding:20px 22px;">
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:18px;font-weight:800;color:#e8e8ff;
                    margin-bottom:8px;">{teamB}</div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:38px;font-weight:800;color:{color_B};
                    line-height:1;">{wins_B}</div>
        <div style="font-size:11px;color:#5a5a8a;margin-top:4px;
                    text-transform:uppercase;letter-spacing:0.08em;">Wins</div>
        <div style="font-size:13px;color:#94a3b8;margin-top:10px;">
            {wpct_B:.1f}% win rate · {matches_B} matches
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:10px;text-transform:uppercase;letter-spacing:0.1em;"
        "color:#3a3a6a;margin-bottom:6px;'>Win share</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style="display:flex;height:12px;border-radius:6px;overflow:hidden;">
        <div style="width:{pct_A_bar*100:.1f}%;background:{color_A};"></div>
        <div style="width:{(1-pct_A_bar)*100:.1f}%;background:{color_B};"></div>
    </div>
    <div style="display:flex;justify-content:space-between;
                font-size:12px;margin-top:6px;">
        <span style="color:{color_A};">{teamA} · {pct_A_bar*100:.0f}%</span>
        <span style="color:{color_B};">{teamB} · {(1-pct_A_bar)*100:.0f}%</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()