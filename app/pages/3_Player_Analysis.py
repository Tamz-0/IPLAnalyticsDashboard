import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.charts import apply_theme

st.set_page_config(layout="wide", page_title="Player Analysis | IPL Dashboard")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
.stApp { background: #080810; }

section[data-testid="stSidebar"] {
    background: #0d0d1a !important;
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
[data-testid="stExpander"] {
    background: #0d0d20 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 10px !important;
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

# ----------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------
def apply_chart_theme(fig, height=360):
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
                color:#e8e8ff;margin:24px 0 14px;padding-left:10px;
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

# ----------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    bat_path = os.path.join(BASE_DIR, "data", "processed", "player_batting.csv")
    bowl_path = os.path.join(BASE_DIR, "data", "processed", "player_bowler.csv")

    bat = pd.read_csv(bat_path)
    bowl = pd.read_csv(bowl_path)

    return bat, bowl

# ================================================================
# MAIN
# ================================================================
def main():
    bat_df, bowl_df = load_data()

    all_batters  = sorted(bat_df["batter"].unique())
    all_bowlers  = sorted(bowl_df["bowler"].unique())
    all_rounders = sorted(
        set(bat_df["batter"].unique()) & set(bowl_df["bowler"].unique())
    )

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
            Player Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    sidebar_label("Role")
    role = st.sidebar.radio(
        "Role", ["Batter", "Bowler", "All-rounder"],
        label_visibility="collapsed"
    )

    if role == "Batter":
        player_list = all_batters
    elif role == "Bowler":
        player_list = all_bowlers
    else:
        player_list = all_rounders

    sidebar_label("Search Player")
    search = st.sidebar.text_input(
        "Search Player", placeholder="e.g. Kohli, Rohit...",
        label_visibility="collapsed"
    )

    filtered = [p for p in player_list if search.lower() in p.lower()] \
               if search else player_list

    if not filtered:
        st.sidebar.warning("No players match your search.")
        st.stop()

    sidebar_label("Select Player")
    player = st.sidebar.selectbox(
        "Select Player", filtered,
        label_visibility="collapsed"
    )

    sidebar_label("Season Range")
    s_min = int(min(bat_df["season"].min(), bowl_df["season"].min()))
    s_max = int(max(bat_df["season"].max(), bowl_df["season"].max()))
    season_range = st.sidebar.slider(
        "Season Range", s_min, s_max, (s_min, s_max),
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    career_view = st.sidebar.toggle("Career View", value=False)
    st.sidebar.caption("Aggregates all seasons into career totals")

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<p style='font-size:11px;color:#2a2a4a;text-align:center;"
        "letter-spacing:0.06em;'>DATA · IPL 2008–2025</p>",
        unsafe_allow_html=True
    )

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

    # ----------------------------------------------------------------
    # CAREER VIEW — collapse to single row
    # ----------------------------------------------------------------
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

    # ----------------------------------------------------------------
    # PROFILE CARD
    # ----------------------------------------------------------------
    initials     = "".join([x[0] for x in player.split()[:2]]).upper()
    display_role = role
    accent_color = "#7c3aed" if role != "Bowler" else "#f59e0b"

    st.markdown(f"""
    <div style="background:#0d0d20;padding:24px 28px;
                border-left:4px solid {accent_color};
                border:1px solid #1e1e3a;border-left:4px solid {accent_color};
                border-radius:12px;display:flex;align-items:center;
                gap:20px;margin-bottom:24px;">
        <div style="width:72px;height:72px;border-radius:50%;
                    background:{accent_color}22;
                    border:2px solid {accent_color};
                    color:{accent_color};
                    display:flex;align-items:center;justify-content:center;
                    font-family:'Barlow Condensed',sans-serif;
                    font-size:26px;font-weight:800;flex-shrink:0;">
            {initials}
        </div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:32px;font-weight:800;color:#e8e8ff;
                        letter-spacing:0.04em;line-height:1.1;">
                {player}
            </div>
            <div style="font-size:12px;color:#5a5a8a;text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:4px;">
                {display_role}
                {"· Seasons " + str(season_range[0]) + "–" + str(season_range[1])
                 if not career_view else "· Career View"}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ================================================================
    # BATTER SECTION
    # ================================================================
    if has_bat and role in ["Batter", "All-rounder"]:
        section_header("Batting Stats", "#7c3aed")

        total_runs = int(bat["runs_batter"].sum())
        avg        = float(bat["batting_average"].mean())
        sr         = float(bat["strike_rate"].mean())
        fours      = int(bat["is_four"].sum())
        sixes      = int(bat["is_six"].sum())
        seasons_p  = bat["season"].nunique() if not career_view else "All"

        bat_stats = [
            ("Runs",    str(total_runs),    "#e8e8ff",  "#7c3aed"),
            ("Average", f"{avg:.1f}",       "#3b82f6",  "#7c3aed"),
            ("SR",      f"{sr:.1f}",        "#22c55e",  "#7c3aed"),
            ("4s",      str(fours),         "#e8e8ff",  "#7c3aed"),
            ("6s",      str(sixes),         "#f59e0b",  "#7c3aed"),
            ("Seasons", str(seasons_p),     "#94a3b8",  "#7c3aed"),
        ]
        cols = st.columns(6)
        for col, (label, val, color, top) in zip(cols, bat_stats):
            stat_card(col, label, val, color, top)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Main trend chart
        if not career_view:
            bat_plot = bat.groupby("season").agg(
                runs=("runs_batter", "sum"),
                avg=("batting_average", "mean"),
                sr=("strike_rate", "mean")
            ).reset_index()

            fig_bat = go.Figure()
            fig_bat.add_trace(go.Scatter(
                x=bat_plot["season"].tolist(),
                y=bat_plot["runs"].tolist(),
                mode="lines+markers",
                name="Runs",
                line=dict(color="#7c3aed", width=3),
                marker=dict(size=8, color="#7c3aed",
                            line=dict(color="#080810", width=2)),
                hovertemplate="<b>%{x}</b><br>Runs: %{y}<extra></extra>"
            ))
            apply_chart_theme(fig_bat, height=340)
            fig_bat.update_layout(title="Runs per Season")
            st.plotly_chart(fig_bat, use_container_width=True, key="bat_trend")

        # Deep stats expander
        with st.expander("Show detailed batting breakdown"):
            if not career_view:
                c1, c2, c3 = st.columns(3)

                fig_sr = px.bar(bat, x="season", y="strike_rate",
                                title="Strike Rate per Season",
                                color_discrete_sequence=["#3b82f6"])
                fig_sr.update_traces(marker_line_width=0)
                apply_chart_theme(fig_sr, height=280)
                c1.plotly_chart(fig_sr, use_container_width=True, key="bat_sr")

                fours_sixes = bat.groupby("season")[
                    ["is_four", "is_six"]
                ].sum().reset_index()
                fig_fs = px.bar(
                    fours_sixes, x="season",
                    y=["is_four", "is_six"],
                    barmode="group",
                    title="4s and 6s per Season",
                    color_discrete_map={"is_four": "#22c55e", "is_six": "#f59e0b"}
                )
                fig_fs.update_traces(marker_line_width=0)
                apply_chart_theme(fig_fs, height=280)
                c2.plotly_chart(fig_fs, use_container_width=True, key="bat_fs")

                fig_avg = px.bar(bat, x="season", y="batting_average",
                                 title="Batting Average per Season",
                                 color_discrete_sequence=["#7c3aed"])
                fig_avg.update_traces(marker_line_width=0)
                apply_chart_theme(fig_avg, height=280)
                c3.plotly_chart(fig_avg, use_container_width=True, key="bat_avg")

            # Clean table
            bat_table = bat[[
                "season", "runs_batter", "balls_faced",
                "batting_average", "strike_rate", "is_four", "is_six"
            ]].copy()
            bat_table.columns = [
                "Season", "Runs", "Balls", "Average", "SR", "4s", "6s"
            ]
            bat_table["Average"] = bat_table["Average"].round(2)
            bat_table["SR"]      = bat_table["SR"].round(1)
            st.dataframe(
                bat_table, use_container_width=True, hide_index=True
            )

    # ================================================================
    # BOWLER SECTION
    # ================================================================
    if has_bowl and role in ["Bowler", "All-rounder"]:
        section_header("Bowling Stats", "#f59e0b")

        wickets   = int(bowl["bowler_wicket"].sum())
        avg_bowl  = float(bowl["bowling_average"].mean())
        eco       = float(bowl["economy"].mean())
        sr_bowl   = float(bowl["strike_rate"].mean())
        overs     = float(bowl["overs"].sum())
        seasons_b = bowl["season"].nunique() if not career_view else "All"

        bowl_stats = [
            ("Wickets", str(wickets),       "#f59e0b",  "#f59e0b"),
            ("Average", f"{avg_bowl:.1f}",  "#ef4444",  "#f59e0b"),
            ("Economy", f"{eco:.2f}",       "#3b82f6",  "#f59e0b"),
            ("SR",      f"{sr_bowl:.1f}",   "#22c55e",  "#f59e0b"),
            ("Overs",   f"{overs:.1f}",     "#e8e8ff",  "#f59e0b"),
            ("Seasons", str(seasons_b),     "#94a3b8",  "#f59e0b"),
        ]
        cols = st.columns(6)
        for col, (label, val, color, top) in zip(cols, bowl_stats):
            stat_card(col, label, val, color, top)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Main trend chart
        if not career_view:
            bowl_plot = bowl.groupby("season").agg(
                wickets=("bowler_wicket", "sum"),
                economy=("economy", "mean")
            ).reset_index()

            fig_bowl = go.Figure()
            fig_bowl.add_trace(go.Scatter(
                x=bowl_plot["season"].tolist(),
                y=bowl_plot["wickets"].tolist(),
                mode="lines+markers",
                name="Wickets",
                line=dict(color="#f59e0b", width=3),
                marker=dict(size=8, color="#f59e0b",
                            line=dict(color="#080810", width=2)),
                hovertemplate="<b>%{x}</b><br>Wickets: %{y}<extra></extra>"
            ))
            apply_chart_theme(fig_bowl, height=340)
            fig_bowl.update_layout(title="Wickets per Season")
            st.plotly_chart(fig_bowl, use_container_width=True, key="bowl_trend")

        # Deep stats expander
        with st.expander("Show detailed bowling breakdown"):
            if not career_view:
                c1, c2, c3 = st.columns(3)

                fig_eco = px.bar(bowl, x="season", y="economy",
                                 title="Economy per Season",
                                 color_discrete_sequence=["#ef4444"])
                fig_eco.update_traces(marker_line_width=0)
                apply_chart_theme(fig_eco, height=280)
                c1.plotly_chart(fig_eco, use_container_width=True, key="bowl_eco")

                fig_wk = px.bar(bowl, x="season", y="bowler_wicket",
                                title="Wickets per Season",
                                color_discrete_sequence=["#f59e0b"])
                fig_wk.update_traces(marker_line_width=0)
                apply_chart_theme(fig_wk, height=280)
                c2.plotly_chart(fig_wk, use_container_width=True, key="bowl_wk")

                fig_bsr = px.bar(bowl, x="season", y="strike_rate",
                                 title="Bowling SR per Season",
                                 color_discrete_sequence=["#7c3aed"])
                fig_bsr.update_traces(marker_line_width=0)
                apply_chart_theme(fig_bsr, height=280)
                c3.plotly_chart(fig_bsr, use_container_width=True, key="bowl_sr")

            bowl_table = bowl[[
                "season", "bowler_wicket", "overs",
                "economy", "bowling_average", "strike_rate"
            ]].copy()
            bowl_table.columns = [
                "Season", "Wickets", "Overs", "Economy", "Average", "SR"
            ]
            bowl_table["Overs"]   = bowl_table["Overs"].round(1)
            bowl_table["Economy"] = bowl_table["Economy"].round(2)
            bowl_table["Average"] = bowl_table["Average"].round(2)
            bowl_table["SR"]      = bowl_table["SR"].round(1)
            st.dataframe(
                bowl_table, use_container_width=True, hide_index=True
            )


if __name__ == "__main__":
    main()