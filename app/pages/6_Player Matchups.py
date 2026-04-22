import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.components import (
    page_header,
    section_header,
    sidebar_footer,
    sidebar_header,
    spacer,
    stat_card,
)
from utils.theme import COLORS, inject_global_css

st.set_page_config(layout="wide", page_title="Player H2H | IPL Dashboard")
inject_global_css()


# ----------------------------------------------------------------
# DATA
# ----------------------------------------------------------------
@st.cache_data
def load():
    import pandas as pd
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bat  = pd.read_csv(os.path.join(base, "data", "processed", "player_batting.csv"))
    bowl = pd.read_csv(os.path.join(base, "data", "processed", "player_bowler.csv"))
    pvt  = pd.read_csv(os.path.join(base, "data", "processed", "player_vs_team.csv"))
    bvt  = pd.read_csv(os.path.join(base, "data", "processed", "bowler_vs_team.csv"))
    pvp  = pd.read_csv(os.path.join(base, "data", "processed", "player_vs_player.csv"))
    return bat, bowl, pvt, bvt, pvp


bat, bowl, pvt, bvt, pvp = load()

players = sorted(set(bat["batter"]).union(set(bowl["bowler"])))
teams   = sorted(set(pvt["bowling_team"]).union(set(bvt["batting_team"])))

start_year = int(bat["season"].min())
end_year   = int(bat["season"].max())

# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
sidebar_header("Player H2H")
sidebar_footer(start_year, end_year)


# ----------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------
def get_batting_stats(player):
    b      = bat[bat["batter"] == player].sum(numeric_only=True)
    runs   = int(b.get("runs_batter", 0))
    balls  = int(b.get("balls_faced", 0))
    wkts   = int(b.get("is_wicket", 0))
    fours  = int(b.get("is_four", 0))
    sixes  = int(b.get("is_six", 0))
    sr     = round(runs / balls * 100, 1) if balls > 0 else 0.0
    avg    = round(runs / wkts, 1)        if wkts > 0  else 0.0
    return {"runs": runs, "balls": balls, "sr": sr,
            "average": avg, "fours": fours, "sixes": sixes}


def get_bowling_stats(player):
    b       = bowl[bowl["bowler"] == player].sum(numeric_only=True)
    runs_c  = int(b.get("runs_bowler", 0))
    wickets = int(b.get("bowler_wicket", 0))
    balls   = int(b.get("ball_no", 0))
    overs   = round(balls / 6, 1)
    economy = round(runs_c / (balls / 6), 2) if balls > 0 else 0.0
    avg     = round(runs_c / wickets, 1)      if wickets > 0 else 0.0
    sr      = round(balls / wickets, 1)       if wickets > 0 else 0.0
    return {"runs_conceded": runs_c, "wickets": wickets,
            "overs": overs, "economy": economy, "average": avg, "sr": sr}


def get_role(player):
    is_bat  = player in bat["batter"].values
    is_bowl = player in bowl["bowler"].values
    if is_bat and is_bowl:
        return "All-Rounder"
    return "Batter" if is_bat else "Bowler"


def determine_winner(v1, v2, invert=False):
    if v1 == v2:
        return "tie"
    if invert:
        if v1 == 0:
            return "p2"
        if v2 == 0:
            return "p1"
        return "p1" if v1 < v2 else "p2"
    return "p1" if v1 > v2 else "p2"


def overall_winner(results):
    p1 = results.count("p1")
    p2 = results.count("p2")
    if p1 > p2:
        return "p1"
    if p2 > p1:
        return "p2"
    return "tie"


def player_vs_box(name1, role1, name2, role2, ow):
    c1_color = COLORS["accent"]  if ow == "p1" else COLORS["text_primary"]
    c2_color = COLORS["amber"]   if ow == "p2" else COLORS["text_primary"]
    crown1   = "&#x1F451;" if ow == "p1" else "&nbsp;"
    crown2   = "&#x1F451;" if ow == "p2" else "&nbsp;"
    st.markdown(f"""
    <div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
                border-radius:12px;padding:28px 32px;
                display:flex;justify-content:space-between;align-items:center;
                margin-bottom:24px;">
        <div style="text-align:center;flex:1;">
            <div style="font-size:20px;min-height:28px;">{crown1}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:24px;
                        font-weight:800;color:{c1_color};">{name1}</div>
            <div style="font-size:11px;color:{COLORS['text_dim']};text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:4px;">{role1}</div>
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:20px;
                    font-weight:800;color:{COLORS['text_faint']};
                    padding:0 24px;letter-spacing:0.1em;">VS</div>
        <div style="text-align:center;flex:1;">
            <div style="font-size:20px;min-height:28px;">{crown2}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:24px;
                        font-weight:800;color:{c2_color};">{name2}</div>
            <div style="font-size:11px;color:{COLORS['text_dim']};text-transform:uppercase;
                        letter-spacing:0.1em;margin-top:4px;">{role2}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def stat_compare(label, v1, v2, name1, name2, invert=False):
    winner  = determine_winner(v1, v2, invert)
    max_v   = max(v1, v2, 0.01)
    p1_pct  = int((v1 / max_v) * 100)
    p2_pct  = int((v2 / max_v) * 100)

    p1_color = COLORS["accent"] if winner == "p1" else COLORS["text_muted"]
    p2_color = COLORS["amber"]  if winner == "p2" else COLORS["text_muted"]

    if winner == "p1":
        tag = f'<span style="font-size:10px;font-weight:700;letter-spacing:1px;padding:2px 10px;border-radius:20px;text-transform:uppercase;background:{COLORS["accent"]}22;color:{COLORS["accent"]};border:1px solid {COLORS["accent"]}55;">{name1} wins</span>'
    elif winner == "p2":
        tag = f'<span style="font-size:10px;font-weight:700;letter-spacing:1px;padding:2px 10px;border-radius:20px;text-transform:uppercase;background:{COLORS["amber"]}22;color:{COLORS["amber"]};border:1px solid {COLORS["amber"]}55;">{name2} wins</span>'
    else:
        tag = f'<span style="font-size:10px;font-weight:700;letter-spacing:1px;padding:2px 10px;border-radius:20px;text-transform:uppercase;background:{COLORS["border"]};color:{COLORS["text_faint"]};border:1px solid {COLORS["border"]};">Tie</span>'

    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:11px;text-transform:uppercase;letter-spacing:0.12em;
                         color:{COLORS['text_dim']};">{label}</span>
            {tag}
        </div>
        <div style="display:flex;gap:14px;align-items:center;">
            <div style="flex:1;">
                <div style="font-size:10px;color:{COLORS['text_faint']};margin-bottom:4px;">{name1}</div>
                <div style="height:6px;border-radius:3px;background:{COLORS['border_grid']};overflow:hidden;margin-bottom:4px;">
                    <div style="width:{p1_pct}%;height:100%;background:{COLORS['accent']};border-radius:3px;"></div>
                </div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:16px;
                            font-weight:700;color:{p1_color};">{v1}</div>
            </div>
            <div style="color:{COLORS['border_input']};font-size:12px;flex-shrink:0;">|</div>
            <div style="flex:1;">
                <div style="font-size:10px;color:{COLORS['text_faint']};margin-bottom:4px;">{name2}</div>
                <div style="height:6px;border-radius:3px;background:{COLORS['border_grid']};overflow:hidden;margin-bottom:4px;">
                    <div style="width:{p2_pct}%;height:100%;background:{COLORS['amber']};border-radius:3px;"></div>
                </div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:16px;
                            font-weight:700;color:{p2_color};">{v2}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return winner


def no_data_card(msg):
    st.markdown(f"""
    <div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
                border-radius:12px;padding:32px;text-align:center;
                color:{COLORS['text_dim']};font-size:14px;letter-spacing:0.08em;">
        {msg}
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------
# PAGE HEADER + TABS
# ----------------------------------------------------------------
page_header(
    f"<span style='font-size:11px; letter-spacing:0.15em; color:#6b7280;'>IPL ANALYTICS DASHBOARD</span><br>"
    f"<span style='font-size:34px; font-weight:900;'>PLAYER MATCHUPS</span>",
    f"<span style='color:#9ca3af;'>Head-to-head stats across players, teams, and battles</span>",
)

tab1, tab2, tab3 = st.tabs(["Player vs Player", "Player vs Team", "Batter vs Bowler"])


# ----------------------------------------------------------------
# TAB 1 — PLAYER VS PLAYER
# ----------------------------------------------------------------
with tab1:
    c1, c2 = st.columns(2)
    p1 = c1.selectbox("Player 1", players,
                      index=players.index("V Kohli") if "V Kohli" in players else 0,
                      key="pvp_p1")
    p2 = c2.selectbox("Player 2", players,
                      index=players.index("MS Dhoni") if "MS Dhoni" in players else 1,
                      key="pvp_p2")

    s1 = get_batting_stats(p1)
    s2 = get_batting_stats(p2)
    b1 = get_bowling_stats(p1)
    b2 = get_bowling_stats(p2)

    results = [
        determine_winner(s1["runs"],    s2["runs"]),
        determine_winner(s1["sr"],      s2["sr"]),
        determine_winner(s1["average"], s2["average"]),
        determine_winner(b1["wickets"], b2["wickets"]),
        determine_winner(b1["economy"], b2["economy"], invert=True),
    ]
    ow = overall_winner(results)

    player_vs_box(p1, get_role(p1), p2, get_role(p2), ow)

    section_header("Batting", COLORS["accent"])
    stat_compare("Runs",        s1["runs"],    s2["runs"],    p1, p2)
    stat_compare("Strike Rate", s1["sr"],      s2["sr"],      p1, p2)
    stat_compare("Average",     s1["average"], s2["average"], p1, p2)
    stat_compare("Fours",       s1["fours"],   s2["fours"],   p1, p2)
    stat_compare("Sixes",       s1["sixes"],   s2["sixes"],   p1, p2)

    section_header("Bowling", COLORS["amber"])
    stat_compare("Wickets",     b1["wickets"], b2["wickets"], p1, p2)
    stat_compare("Economy",     b1["economy"], b2["economy"], p1, p2, invert=True)
    stat_compare("Average",     b1["average"], b2["average"], p1, p2, invert=True)
    stat_compare("Strike Rate", b1["sr"],      b2["sr"],      p1, p2, invert=True)


# ----------------------------------------------------------------
# TAB 2 — PLAYER VS TEAM
# ----------------------------------------------------------------
with tab2:
    role_choice = st.radio("Role", ["Batter", "Bowler"], horizontal=True)

    if role_choice == "Batter":
        batters = sorted(pvt["batter"].unique())
        c1, c2  = st.columns(2)
        player  = c1.selectbox("Batter", batters,
                               index=batters.index("V Kohli") if "V Kohli" in batters else 0,
                               key="pvt_batter")
        team    = c2.selectbox("Bowling Team", teams, key="pvt_bowl_team")
        data    = pvt[(pvt["batter"] == player) & (pvt["bowling_team"] == team)]

        if not data.empty:
            d          = data.iloc[0]
            runs       = int(d["runs"])
            balls      = int(d["balls"])
            dismissals = int(d["dismissals"])
            fours      = int(d["fours"])
            sixes      = int(d["sixes"])
            sr         = round(float(d["strike_rate"]), 1)
            average    = round(runs / dismissals, 1) if dismissals > 0 else round(float(d["average"]), 1)

            spacer(8)
            section_header(f"{player} vs {team}", COLORS["accent"])

            c1, c2, c3 = st.columns(3)
            stat_card(c1, "Runs",        str(runs),       value_color=COLORS["accent"], accent=COLORS["accent"])
            stat_card(c2, "Strike Rate", str(sr),         value_color=COLORS["accent"], accent=COLORS["accent"])
            stat_card(c3, "Average",     str(average),    value_color=COLORS["accent"], accent=COLORS["accent"])

            spacer(8)
            c4, c5, c6 = st.columns(3)
            stat_card(c4, "Fours",      str(fours),      accent=COLORS["accent"])
            stat_card(c5, "Sixes",      str(sixes),      value_color=COLORS["amber"],  accent=COLORS["amber"])
            stat_card(c6, "Dismissals", str(dismissals), value_color=COLORS["red"],    accent=COLORS["red"])
        else:
            no_data_card(f"No data found for {player} vs {team}")

    else:
        bowlers = sorted(bvt["bowler"].unique())
        c1, c2  = st.columns(2)
        player  = c1.selectbox("Bowler", bowlers,
                               index=bowlers.index("JJ Bumrah") if "JJ Bumrah" in bowlers else 0,
                               key="pvt_bowler")
        team    = c2.selectbox("Batting Team", teams, key="pvt_bat_team")
        data    = bvt[(bvt["bowler"] == player) & (bvt["batting_team"] == team)]

        if not data.empty:
            d       = data.iloc[0]
            runs_c  = int(d["runs_conceded"])
            wickets = int(d["wickets"])
            balls   = int(d["balls"])
            overs   = round(float(d["overs"]), 1)
            economy = round(float(d["economy"]), 2)
            average = round(runs_c / wickets, 1) if wickets > 0 else 0.0
            sr      = round(balls / wickets, 1)  if wickets > 0 else 0.0

            spacer(8)
            section_header(f"{player} vs {team}", COLORS["amber"])

            c1, c2, c3 = st.columns(3)
            stat_card(c1, "Wickets",      str(wickets), value_color=COLORS["amber"], accent=COLORS["amber"])
            stat_card(c2, "Economy",      str(economy), value_color=COLORS["amber"], accent=COLORS["amber"])
            stat_card(c3, "Overs Bowled", str(overs),   value_color=COLORS["amber"], accent=COLORS["amber"])

            spacer(8)
            c4, c5, c6 = st.columns(3)
            stat_card(c4, "Runs Conceded", str(runs_c),  value_color=COLORS["red"],  accent=COLORS["red"])
            stat_card(c5, "Average",       str(average), accent=COLORS["accent"])
            stat_card(c6, "Strike Rate",   str(sr),      accent=COLORS["accent"])
        else:
            no_data_card(f"No data found for {player} vs {team}")


# ----------------------------------------------------------------
# TAB 3 — BATTER VS BOWLER
# ----------------------------------------------------------------
with tab3:
    batters = sorted(pvp["batter"].unique())
    bowlers = sorted(pvp["bowler"].unique())

    c1, c2 = st.columns(2)
    batter = c1.selectbox("Batter", batters,
                          index=batters.index("V Kohli") if "V Kohli" in batters else 0,
                          key="bvb_batter")
    bowler = c2.selectbox("Bowler", bowlers,
                          index=bowlers.index("JJ Bumrah") if "JJ Bumrah" in bowlers else 0,
                          key="bvb_bowler")

    data = pvp[(pvp["batter"] == batter) & (pvp["bowler"] == bowler)]

    if not data.empty:
        d          = data.iloc[0]
        runs       = int(d["runs"])
        balls      = int(d["balls"])
        dismissals = int(d["dismissals"])
        sr         = round(float(d["strike_rate"]), 1)
        average    = round(runs / dismissals, 1) if dismissals > 0 else round(float(d["average"]), 1)
        dot_balls  = balls - runs

        batter_score = (sr / 100) + (runs / 50)
        bowler_score = (dismissals * 10) + max(0, (130 - sr))
        ow           = "p1" if batter_score > bowler_score else "p2"

        player_vs_box(batter, "Batter", bowler, "Bowler", ow)

        section_header("Matchup Stats", COLORS["accent"])

        c1, c2, c3 = st.columns(3)
        stat_card(c1, "Runs Scored", str(runs),       value_color=COLORS["accent"], accent=COLORS["accent"])
        stat_card(c2, "Balls Faced", str(balls),      accent=COLORS["accent"])
        stat_card(c3, "Strike Rate", str(sr),         value_color=COLORS["accent"], accent=COLORS["accent"])

        spacer(8)
        c4, c5, c6 = st.columns(3)
        stat_card(c4, "Dismissals", str(dismissals), value_color=COLORS["red"],    accent=COLORS["red"])
        stat_card(c5, "Average",    str(average),    accent=COLORS["accent"])
        stat_card(c6, "Dot Balls",  str(dot_balls),  value_color=COLORS["red"],    accent=COLORS["red"])
    else:
        no_data_card(f"No data found for {batter} vs {bowler}")