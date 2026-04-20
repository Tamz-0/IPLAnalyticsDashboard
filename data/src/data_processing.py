import pandas as pd
def load_and_clean(path):
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
    df=pd.read_csv(path)
    df=df.fillna("Missing")
    df["batting_team"]=df["batting_team"].replace(team_map)
    df["bowling_team"]=df["bowling_team"].replace(team_map)
    df['venue']=df.venue.str.split(",").str[0].replace(venue_mapping)
    df['date']=pd.to_datetime(df['date'])
    df['current_score']=df.groupby(['match_id','innings'])['runs_total'].cumsum()
    df['current_run_rate']=(df['current_score']/df['ball_no'])*6
    df['is_wicket']=df['player_out'].apply(lambda x:0 if x=="Missing" else 1)
    df['wickets_fallen']=df.groupby(['match_id','innings'])['is_wicket'].cumsum()
    return df
def create_df_stats_batter(df):
    stats_batter=df.groupby(['batter','season']).agg({
        'runs_batter':"sum",
        'balls_faced':'sum',
        'is_wicket':'sum'
    }).reset_index()
    stats_batter['strike_rate']=(stats_batter['runs_batter']/stats_batter['balls_faced'].replace(0,1))*100
    stats_batter['batting_average']=stats_batter['runs_batter']/stats_batter['is_wicket'].replace(0,1)
    stats_batter["is_four"]=(df['runs_batter']==4).astype(int)
    stats_batter["is_six"]=(df['runs_batter']==6).astype(int)
    return stats_batter
def create_df_stats_bowler(df):
    stats_bowler=df.groupby(['bowler','season']).agg({
        'runs_bowler':'sum',
        'bowler_wicket':'sum',
        'ball_no':'count'
    }).reset_index()
    
    stats_bowler['overs']=stats_bowler['ball_no']/6
    stats_bowler['bowling_avergae']=stats_bowler["runs_bowler"]/stats_bowler['bowler_wicket'].replace(0,1)
    stats_bowler['economy']=stats_bowler['runs_bowler']/stats_bowler['overs'].replace(0,1)
    stats_bowler["strike_rate"]=stats_bowler["ball_no"]/stats_bowler["bowler_wicket"].replace(0,1)
    
    return stats_bowler

def create_df_stats_team(df):
    matches=df[['match_id','season','batting_team','bowling_team','match_won_by']].drop_duplicates()
    team1=matches[['match_id','season','batting_team','match_won_by']].rename(columns={'batting_team':'team'})
    team2=matches[['match_id','season','bowling_team','match_won_by']].rename(columns={'bowling_team':'team'})
    all_teams=pd.concat([team1,team2])
    total_matches=all_teams.groupby(['team','season']).size().reset_index(name='matches')
    wins=all_teams[all_teams['team']==all_teams['match_won_by']].groupby(['team',"season"]).size().reset_index(name='wins')
    stats_team = total_matches.merge(wins, on=['team', 'season'], how='left')
    stats_team['wins']=stats_team['wins'].fillna(0)
    stats_team['losses']=stats_team['matches']-stats_team['wins']
    stats_team['win_pct']= (stats_team['wins']/stats_team['matches'])*100
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
def main():
    df=load_and_clean("../raw/IPL.csv")
    print(df.head())
    print(create_df_stats_batter(df).head())
    print(create_df_stats_bowler(df).head())
    print(create_df_stats_team(df).head())
    print(create_df_stats_venue(df).head())

if __name__=="__main__":
    main()