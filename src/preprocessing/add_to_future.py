"""
This file adds past stats to future matches for the purpose of prediction.
"""

import pandas as pd


def load_past_stats():
    df = pd.read_csv('../../data/joined_matches.csv', parse_dates=True, dayfirst=True)
    df.drop(['Unnamed: 0',
            # 'team_goals_scored',
            # 'team_goals_conceded',
            # 'opponent_goals_scored',
            # 'opponent_goals_conceded'
            ], axis=1, inplace=True)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df


def load_future_matches():
    df = pd.read_csv('../../data/future_matches.csv', parse_dates=True, dayfirst=True)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df = duplicate_to_team_and_opponent(df)
    return df


def add_stats_to_future(stats, future):
    columns = stats.columns
    stats = get_final_entry(stats, 'team')
    stats_opp = team_to_opponent(stats)

    df_future = pd.merge(future, stats, how='left', on='team')
    df_future = pd.merge(df_future, stats_opp, how='left', on='opponent')
    df_future['elo_diff'] = df_future['elo_team'] - df_future['elo_opponent']
    df_future['date'] = pd.to_datetime(df_future['date'], dayfirst=True)
    df_future['date'] = df_future['date'].dt.date

    df_future.sort_values(by='date', inplace=True)
    df_future = df_future[columns]

    return df_future


def get_final_entry(df, team_or_opponent):
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)
    df.drop_duplicates(subset=team_or_opponent, keep='last', inplace=True)
    df = df.loc[:, df.columns.str.contains(team_or_opponent) | df.columns.str.contains('league_')]

    return df


def duplicate_to_team_and_opponent(df_matches):
    df_matches_copy = df_matches.copy()
    df_matches = df_matches.rename(columns={'pt1': 'team', 'pt2': 'opponent',
                                            })
    df_matches_copy = df_matches_copy.rename(columns={'pt2': 'team', 'pt1': 'opponent',
                                                    })
    df_matches_copy = df_matches_copy[['league', 'date', 'team', 'opponent' 
                                        ]]
    df_matches.loc[:, 'home'] = 1
    df_matches_copy.loc[:, 'home'] = 0
    df_matches = pd.concat([df_matches, df_matches_copy])
    df_matches.sort_values(by='date', inplace=True)

    return df_matches


def team_to_opponent(df):
    df_opponent = df.copy()
    df_opponent = df_opponent.loc[:, df_opponent.columns.str.contains("team")]
    df_opponent.columns = df_opponent.columns.str.replace("team", "opponent")

    return df_opponent


stats_matches = load_past_stats()
future_matches = load_future_matches()

data = add_stats_to_future(stats_matches, future_matches)
data.to_csv('../../data/future_matches_processed.csv')