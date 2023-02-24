"""
This file is to output the current streak that a team is on.
"""

import numpy as np
import pandas as pd

pd.set_option('mode.chained_assignment', None)


def duplicate_to_team_and_opponent(df_matches):
    df_matches = df_matches[['league', 'date', 'pt1', 'pt2', 'score_pt1', 'score_pt2']]
    df_matches['conceded_pt1'] = df_matches['score_pt2']
    df_matches['conceded_pt2'] = df_matches['score_pt1']

    df_matches_copy = df_matches.copy()
    df_matches = df_matches.rename(columns={'pt1': 'team', 'pt2': 'opponent', 'score_pt1': 'team_goals_scored',
                                            'score_pt2': 'opponent_goals_scored', 'conceded_pt1': 'team_goals_conceded',
                                            'conceded_pt2': 'opponent_goals_conceded'})
    df_matches_copy = df_matches_copy.rename(columns={'pt2': 'team', 'pt1': 'opponent', 'score_pt2': 'team_goals_scored',
                                            'score_pt1': 'opponent_goals_scored', 'conceded_pt2': 'team_goals_conceded',
                                            'conceded_pt1': 'opponent_goals_conceded'})
    df_matches_copy = df_matches_copy[['league', 'date', 'team', 'opponent', 'team_goals_scored', 'opponent_goals_scored',
                                        'team_goals_conceded', 'opponent_goals_conceded',
                                        ]]
    df_matches.loc[:, 'home'] = 1
    df_matches_copy.loc[:, 'home'] = 0
    df_matches = pd.concat([df_matches, df_matches_copy])
    df_matches.sort_values(by='date', inplace=True)

    return df_matches


def make_streak(S1):
    '''
    This function takes the values of Win/Loss column as input and returns a list of streak values
    eg: input list : ['Loss', 'Win', 'Win', 'Win', 'Loss', 'Loss']
    output list : ['L1', 'W1', 'W2', 'W3', 'L1', 'L2']
    '''
    S2 = []
    for i in range(len(S1)):
        if i==0:
            S2.append(S1[i][0]+'1');continue
        if S1[i] != S1[i-1]:
            S2.append(S1[i][0]+'1')
        if S1[i] == S1[i-1]:
            S2.append(S1[i][0]+str(int(S2[-1][-1])+1))
    S2.insert(0,'')
    S2 = S2[1:]
    return S2


def create_col(row):
    '''
    This function takes every row of df as input, and returns the value for the
    new column:'Win/Loss Streak'(to be created)
    '''
    df_temp = data[(data[f'team'] == row[f'team'])] #Create a temporary dataframe with passed in row's team name
    df_temp['streak'] = make_streak(df_temp[f'win'].tolist())
    return (df_temp[ df_temp['row_num'] == row['row_num']]['streak'].values[0]) #Return df_temp's last column value which matches passed in row's row number


def create_col_team_opp(df):
    '''
    This function takes every team of df as input, and returns the value for the
    new column:'Win/Loss Streak'(to be created)
    '''
    cols = df.columns
    df_streak = pd.DataFrame(columns=cols)
    df_streak['team_streak'] = None
    df_streak['opponent_streak'] = None
    for team in df['team'].unique().tolist():
        df_temp_joined = pd.DataFrame(columns=cols)
        
        df_temp = df[(df[f'team'] == team) & (df[f'home'] == 1)]
        df_temp['team_streak'] = make_streak(df_temp[f'win'].tolist())
        df_temp_joined = pd.concat([df_temp_joined, df_temp])
        
        df_temp = df[(df[f'team'] == team) & (df[f'home'] == 0)]
        df_temp['opponent_streak'] = make_streak(df_temp[f'win'].tolist())
        df_temp_joined = pd.concat([df_temp_joined, df_temp])
        
        df_temp_joined.sort_values(by='date', inplace=True)
        df_temp_joined.loc[:,'team_streak'] = df_temp_joined.loc[:,'team_streak'].bfill()
        df_temp_joined.loc[:,'opponent_streak'] = df_temp_joined.loc[:,'opponent_streak'].bfill()
        
        df_temp_joined.loc[:,'team_streak'] = df_temp_joined.loc[:,'team_streak'].ffill()
        df_temp_joined.loc[:,'opponent_streak'] = df_temp_joined.loc[:,'opponent_streak'].ffill()
        
        df_streak = pd.concat([df_streak, df_temp_joined])
    df_streak.sort_values(by=['date'], inplace=True)
        
    return df_streak


def load_data(path):
    df = pd.read_csv(path, dtype={'manager_pt1': str, 'manager_pt2': str}, index_col=0)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['date'] = df['date'].dt.date
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)

    return df


def get_win_loss(df):
    win = []
    for h, a in zip(df['team_goals_scored'], df['opponent_goals_scored']):
        if h > a:
            win.append('win')
        if a > h:
            win.append('loss')
        if a == h:
            win.append('draw')
    df['win'] = win
    return df


def make_streak_5(S1):
    '''
    This function takes the values of Win/Loss column as input and returns a list of streak values
    eg: input list : ['Loss', 'Win', 'Win', 'Win', 'Loss', 'Loss']
    output list : ['L1', 'W1', 'W2', 'W3', 'L1', 'L2']
    '''
    S2 = []
    for i in range(len(S1)):
        if i==0:
            S2.append(S1[i][0]);continue
        elif i<=4:
            S2.append(S1[i][0] + S2[-1]);continue
        elif i>=5:
            S2.append(S1[i][0] + S2[-1][:-1])
    S2.insert(0,'')
    S2 = S2[1:]
    return S2


def create_col_5_team_opp(df):
    '''
    This function takes every team of df as input, and returns the value for the
    new column:'Win/Loss Streak'(to be created)
    '''
    cols = df.columns
    df_streak = pd.DataFrame(columns=cols)
    df_streak['team_last_5'] = ''
    df_streak['opponent_last_5'] = ''
    df.sort_values(by='date', inplace=True)
    for team in df['team'].unique().tolist():
        df_temp_joined = pd.DataFrame(columns=cols)
        
        df_temp = df[(df[f'team'] == team) & (df[f'home'] == 1)]
        df_temp['team_last_5'] = make_streak_5(df_temp[f'win'].tolist())
        df_temp_joined = pd.concat([df_temp_joined, df_temp])
        
        df_temp = df[(df[f'team'] == team) & (df[f'home'] == 0)]
        df_temp['opponent_last_5'] = make_streak_5(df_temp[f'win'].tolist())
        df_temp_joined = pd.concat([df_temp_joined, df_temp])
        
        df_temp_joined.sort_values(by='date', inplace=True)
        df_temp_joined.loc[:,'team_last_5'] = df_temp_joined.loc[:,'team_last_5'].bfill()
        df_temp_joined.loc[:,'opponent_last_5'] = df_temp_joined.loc[:,'opponent_last_5'].bfill()
        
        df_temp_joined.loc[:,'team_last_5'] = df_temp_joined.loc[:,'team_last_5'].ffill()
        df_temp_joined.loc[:,'opponent_last_5'] = df_temp_joined.loc[:,'opponent_last_5'].ffill()
        
        df_streak = pd.concat([df_streak, df_temp_joined])
    df_streak.sort_values(by=['date'], inplace=True)
        
    return df_streak


def filter_output(df):
    df = df[[
    'league',
    'date',
    'team',
    'opponent',
    'home',
    'team_streak',
    'opponent_streak',
    'team_last_5',
    'opponent_last_5'
    ]]
    df = df[df['date'] >= '2022-07-30']
    df = df[df['league']=='Serie C, Girone B']
    df['league'] = df['league'].str.lower()

    return df

print("Calculating streaks...")
data = load_data("../data/football_matches.csv")
data['date'] = pd.to_datetime(data['date'], dayfirst=False)
data = duplicate_to_team_and_opponent(data)
data = get_win_loss(data)
data = create_col_team_opp(data)
data = create_col_5_team_opp(data)
data = filter_output(data)
data.to_csv("../data/dashboard_output/streaks.csv")