import streamlit as st
import pandas as pd
import os


# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------
@st.cache_data
def load():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    bat  = pd.read_csv(os.path.join(BASE_DIR, "data/processed/player_batting.csv"))
    bowl = pd.read_csv(os.path.join(BASE_DIR, "data/processed/player_bowler.csv"))
    pvt  = pd.read_csv(os.path.join(BASE_DIR, "data/processed/player_vs_team.csv"))
    bvt  = pd.read_csv(os.path.join(BASE_DIR, "data/processed/bowler_vs_team.csv"))
    pvp  = pd.read_csv(os.path.join(BASE_DIR, "data/processed/player_vs_player.csv"))
    return bat, bowl, pvt, bvt, pvp


# ----------------------------------------------------------
# STYLES
# ----------------------------------------------------------
def inject_styles():
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top, #0b0b1f, #050510);
    }
    .page-title {
        font-size: 36px;
        font-weight: 900;
        color: white;
        letter-spacing: 2px;
        margin-bottom: 4px;
    }
    .page-subtitle {
        color: #8a8ab5;
        font-size: 14px;
        margin-bottom: 28px;
    }
    .vs-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0d0d20;
        padding: 28px 32px;
        border-radius: 16px;
        margin-bottom: 28px;
        border: 1px solid #1e1e3a;
    }
    .player-block {
        text-align: center;
        flex: 1;
    }
    .crown {
        font-size: 20px;
        margin-bottom: 4px;
        min-height: 28px;
    }
    .player-name {
        font-size: 22px;
        font-weight: 800;
        color: white;
    }
    .player-name.p1-leading {
        color: #00f2fe;
        text-shadow: 0 0 16px rgba(0, 242, 254, 0.7);
    }
    .player-name.p2-leading {
        color: #ff7eb3;
        text-shadow: 0 0 16px rgba(255, 126, 179, 0.7);
    }
    .player-role {
        font-size: 12px;
        color: #666;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .vs-divider {
        font-size: 22px;
        font-weight: 900;
        color: #333;
        padding: 0 24px;
    }
    .section-heading {
        font-size: 13px;
        font-weight: 700;
        color: #8a8ab5;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 20px;
        margin-top: 4px;
    }
    .stat-block {
        margin-bottom: 22px;
    }
    .stat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .stat-label {
        color: #666;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .stat-winner-tag {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 2px 10px;
        border-radius: 20px;
        text-transform: uppercase;
    }
    .tag-p1 {
        background: rgba(0, 242, 254, 0.12);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.3);
    }
    .tag-p2 {
        background: rgba(255, 126, 179, 0.12);
        color: #ff7eb3;
        border: 1px solid rgba(255, 126, 179, 0.3);
    }
    .tag-tie {
        background: rgba(255,255,255,0.05);
        color: #555;
        border: 1px solid #333;
    }
    .stat-row-wrap {
        display: flex;
        gap: 14px;
        align-items: center;
    }
    .stat-side {
        flex: 1;
    }
    .side-name {
        font-size: 10px;
        color: #555;
        margin-bottom: 4px;
    }
    .bar-track {
        height: 8px;
        border-radius: 20px;
        background: #1c1c3a;
        overflow: hidden;
        margin-bottom: 5px;
    }
    .bar-p1 {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #4facfe, #00f2fe);
    }
    .bar-p2 {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #ff758c, #ff7eb3);
    }
    .stat-value {
        font-size: 14px;
        font-weight: 700;
        color: #aaa;
    }
    .stat-value.v-p1-win { color: #00f2fe; }
    .stat-value.v-p2-win { color: #ff7eb3; }
    .stat-sep {
        color: #222;
        font-size: 12px;
        font-weight: 700;
        padding: 0 2px;
        flex-shrink: 0;
    }
    .stat-card-value {
        font-size: 28px;
        font-weight: 900;
        margin-top: 4px;
    }
    .stat-card-underline {
        height: 3px;
        border-radius: 2px;
        margin-top: 8px;
    }
    .no-data {
        background: #0d0d20;
        border: 1px solid #1e1e3a;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        color: #555;
        font-size: 14px;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------
def get_batting_stats(player, bat):
    b = bat[bat["batter"] == player].sum(numeric_only=True)
    runs   = int(b.get("runs_batter", 0))
    balls  = int(b.get("balls_faced", 0))
    wkts   = int(b.get("is_wicket", 0))
    fours  = int(b.get("is_four", 0))
    sixes  = int(b.get("is_six", 0))
    sr     = round(runs / balls * 100, 1) if balls > 0 else 0.0
    avg    = round(runs / wkts, 1)        if wkts > 0  else 0.0
    return {"runs": runs, "balls": balls, "sr": sr,
            "average": avg, "fours": fours, "sixes": sixes}


def get_bowling_stats(player, bowl):
    b = bowl[bowl["bowler"] == player].sum(numeric_only=True)
    runs_c  = int(b.get("runs_bowler", 0))
    wickets = int(b.get("bowler_wicket", 0))
    balls   = int(b.get("ball_no", 0))
    overs   = round(balls / 6, 1)
    economy = round(runs_c / (balls / 6), 2) if balls > 0 else 0.0
    avg     = round(runs_c / wickets, 1)      if wickets > 0 else 0.0
    sr      = round(balls / wickets, 1)       if wickets > 0 else 0.0
    return {"runs_conceded": runs_c, "wickets": wickets,
            "overs": overs, "economy": economy, "average": avg, "sr": sr}


def get_role(player, bat, bowl):
    is_bat  = player in bat["batter"].values
    is_bowl = player in bowl["bowler"].values
    if is_bat and is_bowl:
        return "All-Rounder"
    elif is_bat:
        return "Batter"
    return "Bowler"


def determine_winner(v1, v2, invert=False):
    if v1 == v2:
        return "tie"
    if invert:
        if v1 == 0: return "p2"
        if v2 == 0: return "p1"
        return "p1" if v1 < v2 else "p2"
    return "p1" if v1 > v2 else "p2"


def overall_winner(results):
    p1 = results.count("p1")
    p2 = results.count("p2")
    if p1 > p2:   return "p1"
    elif p2 > p1: return "p2"
    return "tie"


def stat_compare(label, v1, v2, name1, name2, invert=False):
    max_v  = max(v1, v2, 0.01)
    p1_pct = int((v1 / max_v) * 100)
    p2_pct = int((v2 / max_v) * 100)
    winner = determine_winner(v1, v2, invert)

    val1_cls = "stat-value v-p1-win" if winner == "p1" else "stat-value"
    val2_cls = "stat-value v-p2-win" if winner == "p2" else "stat-value"

    if winner == "p1":
        tag_html = f'<span class="stat-winner-tag tag-p1">{name1} wins</span>'
    elif winner == "p2":
        tag_html = f'<span class="stat-winner-tag tag-p2">{name2} wins</span>'
    else:
        tag_html = '<span class="stat-winner-tag tag-tie">Tie</span>'

    st.markdown(f"""
    <div class="stat-block">
        <div class="stat-header">
            <span class="stat-label">{label}</span>
            {tag_html}
        </div>
        <div class="stat-row-wrap">
            <div class="stat-side">
                <div class="side-name">{name1}</div>
                <div class="bar-track"><div class="bar-p1" style="width:{p1_pct}%"></div></div>
                <div class="{val1_cls}">{v1}</div>
            </div>
            <div class="stat-sep">|</div>
            <div class="stat-side">
                <div class="side-name">{name2}</div>
                <div class="bar-track"><div class="bar-p2" style="width:{p2_pct}%"></div></div>
                <div class="{val2_cls}">{v2}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return winner


def render_vs_box(name1, role1, name2, role2, ow):
    crown1     = "&#x1F451;" if ow == "p1" else "&nbsp;"
    crown2     = "&#x1F451;" if ow == "p2" else "&nbsp;"
    name1_cls  = "player-name p1-leading" if ow == "p1" else "player-name"
    name2_cls  = "player-name p2-leading" if ow == "p2" else "player-name"
    st.markdown(f"""
    <div class="vs-box">
        <div class="player-block">
            <div class="crown">{crown1}</div>
            <div class="{name1_cls}">{name1}</div>
            <div class="player-role">{role1}</div>
        </div>
        <div class="vs-divider">VS</div>
        <div class="player-block">
            <div class="crown">{crown2}</div>
            <div class="{name2_cls}">{name2}</div>
            <div class="player-role">{role2}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------
# PAGE 1 — PLAYER VS PLAYER (CAREER)
# ----------------------------------------------------------
def page_player_vs_player(bat, bowl, players):
    c1, c2 = st.columns(2)
    p1 = c1.selectbox("Player 1", players,
                      index=players.index("V Kohli") if "V Kohli" in players else 0, key="pvp_p1")
    p2 = c2.selectbox("Player 2", players,
                      index=players.index("MS Dhoni") if "MS Dhoni" in players else 1, key="pvp_p2")

    s1 = get_batting_stats(p1, bat)
    s2 = get_batting_stats(p2, bat)
    b1 = get_bowling_stats(p1, bowl)
    b2 = get_bowling_stats(p2, bowl)

    results = [
        determine_winner(s1["runs"],    s2["runs"]),
        determine_winner(s1["sr"],      s2["sr"]),
        determine_winner(s1["average"], s2["average"]),
        determine_winner(b1["wickets"], b2["wickets"]),
        determine_winner(b1["economy"], b2["economy"], invert=True),
    ]
    ow = overall_winner(results)

    render_vs_box(p1, get_role(p1, bat, bowl),
                  p2, get_role(p2, bat, bowl), ow)

    st.markdown('<div class="section-heading">Batting</div>', unsafe_allow_html=True)
    stat_compare("Runs",        s1["runs"],    s2["runs"],    p1, p2)
    stat_compare("Strike Rate", s1["sr"],      s2["sr"],      p1, p2)
    stat_compare("Average",     s1["average"], s2["average"], p1, p2)
    stat_compare("Fours",       s1["fours"],   s2["fours"],   p1, p2)
    stat_compare("Sixes",       s1["sixes"],   s2["sixes"],   p1, p2)

    st.markdown('<div class="section-heading">Bowling</div>', unsafe_allow_html=True)
    stat_compare("Wickets",     b1["wickets"], b2["wickets"], p1, p2)
    stat_compare("Economy",     b1["economy"], b2["economy"], p1, p2, invert=True)
    stat_compare("Average",     b1["average"], b2["average"], p1, p2, invert=True)
    stat_compare("Strike Rate", b1["sr"],      b2["sr"],      p1, p2, invert=True)


# ----------------------------------------------------------
# PAGE 2 — PLAYER VS TEAM
# ----------------------------------------------------------
def page_player_vs_team(bat, bowl, pvt, bvt, players, teams):
    role_choice = st.radio("Role", ["Batter", "Bowler"], horizontal=True)

    if role_choice == "Batter":
        batters = sorted(pvt["batter"].unique())
        c1, c2  = st.columns(2)
        player  = c1.selectbox("Batter", batters,
                               index=batters.index("V Kohli") if "V Kohli" in batters else 0, key="pvt_batter")
        team    = c2.selectbox("Bowling Team", teams, key="pvt_bowl_team")

        data = pvt[(pvt["batter"] == player) & (pvt["bowling_team"] == team)]

        if not data.empty:
            d          = data.iloc[0]
            runs       = int(d["runs"])
            balls      = int(d["balls"])
            dismissals = int(d["dismissals"])
            fours      = int(d["fours"])
            sixes      = int(d["sixes"])
            sr         = round(float(d["strike_rate"]), 1)
            average    = round(runs / dismissals, 1) if dismissals > 0 else round(float(d["average"]), 1)

            st.markdown(f"""
            <div class="vs-box">
                <div class="player-block">
                    <div class="crown">&nbsp;</div>
                    <div class="player-name p1-leading">{player}</div>
                    <div class="player-role">Batter</div>
                </div>
                <div class="vs-divider">VS</div>
                <div class="player-block">
                    <div class="crown">&nbsp;</div>
                    <div class="player-name p2-leading">{team}</div>
                    <div class="player-role">Bowling Team</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-heading">Head to Head</div>',
                        unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            def stat_card(col, label, value, color, grad):
                col.markdown(f"""
                <div class="stat-block">
                    <div class="stat-label">{label}</div>
                    <div class="stat-card-value" style="color:{color};
                         text-shadow:0 0 12px {color}55;">{value}</div>
                    <div class="stat-card-underline"
                         style="background:linear-gradient(90deg,{grad},transparent);">
                    </div>
                </div>
                """, unsafe_allow_html=True)

            stat_card(col1, "Runs",        runs,       "#00f2fe", "#4facfe,#00f2fe")
            stat_card(col2, "Strike Rate", sr,         "#00f2fe", "#4facfe,#00f2fe")
            stat_card(col3, "Average",     average,    "#00f2fe", "#4facfe,#00f2fe")
            stat_card(col1, "Fours",       fours,      "#a78bfa", "#7c3aed,#a78bfa")
            stat_card(col2, "Sixes",       sixes,      "#a78bfa", "#7c3aed,#a78bfa")
            stat_card(col3, "Dismissals",  dismissals, "#ff7eb3", "#ff758c,#ff7eb3")
        else:
            st.markdown(
                f'<div class="no-data">No data found for {player} vs {team}</div>',
                unsafe_allow_html=True)

    else:
        bowlers = sorted(bvt["bowler"].unique())
        c1, c2  = st.columns(2)
        player  = c1.selectbox("Bowler", bowlers, index=bowlers.index("JJ Bumrah") if "JJ Bumrah" in bowlers else 0, key="pvt_bowler")
        team    = c2.selectbox("Batting Team", teams, key="pvt_bat_team")

        data = bvt[(bvt["bowler"] == player) & (bvt["batting_team"] == team)]

        if not data.empty:
            d            = data.iloc[0]
            runs_c       = int(d["runs_conceded"])
            wickets      = int(d["wickets"])
            balls        = int(d["balls"])
            overs        = round(float(d["overs"]), 1)
            economy      = round(float(d["economy"]), 2)
            average      = round(runs_c / wickets, 1) if wickets > 0 else 0.0
            sr           = round(balls / wickets, 1)  if wickets > 0 else 0.0

            st.markdown(f"""
            <div class="vs-box">
                <div class="player-block">
                    <div class="crown">&nbsp;</div>
                    <div class="player-name p1-leading">{player}</div>
                    <div class="player-role">Bowler</div>
                </div>
                <div class="vs-divider">VS</div>
                <div class="player-block">
                    <div class="crown">&nbsp;</div>
                    <div class="player-name p2-leading">{team}</div>
                    <div class="player-role">Batting Team</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-heading">Head to Head</div>',
                        unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            def stat_card(col, label, value, color, grad):
                col.markdown(f"""
                <div class="stat-block">
                    <div class="stat-label">{label}</div>
                    <div class="stat-card-value" style="color:{color};
                         text-shadow:0 0 12px {color}55;">{value}</div>
                    <div class="stat-card-underline"
                         style="background:linear-gradient(90deg,{grad},transparent);">
                    </div>
                </div>
                """, unsafe_allow_html=True)

            stat_card(col1, "Wickets",       wickets, "#00f2fe", "#4facfe,#00f2fe")
            stat_card(col2, "Economy",       economy, "#00f2fe", "#4facfe,#00f2fe")
            stat_card(col3, "Overs Bowled",  overs,   "#00f2fe", "#4facfe,#00f2fe")
            stat_card(col1, "Runs Conceded", runs_c,  "#ff7eb3", "#ff758c,#ff7eb3")
            stat_card(col2, "Average",       average, "#a78bfa", "#7c3aed,#a78bfa")
            stat_card(col3, "Strike Rate",   sr,      "#a78bfa", "#7c3aed,#a78bfa")
        else:
            st.markdown(
                f'<div class="no-data">No data found for {player} vs {team}</div>',
                unsafe_allow_html=True)


# ----------------------------------------------------------
# PAGE 3 — BATTER VS BOWLER
# ----------------------------------------------------------
def page_batter_vs_bowler(pvp):
    batters = sorted(pvp["batter"].unique())
    bowlers = sorted(pvp["bowler"].unique())

    c1, c2  = st.columns(2)
    batter  = c1.selectbox("Batter", batters,
                           index=batters.index("V Kohli") if "V Kohli" in batters else 0,
                           key="bvb_batter")
    bowler  = c2.selectbox("Bowler", bowlers, index=bowlers.index("JJ Bumrah") if "JJ Bumrah" in bowlers else 0, key="pvt_bowler")

    data = pvp[(pvp["batter"] == batter) & (pvp["bowler"] == bowler)]

    if not data.empty:
        d          = data.iloc[0]
        runs       = int(d["runs"])
        balls      = int(d["balls"])
        dismissals = int(d["dismissals"])
        sr         = round(float(d["strike_rate"]), 1)
        average    = round(runs / dismissals, 1) if dismissals > 0 else round(float(d["average"]), 1)
        dot_balls  = balls - runs  # proxy: balls where batter scored 0

        # who has edge: batter wins if sr > 130 and dismissals < 3, else bowler
        batter_score = (sr / 100) + (runs / 50)
        bowler_score = (dismissals * 10) + max(0, (130 - sr))
        ow = "p1" if batter_score > bowler_score else "p2"

        render_vs_box(batter, "Batter", bowler, "Bowler", ow)

        st.markdown('<div class="section-heading">Head to Head</div>',
                    unsafe_allow_html=True)

        results = [
            determine_winner(runs,       0),
            determine_winner(sr,         130),
            determine_winner(0,          dismissals, invert=False),
        ]

        col1, col2, col3 = st.columns(3)

        def stat_card(col, label, value, color, grad):
            col.markdown(f"""
            <div class="stat-block">
                <div class="stat-label">{label}</div>
                <div class="stat-card-value" style="color:{color};
                     text-shadow:0 0 12px {color}55;">{value}</div>
                <div class="stat-card-underline"
                     style="background:linear-gradient(90deg,{grad},transparent);">
                </div>
            </div>
            """, unsafe_allow_html=True)

        stat_card(col1, "Runs Scored",  runs,       "#00f2fe", "#4facfe,#00f2fe")
        stat_card(col2, "Balls Faced",  balls,      "#00f2fe", "#4facfe,#00f2fe")
        stat_card(col3, "Strike Rate",  sr,         "#00f2fe", "#4facfe,#00f2fe")
        stat_card(col1, "Dismissals",   dismissals, "#ff7eb3", "#ff758c,#ff7eb3")
        stat_card(col2, "Average",      average,    "#a78bfa", "#7c3aed,#a78bfa")
        stat_card(col3, "Dot Balls",    dot_balls,  "#ff7eb3", "#ff758c,#ff7eb3")

    else:
        st.markdown(
            f'<div class="no-data">No data found for {batter} vs {bowler}</div>',
            unsafe_allow_html=True)


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
def main():
    st.set_page_config(layout="wide", page_title="Player Analytics | IPL")

    bat, bowl, pvt, bvt, pvp = load()

    players = sorted(set(bat["batter"]).union(set(bowl["bowler"])))
    teams   = sorted(set(pvt["bowling_team"]).union(set(bvt["batting_team"])))

    inject_styles()

    st.markdown('<div class="page-title">PLAYER ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Head-to-head stats across players, teams, and matchups</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "Player vs Player",
        "Player vs Team",
        "Batter vs Bowler"
    ])

    with tab1:
        page_player_vs_player(bat, bowl, players)

    with tab2:
        page_player_vs_team(bat, bowl, pvt, bvt, players, teams)

    with tab3:
        page_batter_vs_bowler(pvp)


if __name__ == "__main__":
    main()