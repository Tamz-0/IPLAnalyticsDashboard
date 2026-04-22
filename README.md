# IPL Analytics Dashboard

A full-stack cricket analytics platform built on 17 years of IPL ball-by-ball data (2008–2025). Designed with a premium dark theme inspired by ESPN and Cricbuzz, featuring team intelligence, player profiling, head-to-head rivalry analysis, and venue breakdowns — all interactive and filterable by season.

---

## Screenshots

### Home — Season Overview
![Home](screenshots/home.png)
### Season Deep Dive
![Season Overview](screenshots/season_overview.png)

### Team Intelligence
![Team Analysis](screenshots/team_analysis.png)

### Player Insights
![Player Analysis](screenshots/player_analysis.png)

### Rivalries — Head to Head
![Head to Head](screenshots/head_to_head.png)

### Venue Intelligence
![Venue Stats](screenshots/venue_stats.png)

### Player Matchups
![Player H2H](screenshots/player_h2h.png)



---

## Features

| Page | What it does |
|---|---|
| Overview | Season-by-season trends, champion banner, runs and sixes charts |
| Season Deep Dive | Per-season team standings, top performers leaderboard, NRR, toss analysis |
| Team Analysis | Win%, NRR, chasing vs defending, toss decisions, team comparison |
| Player Analysis | Career and season stats for batters, bowlers, and all-rounders |
| Head to Head | Real H2H match data between any two teams, player trackers, toss effect |
| Venue Stats | Matches hosted, average scores, highest totals, scatter analysis |
| Player H2H | Player vs player, player vs team, batter vs bowler comparisons |

---

## Tech Stack

- **Frontend** — Streamlit, Plotly, custom CSS design system
- **Data** — Pandas, Kaggle IPL ball-by-ball dataset (2008–2025)
- **Language** — Python 3.10+
- **Design** — Barlow / Barlow Condensed, ESPN-inspired dark theme

---

## Project Structure

```
IPLAnalyticsDashboard/
│
├── main.py                        # Entry point — runs full pipeline + launches app
├── requirements.txt
│
├── app/                           # Streamlit application
│   ├── Home.py                    # Landing page + season overview
│   ├── .streamlit/
│   │   └── config.toml            # Theme configuration
│   ├── pages/
│   │   ├── 1_Overview.py          # Season deep dive
│   │   ├── 2_Team_Analysis.py     # Team intelligence
│   │   ├── 3_Player_Analysis.py   # Player profiling
│   │   ├── 4_Head_to_Head.py      # Team H2H
│   │   ├── 5_Venue_Stats.py       # Venue analysis
│   │   └── 6_Player_H2H.py        # Player matchups
│   └── utils/
│       ├── theme.py               # Global CSS + color system
│       ├── charts.py              # Universal Plotly theme
│       └── components.py          # Reusable UI components
│
├── src/
│   └── data_processing.py         # Full ETL pipeline
│
├── data/
│   ├── raw/
│   │   ├── IPL.csv                # Raw ball-by-ball data (auto-downloaded)
│   │   └── rawdatadownload.py     # Kaggle download script
│   └── processed/                 # Auto-generated CSVs (gitignored)
│
└── notebooks/
    └── 01_eda_and_processing.ipynb
```

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/Tamz-0/IPLAnalyticsDashboard.git
cd IPLAnalyticsDashboard
```

### 2. Set up a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Kaggle credentials

The data is downloaded automatically via the Kaggle API. You need a Kaggle account and API token.

1. Go to [kaggle.com](https://www.kaggle.com) → Account → API → Create New Token
2. This downloads a `kaggle.json` file
3. Place it at:
   - **Windows:** `C:\Users\<username>\.kaggle\kaggle.json`
   - **macOS/Linux:** `~/.kaggle/kaggle.json`

### 5. Run

```bash
python main.py
```

This will:
1. Download `IPL.csv` from Kaggle (skippable if already downloaded)
2. Run the full data processing pipeline and generate all CSVs
3. Launch the Streamlit dashboard at `http://localhost:8501`

> On subsequent runs, `main.py` will ask if you want to skip the download step since the data doesn't change.

---

## Data Pipeline

The ETL pipeline in `src/data_processing.py` takes the raw ball-by-ball CSV and produces:

| File | Description |
|---|---|
| `season_stats.csv` | Aggregated per-season stats + champion |
| `team_stats.csv` | Team performance per season including NRR, toss, chasing/defending |
| `player_batting.csv` | Batter stats per season — runs, SR, average, 4s, 6s |
| `player_bowler.csv` | Bowler stats per season — wickets, economy, average, SR |
| `venue_stats.csv` | Per-venue match count, average score, highest total |
| `h2h_matches.csv` | One row per match with normalized team pairs |
| `h2h_player_batting.csv` | Batter stats filtered per opponent team |
| `h2h_player_bowling.csv` | Bowler stats filtered per opponent team |
| `player_vs_team.csv` | Batter performance against each bowling team |
| `bowler_vs_team.csv` | Bowler performance against each batting team |
| `player_vs_player.csv` | Batter vs specific bowler matchup stats |

---

## Design System

All styling is centralized in `app/utils/` — no page contains raw CSS or duplicate code.

```
utils/theme.py       →  inject_css(), COLORS dict, get_team_color()
utils/charts.py      →  apply_chart_theme(fig, height)
utils/components.py  →  sidebar_header(), page_header(), section_header(),
                         stat_card(), leaderboard_card(), rivalry_banner(),
                         champion_banner(), split_bar(), no_data_card()
```

Color palette follows team brand colors for all 10 active franchises with fallbacks for historical teams.

---

## Dataset

- **Source:** [IPL Complete Dataset 2008–2025](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020) on Kaggle
- **Format:** Ball-by-ball delivery data
- **Size:** ~200,000+ rows
- **Coverage:** IPL seasons 2008 through 2025

---

## Roadmap

- [ ] Win probability model (live match state → predicted win %)
- [ ] Phase-wise analysis (powerplay, middle overs, death)
- [ ] Partnership analysis
- [ ] Wagon wheel visualization
- [ ] Mobile-responsive layout

---

## Contributing

Pull requests are welcome. For major changes please open an issue first.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Taha Murad Zaman**
[GitHub](https://github.com/Tamz-0) · [LinkedIn](https://www.linkedin.com/in/taha-0-zaman/)

---

> Built with Python, Streamlit, and a lot of cricket data.

