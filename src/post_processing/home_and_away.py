"""
This file takes the past predictions, formatted as team and opponent, and splits them into home and away.
Steps:
1. Import past predictions from csv
2. Duplicate where home=0
3. Swap team and opponent and change to home=1
4. Append to past predictions
5. Filter to home=1
6. Group by date, team, and opponent - mean aggregation
7. Change to match headings in gsheets.
8. Save to past_predictions_home_away
"""

import numpy as np
import pandas as pd


def duplicate_data(df):
    df_copy = df[df['home']==0].copy()
    return df_copy

def swap_team_and_opponent(df):
    df = df.rename(columns={'team': 'opponent', 'opponent': 'team'}).copy()
    df['home'] = 1
    return df
    
def update_original(df, df_new):
    df_combined = pd.concat([df, df_new])
    df_combined = df_combined[df_combined['home']==1]
    return df_combined

def compress_to_home_and_away(df):
    df_compress = df.groupby(by=['date', 'team', 'opponent']).mean()
    df_compress.reset_index(inplace=True)
    df_compress.rename(columns={'team': 'home_team',
                                'opponent': 'away_team',
                                '0': 'A',
                                '1': 'D',
                                '2': 'H'}, inplace=True)
    return df_compress

def add_additional_info(df, df_new):
    df_new = df_new[['date', 'home_team', 'away_team', 'A', 'D', 'H']]
    df.rename(columns={'team': 'home_team',
                        'opponent': 'away_team',
                        }, inplace=True)
    df_home = df[df['home']==1].copy()
    df_home = df_home.drop(['0', '1', '2'], axis=1)
    df_home = pd.merge(left=df_home, right=df_new,
                        left_on=['date', 'home_team', 'away_team'],
                        right_on=['date', 'home_team', 'away_team'])
    return df_home


def combine_team_and_opponent(df):
    df_temp = duplicate_data(df)
    df_temp = swap_team_and_opponent(df_temp)
    df_temp = update_original(df, df_temp)
    df_temp = compress_to_home_and_away(df_temp)
    df_temp = add_additional_info(df, df_temp)
    # df_temp = df_temp[[]]
    return df_temp


past_predictions = pd.read_csv("../data/past_predictions.csv", index_col=0, parse_dates=['date'], dayfirst=False)
home_and_away = combine_team_and_opponent(past_predictions)
home_and_away.to_csv("../data/dashboard_output/past_home_and_away_predictions.csv")