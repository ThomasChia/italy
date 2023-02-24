"""
This file updates teams names to be inline.
"""

import code
import pandas as pd


def update_names(df):
    df['pt1'] = df['pt1'].replace({'us_ancona': 'ancona',
                                   'Inter Milan': 'inter_milan',
                                   'internazionale': 'inter_milan',
                                   'inter': 'inter_milan',
                                   'internazionale': 'inter_milan',
                                   'san_donato': 'san_donato_tavarnelle',
                                   'sassari_torres': 'torres',
                                   'verona': 'hellas_verona',})
    df['pt2'] = df['pt2'].replace({'us_ancona': 'ancona',
                                   'Inter Milan': 'inter_milan',
                                   'internazionale': 'inter_milan',
                                   'inter': 'inter_milan',
                                   'san_donato': 'san_donato_tavarnelle',
                                   'sassari_torres': 'torres',
                                   'verona': 'hellas_verona',})
    df['league'] = df['league'].replace({'Serie C Grp. A': 'Serie C, Girone A',
                                        'Serie C Grp. B': 'Serie C, Girone B',
                                        'Serie C Grp. C': 'Serie C, Girone C'})
    df['league'] = df['league'].replace({'Italian Serie A': 'Serie A',
                                        'Italian Serie B': 'Serie B',
                                        })

    return df

def duplicate_and_swap_pt1_pt2(df):
    df_copy = df.copy(deep=True)
    df_copy.columns = [col.replace('pt1', 'pt2') if 'pt1' in col else col.replace('pt2', 'pt1') if 'pt2' in col else col for col in df_copy.columns]
    df = pd.concat([df, df_copy]).reset_index(drop=True)
    return df

def drop_duplicates(df):
    df_clean = df.drop_duplicates(subset=['pt1', 'pt2', 'date'])
    return df_clean


data = pd.read_csv("../data/football_matches.csv", dtype={'manager_pt1': str, 'manager_pt2': str})
data = data.loc[:, ~data.columns.str.contains('Unnamed')]
data = update_names(data)
# data = duplicate_and_swap_pt1_pt2(data)
data = drop_duplicates(data)
data.to_csv("../data/football_matches_a.csv")

# code.interact(local=locals())