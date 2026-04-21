import streamlit as st
import pandas as pd

st.set_page_config(page_title="IPL Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/season_stats.csv")

df = load_data()

st.title("IPL Analytics Dashboard")
st.markdown("Season-by-season breakdown of IPL from 2008 to 2025")

season = st.selectbox("Select Season", sorted(df['season'].unique(), reverse=True))

row = df[df['season'] == season].iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Matches", int(row['total_matches']))
c2.metric("Total Runs", f"{int(row['total_runs']):,}")
c3.metric("Most Sixes", int(row['most_sixes']))
c4.metric("Highest Score", int(row['highest_score']))
c5.metric("Champion", row['title_winner'])