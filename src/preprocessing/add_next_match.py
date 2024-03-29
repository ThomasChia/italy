import numpy as np
import pandas as pd


def load_future_matches():
    df = pd.read_csv('../data/future_matches.csv', parse_dates=True, dayfirst=False)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df = duplicate_to_team_and_opponent(df)
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

def load_past_matches():
    df = pd.read_csv('../data/football_matches_a.csv', dtype={'manager_pt1': str, 'manager_pt2': str})
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['date'] = df['date'].dt.date
    df.drop('Unnamed: 0', axis=1, inplace=True)

    return df

def get_first_match(df):
    df.drop_duplicates(subset=['team'], keep='first', inplace=True)
    df_combined = compress_home_away(df)
    return df_combined

def compress_home_away(df):
    df_home = df[df['home']==1]
    df_away = df[df['home']==0]
    df_home = df_home.rename(columns={'team': 'pt1', 'opponent': 'pt2'})
    df_away = df_away.rename(columns={'team': 'pt2', 'opponent': 'pt1'})

    df_combined = pd.concat([df_home, df_away])
    df_combined.drop_duplicates(subset=['pt1'], keep='first', inplace=True)
    df_combined.drop(['home'], axis=1, inplace=True)
    df_combined.reset_index(inplace=True, drop=True)
    return df_combined

def remove_duplicate_matches(df):
    df = df.drop_duplicates(subset=['date', 'pt1', 'pt2'])
    return df


past = load_past_matches()
future = load_future_matches()
data = get_first_match(future)
joined = pd.concat([past, data]).reset_index(drop=True)
joined = remove_duplicate_matches(joined)
joined.fillna(0, inplace=True)
print(joined.head())
joined.to_csv("../data/football_matches_a.csv")
