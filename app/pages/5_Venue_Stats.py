import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.charts import apply_theme

st.set_page_config(layout="wide", page_title="Venue Stats | IPL Dashboard")

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

# ----------------------------------------------------------------
# LOAD — venue_stats.csv is already aggregated, no re-groupby needed
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    venue_path = os.path.join(BASE_DIR, "data", "processed", "venue_stats.csv")
    df = pd.read_csv(venue_path)
    df = df.rename(columns={
        "match_id":              "matches",
        "average_score_by_venue":"avg_score",
        "highest_totals":        "highest_total"
    })
    df["avg_score"]     = df["avg_score"].round(1)
    df["highest_total"] = df["highest_total"].astype(int)
    df["matches"]       = df["matches"].astype(int)
    return df

# ================================================================
# MAIN
# ================================================================
def main():
    df = load_data()
    venues = sorted(df["venue"].unique())

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
            Venue Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    sidebar_label("Focus Venue")
    selected_venue = st.sidebar.selectbox(
        "Focus Venue", venues,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)

    sidebar_label("Compare Venues")
    selected_venues = st.sidebar.multiselect(
        "Compare Venues", venues,
        default=venues,
        label_visibility="collapsed",
        placeholder="All venues"
    )
    if not selected_venues:
        selected_venues = venues

    st.sidebar.markdown(
        f"<p style='font-size:11px;color:#3a3a6a;margin-top:4px;'>"
        f"{len(selected_venues)}/{len(venues)} venues</p>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    top_n = st.sidebar.slider(
        "Show Top N Venues in Charts", 5, 20, 10
    )

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<p style='font-size:11px;color:#2a2a4a;text-align:center;"
        "letter-spacing:0.06em;'>DATA · IPL 2008–2025</p>",
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------------
    # FOCUS VENUE HEADER
    # ----------------------------------------------------------------
    venue_row = df[df["venue"] == selected_venue].iloc[0]

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;
                margin-bottom:28px;padding-bottom:20px;
                border-bottom:1px solid #1e1e3a;">
        <div style="width:6px;height:52px;background:#7c3aed;
                    border-radius:3px;flex-shrink:0;"></div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:34px;font-weight:800;color:#e8e8ff;
                        letter-spacing:0.04em;line-height:1;">
                {selected_venue.upper()}
            </div>
            <div style="font-size:12px;color:#5a5a8a;letter-spacing:0.1em;
                        text-transform:uppercase;margin-top:3px;">
                Venue Analysis · IPL 2008–2025
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3 stat cards for focus venue
    c1, c2, c3 = st.columns(3)
    stat_card(c1, "Matches Hosted",
              str(venue_row["matches"]),    "#e8e8ff", "#7c3aed")
    stat_card(c2, "Average Score",
              f"{venue_row['avg_score']:.0f}", "#f59e0b", "#f59e0b")
    stat_card(c3, "Highest Total Ever",
              str(venue_row["highest_total"]), "#22c55e", "#22c55e")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # SECTION 1 — VENUE COMPARISON CHARTS
    # ----------------------------------------------------------------
    section_header("Venue Comparison", "#7c3aed")

    compare_df = df[df["venue"].isin(selected_venues)]

    left, right = st.columns(2)

    # Top N by matches
    top_matches = compare_df.sort_values(
        "matches", ascending=True
    ).tail(top_n)

    fig1 = px.bar(
        top_matches, x="matches", y="venue",
        orientation="h",
        title=f"Top {top_n} Venues by Matches Hosted",
        color_discrete_sequence=["#7c3aed"]
    )
    fig1.update_traces(marker_line_width=0)
    apply_chart_theme(fig1, height=420)
    fig1.update_layout(yaxis=dict(autorange="reversed",
                                  gridcolor="#1a1a30",
                                  linecolor="#1a1a30"))
    left.plotly_chart(fig1, use_container_width=True, key="matches_bar")

    # Top N by avg score
    top_scores = compare_df.sort_values(
        "avg_score", ascending=True
    ).tail(top_n)

    fig2 = px.bar(
        top_scores, x="avg_score", y="venue",
        orientation="h",
        title=f"Top {top_n} Venues by Average Score",
        color_discrete_sequence=["#f59e0b"]
    )
    fig2.update_traces(marker_line_width=0)
    apply_chart_theme(fig2, height=420)
    fig2.update_layout(yaxis=dict(autorange="reversed",
                                  gridcolor="#1a1a30",
                                  linecolor="#1a1a30"))
    right.plotly_chart(fig2, use_container_width=True, key="scores_bar")

    # ----------------------------------------------------------------
    # SECTION 2 — HIGHEST TOTALS SCATTER
    # ----------------------------------------------------------------
    section_header("Highest Totals vs Average Score", "#f59e0b")

    fig3 = px.scatter(
        compare_df,
        x="avg_score",
        y="highest_total",
        size="matches",
        hover_name="venue",
        title="Highest Total vs Avg Score (bubble size = matches played)",
        color_discrete_sequence=["#7c3aed"]
    )
    fig3.update_traces(
        marker=dict(opacity=0.8, line=dict(color="#080810", width=1))
    )
    apply_chart_theme(fig3, height=420)
    st.plotly_chart(fig3, use_container_width=True, key="scatter")

    # ----------------------------------------------------------------
    # SECTION 3 — FULL TABLE
    # ----------------------------------------------------------------
    section_header("All Venue Stats", "#22c55e")

    table_df = compare_df.sort_values(
        "highest_total", ascending=False
    )[["venue", "matches", "avg_score", "highest_total"]].copy()

    table_df.columns = ["Venue", "Matches", "Avg Score", "Highest Total"]
    table_df["Avg Score"] = table_df["Avg Score"].round(1)

    st.dataframe(table_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()