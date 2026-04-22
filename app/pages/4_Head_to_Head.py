import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import os


# ----------------------------------------------------------
# LOAD FUNCTION
# ----------------------------------------------------------
@st.cache_data
def load():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    m = pd.read_csv(os.path.join(BASE_DIR, "data/processed/h2h_matches.csv"))
    p = pd.read_csv(os.path.join(BASE_DIR, "data/processed/h2hplayer_stats.csv"))
    return m, p


# ----------------------------------------------------------
# MAIN APP
# ----------------------------------------------------------
def main():
    st.set_page_config(layout="wide", page_title="Head to Head | IPL Dashboard")

    # ----------------------------------------------------------
    # STYLES
    # ----------------------------------------------------------
    st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }
    .stApp { background: #080810; }
    
    .card {
        background:#0d0d20;
        border:1px solid #1e1e3a;
        border-radius:12px;
        padding:18px 20px;
    }

    .stat {
        font-family:'Barlow Condensed',sans-serif;
        font-size:28px;
        font-weight:800;
        color:#e8e8ff;
    }

    .label {
        font-size:11px;
        text-transform:uppercase;
        color:#5a5a8a;
        letter-spacing:0.08em;
    }
    </style>
    """, unsafe_allow_html=True)

    matches, players = load()

    teams = sorted(set(matches["team1"]).union(set(matches["team2"])))

    # ----------------------------------------------------------
    # HEADER
    # ----------------------------------------------------------
    st.markdown("""
    <div style="font-family:'Barlow Condensed',sans-serif;
    font-size:28px;font-weight:800;color:#e8e8ff;
    letter-spacing:0.06em;margin-bottom:20px;">
    HEAD TO HEAD ANALYSIS
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # SELECTORS (DEFAULT RCB vs CSK)
    # ----------------------------------------------------------
    c1, c2 = st.columns(2)

    default_team1 = "Royal Challengers Bengaluru"
    default_team2 = "Chennai Super Kings"

    team1 = c1.selectbox("Team 1", teams, index=teams.index(default_team1) if default_team1 in teams else 0)
    team2 = c2.selectbox("Team 2", teams, index=teams.index(default_team2) if default_team2 in teams else 1)

    if team1 == team2:
        st.stop()

 # ----------------------------------------------------------
# FILTER
# ----------------------------------------------------------
    h2h = matches[
        ((matches["team1"] == team1) & (matches["team2"] == team2)) |
        ((matches["team1"] == team2) & (matches["team2"] == team1))
    ].copy()

    if h2h.empty:
        st.warning("No matches found")
        st.stop()

# ----------------------------------------------------------
# 🔥 FIX: REMOVE DUPLICATES (VERY IMPORTANT)
# ----------------------------------------------------------
    h2h = h2h.drop_duplicates(subset="match_id")

# ----------------------------------------------------------
# 🔥 NORMALIZE MATCHUP (PUT YOUR CODE HERE)
# ----------------------------------------------------------
    h2h['teamA'] = h2h[['team1','team2']].min(axis=1)
    h2h['teamB'] = h2h[['team1','team2']].max(axis=1)

# ----------------------------------------------------------
# STATS
# ----------------------------------------------------------
    # normalize pair
    h2h['teamA'] = h2h[['team1','team2']].min(axis=1)
    h2h['teamB'] = h2h[['team1','team2']].max(axis=1)

# determine which is A/B for selected teams
    teamA = min(team1, team2)
    teamB = max(team1, team2)

# filter correctly
    h2h_pair = h2h[
        (h2h['teamA'] == teamA) &
        (h2h['teamB'] == teamB)
    ]

    total = len(h2h_pair)

    wins_A = (h2h_pair['winner'] == teamA).sum()
    wins_B = (h2h_pair['winner'] == teamB).sum()

# map back to UI order
    if team1 == teamA:
        w1, w2 = wins_A, wins_B
    else:
        w1, w2 = wins_B, wins_A
    # ----------------------------------------------------------
    # RIVALRY BANNER
    # ----------------------------------------------------------
    st.markdown(f"""
    <div class="card" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
        <div>
            <div class="label">Rivalry</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:32px;font-weight:800;">
                {team1} vs {team2}
            </div>
        </div>
        <div class="stat">{w1} - {w2}</div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # STAT CARDS
    # ----------------------------------------------------------
    c1, c2, c3 = st.columns(3)

    def stat_card(col, label, value):
        col.markdown(f"""
        <div class="card">
            <div class="label">{label}</div>
            <div class="stat">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    stat_card(c1, "Total Matches", total)
    stat_card(c2, f"{team1} Wins", w1)
    stat_card(c3, f"{team2} Wins", w2)

    # ----------------------------------------------------------
    # CHART
    # ----------------------------------------------------------
    fig = go.Figure(go.Bar(
        x=[team1, team2],
        y=[w1, w2],
        text=[w1, w2],
        textposition="outside"
    ))

    fig.update_layout(
        plot_bgcolor="#0d0d20",
        paper_bgcolor="#0d0d20",
        font=dict(color="#e8e8ff"),
        title="Win Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------------
    # TOP PLAYERS
    # ----------------------------------------------------------
    st.markdown("### Top Performers")

    bat = players[
        (players["player_team"].isin([team1, team2]))
    ]

    top_bat = bat.groupby("player")["runs_batter"].sum().sort_values(ascending=False).head(5)

    def leaderboard(title, data, unit):
        rows = ""
        for i, (name, val) in enumerate(data.items(), 1):
            rows += f"""
            <div style="display:flex;justify-content:space-between;
                        padding:10px 0;border-bottom:1px solid #1e1e3a;">
                <span style="color:#e8e8ff;">{i}. {name}</span>
                <span style="color:#e8e8ff;">{int(val)} {unit}</span>
            </div>
            """

        return f"""
        <div style="background:#0d0d20;padding:16px;border-radius:12px;border:1px solid #1e1e3a;">
            <div style="color:#5a5a8a;margin-bottom:10px;">{title}</div>
            {rows}
        </div>
        """

    st.components.v1.html(leaderboard("Top Batters", top_bat, "runs"), height=300)

    # ----------------------------------------------------------
    # MATCH HISTORY
    # ----------------------------------------------------------
    st.markdown("### Match History")

    st.dataframe(
        h2h.sort_values("season", ascending=False)[
            ["season","team1","team2","winner","venue"]
        ],
        use_container_width=True
    )


# ----------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------
if __name__ == "__main__":
    main()