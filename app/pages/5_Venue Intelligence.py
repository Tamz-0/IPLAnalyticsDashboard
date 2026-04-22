import os
import sys

import plotly.express as px
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

st.set_page_config(layout="wide", page_title="Venue Stats | IPL Dashboard")
inject_global_css()


# ----------------------------------------------------------------
# DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    import pandas as pd
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    venue_df = pd.read_csv(os.path.join(base, "data", "processed", "venue_stats.csv"))
    season_df = pd.read_csv(os.path.join(base, "data", "processed", "season_stats.csv"))

    venue_df = venue_df.rename(columns={
        "match_id": "matches",
        "average_score_by_venue": "avg_score",
        "highest_totals": "highest_total",
    })

    venue_df["avg_score"] = venue_df["avg_score"].round(1)
    venue_df["highest_total"] = venue_df["highest_total"].astype(int)
    venue_df["matches"] = venue_df["matches"].astype(int)

    return venue_df, season_df

df,season_df     = load_data()
venues = sorted(df["venue"].unique())
start_year = int(season_df["season"].min())
end_year   = int(season_df["season"].max())


# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
sidebar_header("Venue Intelligence")

sidebar_label("Focus Venue")
selected_venue = st.sidebar.selectbox(
    "Focus Venue", venues, label_visibility="collapsed"
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

sidebar_label("Compare Venues")
selected_venues = st.sidebar.multiselect(
    "Compare Venues", venues, default=venues,
    label_visibility="collapsed", placeholder="All venues",
)
if not selected_venues:
    selected_venues = venues

st.sidebar.markdown(
    f"<p style='font-size:11px;color:{COLORS['text_faint']};margin-top:4px;'>"
    f"{len(selected_venues)}/{len(venues)} venues</p>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
top_n = st.sidebar.slider("Show Top N Venues in Charts", 5, 20, 10)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
sidebar_footer(start_year, end_year)


# ----------------------------------------------------------------
# PAGE HEADER
# ----------------------------------------------------------------
page_header(
    f"<span style='font-size:11px; letter-spacing:0.15em; color:#6b7280;'>IPL ANALYTICS DASHBOARD</span><br>"
    f"<span style='font-size:36px; font-weight:900; letter-spacing:0.02em;'>{selected_venue.upper()}</span>",
    f"<span style='color:#9ca3af;'>Venue Analysis · IPL {start_year}–{end_year}</span>",
)

venue_row = df[df["venue"] == selected_venue].iloc[0]

c1, c2, c3 = st.columns(3)
stat_card(c1, "Matches Hosted",  str(venue_row["matches"]),                 accent=COLORS["accent"])
stat_card(c2, "Average Score",   f"{venue_row['avg_score']:.0f}",           value_color=COLORS["amber"], accent=COLORS["amber"])
stat_card(c3, "Highest Total",   str(venue_row["highest_total"]),           value_color=COLORS["green"], accent=COLORS["green"])

spacer(8)


# ----------------------------------------------------------------
# SECTION — VENUE COMPARISON
# ----------------------------------------------------------------
section_header("Venue Comparison", COLORS["accent"])

compare_df = df[df["venue"].isin(selected_venues)]
left, right = st.columns(2)

top_matches = compare_df.sort_values("matches", ascending=True).tail(top_n)
fig1 = px.bar(
    top_matches, x="matches", y="venue", orientation="h",
    title=f"Top {top_n} Venues by Matches Hosted",
    color_discrete_sequence=[COLORS["accent"]],
)
fig1.update_traces(marker_line_width=0)
apply_chart_theme(fig1, height=420)
fig1.update_layout(yaxis=dict(autorange="reversed"))
left.plotly_chart(fig1, use_container_width=True, key="matches_bar")

top_scores = compare_df.sort_values("avg_score", ascending=True).tail(top_n)
fig2 = px.bar(
    top_scores, x="avg_score", y="venue", orientation="h",
    title=f"Top {top_n} Venues by Average Score",
    color_discrete_sequence=[COLORS["amber"]],
)
fig2.update_traces(marker_line_width=0)
apply_chart_theme(fig2, height=420)
fig2.update_layout(yaxis=dict(autorange="reversed"))
right.plotly_chart(fig2, use_container_width=True, key="scores_bar")


# ----------------------------------------------------------------
# SECTION — SCATTER
# ----------------------------------------------------------------
section_header("Highest Totals vs Average Score", COLORS["amber"])

fig3 = px.scatter(
    compare_df,
    x="avg_score",
    y="highest_total",
    size="matches",
    hover_name="venue",
    title="Highest Total vs Avg Score (bubble size = matches played)",
    color_discrete_sequence=[COLORS["accent"]],
)
fig3.update_traces(
    marker=dict(opacity=0.8, line=dict(color=COLORS["bg_base"], width=1))
)
apply_chart_theme(fig3, height=420)
st.plotly_chart(fig3, use_container_width=True, key="scatter")


# ----------------------------------------------------------------
# SECTION — TABLE
# ----------------------------------------------------------------
section_header("All Venue Stats", COLORS["green"])

table_df = compare_df.sort_values("highest_total", ascending=False)[
    ["venue", "matches", "avg_score", "highest_total"]
].copy()
table_df.columns     = ["Venue", "Matches", "Avg Score", "Highest Total"]
table_df["Avg Score"] = table_df["Avg Score"].round(1)

st.dataframe(table_df, use_container_width=True, hide_index=True)