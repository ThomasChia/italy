"""
Objective:
This file is for calculated the expected goals in each match based on a simple Poisson model.
"""

import code
import numpy as np
import pandas as pd
import sqlite3
import time
pd.options.mode.chained_assignment = None  # default='warn'


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


def calc_rolling_average(df, team, stat_list, for_team=True):
    df.sort_values(by='date', inplace=True)
    if for_team:
        df_stat = df[df['team'] == team]
        df_stat_home = df[(df['team'] == team) & (df['home'] == 1)]
        df_stat_away = df[(df['team'] == team) & (df['home'] == 0)]
    else:
        df_stat = df[df['opponent'] == team]
        df_stat_home = df[(df['opponent'] == team) & (df['home'] == 0)]
        df_stat_away = df[(df['opponent'] == team) & (df['home'] == 1)]
    
    for stat in stat_list:
        df_stat.loc[:, stat + '_avg'] = df_stat[stat].shift(1).rolling(19).mean()
        if not any(substring in stat for substring in ['home', 'away']):
            df_stat_home.loc[:, stat + '_avg_home'] = df_stat_home[stat].shift(1).rolling(19).mean()
            df_stat_away.loc[:, stat + '_avg_away'] = df_stat_away[stat].shift(1).rolling(19).mean()
    
    
    df_stat_home_and_away = pd.concat([df_stat_home, df_stat_away])
    avg_cols = [col for col in df_stat_home_and_away.columns if 'avg' in col]
    df_stat_home_and_away = df_stat_home_and_away[avg_cols + ['team', 'date']]
    df_stat = df_stat.merge(df_stat_home_and_away, on=['team', 'date'], how='outer')
    
    df_stat.sort_values(by='date', inplace=True)
    df_stat.loc[:, avg_cols] = df_stat.loc[:,avg_cols].bfill()
    df_stat.loc[:, avg_cols] = df_stat.loc[:, avg_cols].ffill()
    
    return df_stat


def get_rolling_average(df, stats_list, for_team=True):
    teams_list = df['team'].unique().tolist()
    df['row_num'] = np.arange(1, len(df)+1)
    df_average = pd.DataFrame(columns=df.columns)

    for team in teams_list:
        df_temp = calc_rolling_average(df, team, stats_list, for_team)
        df_average = pd.concat([df_average, df_temp])

    df_average.drop('row_num', axis=1, inplace=True)

    return df_average


def get_league_average(df, scored_or_conceded):

    # print(df.shape)
    df_home = df[df['home'] == 1]
    df_away = df[df['home'] == 0]
    df_league_home_avg = df_home.pivot_table('team_goals_' + scored_or_conceded, index='date', columns='league')
    df_league_away_avg = df_away.pivot_table('team_goals_' + scored_or_conceded, index='date', columns='league')

    columns = df_league_home_avg.columns
    for column in columns:
        df_league_home_avg_copy = df_league_home_avg.copy().reset_index()
        df_league_away_avg_copy = df_league_away_avg.copy().reset_index()
        s_h = df_league_home_avg_copy[['date', column]].copy()
        s_a = df_league_away_avg_copy[['date', column]].copy()
        s_h[column + '_avg_home'] = s_h[column].dropna().shift(1).rolling(19).mean()
        s_a[column + '_avg_away'] = s_a[column].dropna().shift(1).rolling(19).mean()
        s_h.drop(column, axis=1, inplace=True)
        s_a.drop(column, axis=1, inplace=True)
        df_league_home_avg = df_league_home_avg.merge(s_h, left_on='date', right_on='date')
        df_league_away_avg = df_league_away_avg.merge(s_a, left_on='date', right_on='date')

    df_league_home_avg = df_league_home_avg.ffill()
    df_league_away_avg = df_league_away_avg.ffill()

    df_league_home_avg.reset_index(inplace=True)
    df_league_away_avg.reset_index(inplace=True)

    df_home_avg_merge = pd.merge(df, df_league_home_avg.melt(id_vars='date')
                                    # .assign(league = lambda x: x['variable'])
                                    , on=['league','date'])
    df_away_avg_merge = pd.merge(df, df_league_away_avg.melt(id_vars='date')
                                    # .assign(league = lambda x: x['variable'])
                                    , on=['league','date'])

    df_home_avg_merge.rename(columns={'value': 'league_home_goals_'  + scored_or_conceded}, inplace=True)
    df_away_avg_merge.rename(columns={'value': 'league_away_goals_'  + scored_or_conceded}, inplace=True)

    df_merge = df_home_avg_merge.copy()
    df_merge['league_away_goals_' + scored_or_conceded] = df_away_avg_merge['league_away_goals_' + scored_or_conceded]

    columns = columns.values.tolist()
    df_league_home_avg.drop(columns, axis=1, inplace=True)
    df_league_away_avg.drop(columns, axis=1, inplace=True)
    for column in df_league_home_avg.columns:
        if column[-9:] == '_avg_home':
            df_league_home_avg.rename(columns={column: column[:-9]}, inplace=True)
    for column in df_league_away_avg.columns:
        if column[-9:] == '_avg_away':
            df_league_away_avg.rename(columns={column: column[:-9]}, inplace=True)
    
    df_home_avg_merge = pd.merge(df_home_avg_merge, df_league_home_avg.melt(id_vars='date')
                                    # .assign(league = lambda x: x['variable'])
                                    , on=['league','date'])
    df_away_avg_merge = pd.merge(df_away_avg_merge, df_league_away_avg.melt(id_vars='date')
                                    # .assign(league = lambda x: x['variable'])
                                    , on=['league','date'])

    df_home_avg_merge.rename(columns={'value': 'league_home_goals_'  + scored_or_conceded + '_avg'}, inplace=True)
    df_away_avg_merge.rename(columns={'value': 'league_away_goals_'  + scored_or_conceded + '_avg'}, inplace=True)

    df_merge_avg = df_home_avg_merge.copy()
    df_merge_avg['league_away_goals_' + scored_or_conceded + '_avg'] = df_away_avg_merge['league_away_goals_' + scored_or_conceded + '_avg']
    df_merge = merge_on_common_columns(df_merge, df_merge_avg)
    df_merge.sort_values(by='date', inplace=True)
    # print(df_merge.tail())
    # print(df_merge.shape)


    return df_merge


def calc_lambda(df):
    strength_columns = ['team_attack_strength', 'team_defense_strength', 'opponent_attack_strength', 'opponent_defense_strength']
    df[strength_columns].fillna(0, inplace=True)
    conditions = [
        df['home'] == 1,
        df['home'] == 0,
    ]

    output_team = [
        df['league_home_goals_scored_avg'] * df['team_attack_strength'] * df['opponent_defense_strength'],
        df['league_away_goals_scored_avg'] * df['team_attack_strength'] * df['opponent_defense_strength'],
    ]

    output_opponent = [
        df['league_away_goals_scored_avg'] * df['opponent_attack_strength'] * df['team_defense_strength'],
        df['league_home_goals_scored_avg'] * df['opponent_attack_strength'] * df['team_defense_strength'],
    ]

    df['team_lambda'] = np.select(conditions, output_team, 'Other')
    df['opponent_lambda'] = np.select(conditions, output_opponent, 'Other')

    return df


def calc_strength(df):
    conditions = [
        df['home'] == 1,
        df['home'] == 0
    ]

    output_team_score = [
        df['team_goals_scored_avg_home'] / df['league_home_goals_scored_avg'],
        df['team_goals_scored_avg_away'] / df['league_away_goals_scored_avg']
    ]

    output_team_concede = [
        df['team_goals_conceded_avg_home'] / df['league_home_goals_conceded_avg'],
        df['team_goals_conceded_avg_away'] / df['league_away_goals_conceded_avg']
    ]

    output_opponent_score = [
        df['opponent_goals_scored_avg_away'] / df['league_away_goals_scored_avg'],
        df['opponent_goals_scored_avg_home'] / df['league_home_goals_scored_avg']
    ]

    output_opponent_concede = [
        df['opponent_goals_conceded_avg_away'] / df['league_away_goals_conceded_avg'],
        df['opponent_goals_conceded_avg_home'] / df['league_home_goals_conceded_avg']
    ]

    df['team_attack_strength'] = np.select(conditions, output_team_score, 'Other').astype(float)
    df['team_defense_strength'] = np.select(conditions, output_team_concede, 'Other').astype(float)
    df['opponent_attack_strength'] = np.select(conditions, output_opponent_score, 'Other').astype(float)
    df['opponent_defense_strength'] = np.select(conditions, output_opponent_concede, 'Other').astype(float)

    df.replace(np.nan, 0, inplace=True)
    df.replace('nan', 0, inplace=True)

    return df


def merge_on_common_columns(df1, df2):
    common_columns = list(set(df1.columns).intersection(df2.columns))

    df = pd.merge(df1, df2, on=common_columns)

    return df


# if __name__ == "__main__":
print("Calculating goals...")
start = time.time()

data_matches = pd.read_csv("../data/football_matches_a.csv", dtype={'manager_pt1': str, 'manager_pt2': str})
data_matches['date'] = pd.to_datetime(data_matches['date'], dayfirst=True)
data_matches['date'] = data_matches['date'].dt.date
data_matches.sort_values(by='date', inplace=True)
data_matches.reset_index(inplace=True, drop=True)

# data_matches = data_matches[-10000:]
data_matches = duplicate_to_team_and_opponent(data_matches)
team_stats = ['team_goals_scored',
        'team_goals_conceded',
        ]
opponent_stats = ['opponent_goals_scored',
                'opponent_goals_conceded',]
# league_stats = ['league_home_goals_scored',
#                 'league_home_goals_conceded',
#                 'league_away_goals_scored',
#                 'league_away_goals_conceded',]    
data_matches['id'] = np.arange(1, len(data_matches)+1)     
data_matches_team_avg = get_rolling_average(data_matches, team_stats, for_team=True)
data_matches_opponent_avg = get_rolling_average(data_matches, opponent_stats, for_team=False)
# data_matches_league_avg = get_rolling_average(data_matches, league_stats)
data_matches_avg = merge_on_common_columns(data_matches_team_avg, data_matches_opponent_avg)
# data_matches_avg = merge_on_common_columns(data_matches_avg, data_matches_league_avg)
data_matches = get_league_average(data_matches, 'scored')
data_matches = get_league_average(data_matches, 'conceded')
data_matches_avg = merge_on_common_columns(data_matches_avg, data_matches)
data_matches_avg = calc_strength(data_matches_avg)
data_matches_avg = calc_lambda(data_matches_avg)
data_matches_avg.reset_index(inplace=True, drop=True)
data_matches_avg.drop(['id', 'row_num',
                        # 'team_goals_scored',
                        # 'team_goals_conceded',
                        # 'opponent_goals_scored',
                        # 'opponent_goals_conceded'
                        ], axis=1, inplace=True)
data_matches_avg.drop_duplicates(subset=['date', 'team', 'opponent'], inplace=True)
data_matches_avg.to_csv('../data/goals_matches.csv')

finish = time.time()
print('time taken to calc lambda:', str(finish - start))
# code.interact(local=locals())