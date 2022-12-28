import numpy as np
import pandas as pd


def load_past_matches(file):
    df = pd.read_csv(f'../../data/{file}')
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df['date'] = pd.to_datetime(df['date'], utc = True)

    return df


def join_data(df1, df2):
    df = pd.merge(df1, df2,  how='left',
        left_on=['league', 'date','team', 'opponent', 'home'],
        right_on=['league', 'date','team', 'opponent', 'home'])
    df.sort_values(by=['date', 'league', 'team', 'opponent'], inplace=True)

    return df


elos = load_past_matches("elos_matches.csv")
goals = load_past_matches("goals_matches.csv")
data = join_data(elos, goals)

# print(data.shape)
# print(data.tail())