import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="IPL Analytics Dashboard")

# ---------------- LOAD ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/season_stats.csv")

df = load_data().sort_values("season", ascending=False)

# ---------------- GLOBAL THEME (EXACT COPY) ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}
.stApp { background: #080810; }

header[data-testid="stHeader"] { display: none; }

[data-testid="stSelectbox"] > div > div {
    background: #111128 !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
    color: #e8e8ff !important;
}

[data-testid="stPlotlyChart"] {
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    background: #0d0d20;
}

hr { border-color: #1e1e3a !important; }

</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def section_header(title, color="#7c3aed"):
    st.markdown(f"""
    <div style="font-family:'Barlow Condensed',sans-serif;
                font-size:18px;font-weight:700;
                letter-spacing:0.06em;text-transform:uppercase;
                color:#e8e8ff;margin:20px 0 16px;
                padding-left:10px;border-left:3px solid {color};">
        {title}
    </div>
    """, unsafe_allow_html=True)

def apply_chart_theme(fig):
    fig.update_layout(
        plot_bgcolor="#0d0d20",
        paper_bgcolor="#0d0d20",
        font=dict(color="#94a3b8", family="Barlow"),
        title_font=dict(color="#e8e8ff", size=15,
                        family="Barlow Condensed"),
        xaxis=dict(gridcolor="#1a1a30"),
        yaxis=dict(gridcolor="#1a1a30"),
        margin=dict(l=16, r=16, t=44, b=16),
    )
    return fig

# ---------------- HEADER ----------------
col1, col2 = st.columns([8,2])

with col1:
    st.markdown("""
    <div style="font-family:'Barlow Condensed',sans-serif;
                font-size:34px;font-weight:800;
                color:#e8e8ff;letter-spacing:0.04em;">
        IPL ANALYTICS
    </div>
    <div style="font-size:11px;color:#5a5a8a;
                letter-spacing:0.1em;text-transform:uppercase;">
        Season Overview
    </div>
    """, unsafe_allow_html=True)

with col2:
    seasons = df["season"].unique()
    selected = st.selectbox("", seasons)

season = df[df["season"] == selected].iloc[0]

# ---------------- HERO ----------------
st.markdown(f"""
<div style="display:flex;align-items:center;gap:16px;
            margin-bottom:28px;padding-bottom:20px;
            border-bottom:1px solid #1e1e3a;">
    <div style="width:6px;height:52px;background:#f59e0b;
                border-radius:3px;"></div>
    <div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:34px;font-weight:800;color:#e8e8ff;">
            {str(season['title_winner']).upper() if pd.notna(season['title_winner']) else "UNKNOWN"}
        </div>
        <div style="font-size:12px;color:#5a5a8a;
                    letter-spacing:0.1em;text-transform:uppercase;">
            IPL {selected} Champion
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- STAT STRIP ----------------
stats = [
    ("Matches", season["total_matches"]),
    ("Runs", season["total_runs"]),
    ("Sixes", season["most_sixes"]),
    ("Highest", season["highest_score"]),
]

cols = st.columns(4)

for col, (label, value) in zip(cols, stats):
    col.markdown(f"""
    <div style="background:#0d0d20;border:1px solid #1e1e3a;
                border-top:3px solid #7c3aed;
                border-radius:10px;padding:16px 18px;">
        <div style="font-size:10px;text-transform:uppercase;
                    letter-spacing:0.1em;color:#5a5a8a;">
            {label}
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:28px;font-weight:800;color:#e8e8ff;">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- CHARTS ----------------
section_header("Season Trends")

df_sorted = df.sort_values("season")

left, right = st.columns([3,2])

fig_runs = px.bar(df_sorted, x="season", y="total_runs")
fig_runs.add_scatter(
    x=df_sorted["season"],
    y=df_sorted["total_runs"],
    mode="lines",
    line=dict(width=3)
)
apply_chart_theme(fig_runs)
left.plotly_chart(fig_runs, use_container_width=True)

fig_sixes = px.bar(
    df_sorted, x="season", y="most_sixes",
    color_discrete_sequence=["#f59e0b"]
)
apply_chart_theme(fig_sixes)
right.plotly_chart(fig_sixes, use_container_width=True)

# ---------------- TABLE ----------------
section_header("All Seasons")

display_df = df[[
    "season","title_winner","total_matches",
    "total_runs","highest_score"
]].rename(columns={
    "season":"Season",
    "title_winner":"Champion",
    "total_matches":"Matches",
    "total_runs":"Runs",
    "highest_score":"Highest"
})

st.dataframe(display_df, use_container_width=True, hide_index=True)