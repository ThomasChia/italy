"""
This file updates teams names to be inline.
"""


import pandas as pd


def update_names(df):
    df['pt1'] = df['pt1'].replace({'us_ancona': 'ancona', 'Inter Milan': 'inter_milan'})
    df['pt2'] = df['pt2'].replace({'us_ancona': 'ancona', 'Inter Milan': 'inter_milan'})
    

    return df


data = pd.read_csv("../../data/football_matches.csv", dtype={'manager_pt1': str, 'manager_pt2': str})
data = update_names(data)
# print(data.head())
# print(data.shape)
data.to_csv("../../data/football_matches.csv")