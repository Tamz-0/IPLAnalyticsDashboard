import pandas as pd
from pathlib import Path
def clean_season(x):
    x = str(x)
    if '/' in x:
        last_part = x.split('/')[-1]   
        if len(last_part) == 2:
            return int('20' + last_part)  
        else:
            return int(last_part)        

    return int(x)
def load_and_clean(path):
    df=pd.read_csv(path, low_memory=False)
    df['season'] = df['season'].apply(clean_season)
    df['season'] = pd.to_numeric(df['season'], errors='coerce')
    df = df.dropna(subset=['season'])
    df['season'] = df['season'].astype(int)
    team_map = {
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Deccan Chargers': 'Sunrisers Hyderabad', 
    'Rising Pune Supergiant': 'Rising Pune Supergiants', 
    'Kochi Tuskers Kerala': 'Other', 
    'Pune Warriors': 'Other',
    'Gujarat Lions': 'Other'
    }
    venue_mapping = {
        'M.Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
        'Feroz Shah Kotla': 'Arun Jaitley Stadium',
        'Sardar Patel Stadium': 'Narendra Modi Stadium',
        'Punjab Cricket Association Stadium': 'PCA IS Bindra Stadium',
        'Punjab Cricket Association IS Bindra Stadium': 'PCA IS Bindra Stadium',
        'Zayed Cricket Stadium': 'Sheikh Zayed Stadium',
        'Subrata Roy Sahara Stadium': 'Maharashtra Cricket Association Stadium',
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium': 'ACA-VDCA Stadium'
    }
    str_cols=df.select_dtypes(include='object').columns
    df[str_cols]=df[str_cols].fillna("Missing")
    df["batting_team"]=df["batting_team"].replace(team_map)
    df["bowling_team"]=df["bowling_team"].replace(team_map)
    df['match_won_by'] = df['match_won_by'].replace(team_map)
    df['venue']=df.venue.str.split(",").str[0].replace(venue_mapping)
    df['date']=pd.to_datetime(df['date'])
    df['current_score']=df.groupby(['match_id','innings'])['runs_total'].cumsum()
    df['current_run_rate']=(df['current_score']/df['ball_no'])*6
    df['is_wicket']=df['player_out'].apply(lambda x:0 if x=="Missing" else 1)
    df['wickets_fallen']=df.groupby(['match_id','innings'])['is_wicket'].cumsum()
    df["is_four"]=(df['runs_batter']==4).astype(int)
    df["is_six"]=(df['runs_batter']==6).astype(int)
    
    return df
def create_df_stats_batter(df):
    stats_batter=df.groupby(['batter','season']).agg({
        'runs_batter':"sum",
        'balls_faced':'sum',
        'is_wicket':'sum',
        'is_four':'sum',
        'is_six':'sum'
    }).reset_index()
    stats_batter['strike_rate']=(stats_batter['runs_batter']/stats_batter['balls_faced'].replace(0,1))*100
    stats_batter['batting_average']=stats_batter['runs_batter']/stats_batter['is_wicket'].replace(0,1)
    return stats_batter
def create_df_stats_bowler(df):
    stats_bowler=df.groupby(['bowler','season']).agg({
        'runs_bowler':'sum',
        'bowler_wicket':'sum',
        'ball_no':'count'
    }).reset_index()
    
    stats_bowler['overs']=stats_bowler['ball_no']/6
    stats_bowler['bowling_average']=stats_bowler["runs_bowler"]/stats_bowler['bowler_wicket'].replace(0,1)
    stats_bowler['economy']=stats_bowler['runs_bowler']/stats_bowler['overs'].replace(0,1)
    stats_bowler["strike_rate"]=stats_bowler["ball_no"]/stats_bowler["bowler_wicket"].replace(0,1)
    
    return stats_bowler

def create_df_stats_team(df):
    matches=df[['match_id','season','batting_team','bowling_team','match_won_by','toss_winner','toss_decision']].drop_duplicates()
    team1=matches[['match_id','season','batting_team','match_won_by']].rename(columns={'batting_team':'team'})
    team2=matches[['match_id','season','bowling_team','match_won_by']].rename(columns={'bowling_team':'team'})
    all_teams=pd.concat([team1,team2])
    total_matches=all_teams.groupby(['team','season']).size().reset_index(name='matches')
    wins=all_teams[all_teams['team']==all_teams['match_won_by']].groupby(['team',"season"]).size().reset_index(name='wins')
    stats_team = total_matches.merge(wins, on=['team', 'season'], how='left')
    stats_team['wins']=stats_team['wins'].fillna(0)
    stats_team['losses']=stats_team['matches']-stats_team['wins']
    stats_team['win_pct']= (stats_team['wins']/stats_team['matches'])*100
    toss = matches[['match_id','season','toss_winner','match_won_by','toss_decision']]
    toss_counts = toss.groupby(['toss_winner','season']).size().reset_index(name='toss_wins').rename(columns={
        'toss_winner':'team'
        })
    stats_team = stats_team.merge(toss_counts, on=['team','season'], how='left')
    stats_team['toss_wins'] = stats_team['toss_wins'].fillna(0)
    toss['toss_win_match_win'] = (toss['toss_winner'] == toss['match_won_by']).astype(int)

    toss_effect = toss.groupby(['toss_winner','season']) \
        .agg({'toss_win_match_win':'mean'}).reset_index() \
        .rename(columns={
            'toss_winner':'team',
            'toss_win_match_win':'toss_win_match_win_pct'
        })

    toss_effect['toss_win_match_win_pct'] *= 100

    stats_team = stats_team.merge(toss_effect, on=['team','season'], how='left')
    toss_decision = toss.groupby(['toss_winner','season','toss_decision']) \
        .size().reset_index(name='decision_count')

    toss_decision = toss_decision.pivot_table(
        index=['toss_winner','season'],
        columns='toss_decision',
        values='decision_count',
        fill_value=0
    ).reset_index()

    toss_decision = toss_decision.rename(columns={'toss_winner':'team'})

    stats_team = stats_team.merge(toss_decision, on=['team','season'], how='left')
    matches['is_chasing_win'] = (
        (matches['toss_decision'] == 'field') &
        (matches['toss_winner'] == matches['match_won_by'])
    ).astype(int)

    matches['is_defending_win'] = (
        (matches['toss_decision'] == 'bat') &
        (matches['toss_winner'] == matches['match_won_by'])
    ).astype(int)

    chasing = matches.groupby(['toss_winner','season'])['is_chasing_win'] \
        .sum().reset_index().rename(columns={'toss_winner':'team','is_chasing_win':'chasing_wins'})

    defending = matches.groupby(['toss_winner','season'])['is_defending_win'] \
        .sum().reset_index().rename(columns={'toss_winner':'team','is_defending_win':'defending_wins'})

    stats_team = stats_team.merge(chasing, on=['team','season'], how='left')
    stats_team = stats_team.merge(defending, on=['team','season'], how='left')

    runs_scored = df.groupby(['batting_team','season'])['runs_total'] \
        .sum().reset_index().rename(columns={'batting_team':'team','runs_total':'runs_scored'})

    runs_conceded = df.groupby(['bowling_team','season'])['runs_total'] \
        .sum().reset_index().rename(columns={'bowling_team':'team','runs_total':'runs_conceded'})

    stats_team = stats_team.merge(runs_scored, on=['team','season'], how='left')
    stats_team = stats_team.merge(runs_conceded, on=['team','season'], how='left')
    balls_faced = df.groupby(['batting_team','season']).size().reset_index(name='balls_faced') \
        .rename(columns={'batting_team':'team'})

    balls_bowled = df.groupby(['bowling_team','season']).size().reset_index(name='balls_bowled') \
        .rename(columns={'bowling_team':'team'})

    stats_team = stats_team.merge(balls_faced, on=['team','season'], how='left')
    stats_team = stats_team.merge(balls_bowled, on=['team','season'], how='left')
    stats_team['overs_faced'] = stats_team['balls_faced'] / 6
    stats_team['overs_bowled'] = stats_team['balls_bowled'] / 6

    stats_team['run_rate'] = stats_team['runs_scored'] / stats_team['overs_faced']
    stats_team['economy_rate'] = stats_team['runs_conceded'] / stats_team['overs_bowled']

    stats_team['nrr'] = stats_team['run_rate'] - stats_team['economy_rate']
    stats_team = stats_team[stats_team['team'] != 'Other']

    return stats_team

def create_df_stats_venue(df):
    stats_venue=df.groupby('venue').agg({
        'match_id':'nunique',
        'runs_total':'sum'
    }).reset_index()
    stats_venue["average_score_by_venue"]=stats_venue["runs_total"]/stats_venue["match_id"]
    high_scores=df.groupby(['venue','match_id','innings'])['runs_total'].sum().reset_index()
    highest_totals=high_scores.groupby('venue')['runs_total'].max().reset_index()
    highest_totals.columns=['venue',"highest_totals"]
    stats_venue=stats_venue.merge(highest_totals,on="venue",how="left")
    return stats_venue

def create_df_stats_season(df):
    df=df.copy()
    df['season'] = df['season'].apply(clean_season)
    df['season'] = pd.to_numeric(df['season'], errors='coerce')
    df = df.dropna(subset=['season'])
    df['season'] = df['season'].astype(int)
    season_base=df.groupby('season').agg({
        'match_id':'nunique',
        'runs_total':'sum',
        'is_six':'sum',
        'is_four':'sum'
    }).reset_index()
    match_totals=df.groupby(['season','match_id','innings'])['runs_total'].sum().reset_index()
    highest_scores = match_totals.groupby('season')['runs_total'].max().reset_index()
    highest_scores.columns = ['season', 'highest_score']
    finals=df[df['stage']=='Final'][['season','match_id','match_won_by']].drop_duplicates()
    champions = finals[['season','match_won_by']].rename(columns={
        'match_won_by':'title_winner'
        })
    manual_winners = {
    2008: 'Rajasthan Royals',
    2009: 'Deccan Chargers',
    2010: 'Chennai Super Kings'
}
    manual_df=pd.DataFrame([{
        'season':k,
        'title_winner':v}
        for k,v in manual_winners.items()
    ])
    champions=pd.concat([champions,manual_df],ignore_index=True)
    champions['season'] = champions['season'].astype(int)
    champions = champions.drop_duplicates(subset='season', keep='first')
    stats_season = season_base.merge(highest_scores, on='season')
    stats_season = stats_season.merge(champions, on='season', how='left')
    stats_season.columns = ['season', 'total_matches', 'total_runs', 'total_sixes','total_fours', 'highest_score', 'title_winner']
    return stats_season
def create_df_stats_h2h_matches(df):
    matches = df.groupby('match_id').agg({
        'season': 'first',
        'date': 'first',
        'batting_team': 'first',
        'bowling_team': 'first',
        'match_won_by': lambda x: x.dropna().iloc[-1] if len(x.dropna()) > 0 else None,
        'venue': 'first'
    }).reset_index()
    matches = matches[[
        'match_id',
        'season',
        'date',
        'batting_team',
        'bowling_team',
        'match_won_by',
        'venue'
    ]]

    matches = matches.rename(columns={
        'batting_team': 'team1',
        'bowling_team': 'team2',
        'match_won_by': 'winner'
    })
    matches['winner'] = matches['winner'].str.strip()
    # 🔥 REMOVE INVALID MATCHES (CRITICAL FIX)
    matches = matches[
        (matches['winner'].notna()) &
        (matches['winner'] != "Missing") &
        (matches['winner'] != "")
    ]

    # 🔥 REMOVE SELF MATCH BUG (rare but possible)
    matches = matches[matches['team1'] != matches['team2']]

    return matches
def create_df_stats_h2h_summary(matches):
    matches = matches.copy()

    # normalize team pairs
    matches['teamA'] = matches[['team1','team2']].min(axis=1)
    matches['teamB'] = matches[['team1','team2']].max(axis=1)

    h2hsummary_stats = matches.groupby(['teamA','teamB']).agg(
        total_matches=('match_id','count'),
        teamA_wins=('winner', lambda x: (x == x.name[0]).sum()),
        teamB_wins=('winner', lambda x: (x == x.name[1]).sum())
    ).reset_index()

    h2hsummary_stats['teamA_win_pct'] = (h2hsummary_stats['teamA_wins'] / h2hsummary_stats['total_matches']) * 100

    return h2hsummary_stats
def create_df_stats_h2h_player_stats(df):
    # ---------------- BATTERS ----------------
    bat = df.groupby([
        'batter','batting_team','bowling_team'
    ]).agg({
        'runs_batter':'sum',
        'balls_faced':'sum'
    }).reset_index()

    bat['strike_rate'] = (
        bat['runs_batter'] / bat['balls_faced'].replace(0,1)
    ) * 100

    bat = bat.rename(columns={
        'batter':'player',
        'batting_team':'player_team',
        'bowling_team':'opponent_team'
    })

    bat['role'] = 'batter'

    # ---------------- BOWLERS ----------------
    bowl = df.groupby([
        'bowler','bowling_team','batting_team'
    ]).agg({
        'runs_bowler':'sum',
        'bowler_wicket':'sum',
        'ball_no':'count'
    }).reset_index()

    bowl['overs'] = bowl['ball_no'] / 6
    bowl['economy'] = bowl['runs_bowler'] / bowl['overs'].replace(0,1)

    bowl = bowl.rename(columns={
        'bowler':'player',
        'bowling_team':'player_team',
        'batting_team':'opponent_team'
    })

    bowl['role'] = 'bowler'

    # ---------------- MERGE ----------------
    h2h_player_stats = pd.concat([bat, bowl], ignore_index=True)

    return h2h_player_stats
def create_df_player_vs_player(df):
    pvp = df.groupby(['batter', 'bowler']).agg(
        runs=('runs_batter', 'sum'),
        balls=('balls_faced', 'sum'),
        dismissals=('player_out', lambda x: x.notna().sum())
    ).reset_index()

    pvp['strike_rate'] = (pvp['runs'] / pvp['balls'].replace(0,1)) * 100
    pvp['average'] = pvp['runs'] / pvp['dismissals'].replace(0,1)

    return pvp
def create_df_player_vs_team(df):
    pvt = df.groupby(['batter', 'bowling_team']).agg(
        runs=('runs_batter', 'sum'),
        balls=('balls_faced', 'sum'),
        dismissals=('player_out', lambda x: x.notna().sum()),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum')
    ).reset_index()

    pvt['strike_rate'] = (pvt['runs'] / pvt['balls'].replace(0,1)) * 100
    pvt['average'] = pvt['runs'] / pvt['dismissals'].replace(0,1)

    return pvt
def create_df_bowler_vs_team(df):
    bvt = df.groupby(['bowler', 'batting_team']).agg(
        runs_conceded=('runs_bowler', 'sum'),
        wickets=('bowler_wicket', 'sum'),
        balls=('ball_no', 'count')
    ).reset_index()
    bvt['overs'] = bvt['balls'] / 6
    bvt['economy'] = bvt['runs_conceded'] / bvt['overs'].replace(0, 1)
    bvt['average'] = bvt['runs_conceded'] / bvt['wickets'].replace(0, 1)
    bvt['strike_rate'] = bvt['balls'] / bvt['wickets'].replace(0, 1)
    return bvt
def main():
    BASE_DIR = Path(__file__).resolve().parents[2]

    raw_path = BASE_DIR / "data" / "raw" / "IPL.csv"
    processed_dir = BASE_DIR / "data" / "processed"

    print("DEBUG PATH:", raw_path)   # 👈 ADD THIS TEMP

    if not raw_path.exists():
        raise FileNotFoundError(f"File not found at: {raw_path}")

    processed_dir.mkdir(parents=True, exist_ok=True)

    df = load_and_clean(raw_path)
    create_df_stats_batter(df).to_csv(processed_dir / "player_batting.csv", index=False)
    create_df_stats_bowler(df).to_csv(processed_dir / "player_bowler.csv", index=False)
    create_df_stats_team(df).to_csv(processed_dir / "team_stats.csv", index=False)
    create_df_stats_venue(df).to_csv(processed_dir / "venue_stats.csv", index=False)
    create_df_stats_season(df).to_csv(processed_dir / "season_stats.csv", index=False)
    create_df_stats_h2h_matches(df).to_csv(processed_dir / "h2h_matches.csv", index=False)
    create_df_stats_h2h_summary(create_df_stats_h2h_matches(df)).to_csv(processed_dir / "h2hsummary.csv", index=False)
    create_df_stats_h2h_player_stats(df).to_csv(processed_dir / "h2hplayer_stats.csv", index=False)
    create_df_player_vs_player(df).to_csv(processed_dir / "player_vs_player.csv", index=False)
    create_df_player_vs_team(df).to_csv(processed_dir / "player_vs_team.csv", index=False)
    create_df_bowler_vs_team(df).to_csv(processed_dir / "bowler_vs_team.csv", index=False)
    print("All Processed Files Saved")

if __name__=="__main__":
    main()