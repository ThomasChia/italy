import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F


class Loader:

    def __init__(self, files):
        self.files = files

    def get_data(self):
        dfs = []
        for file in self.files:
            df = self.load_past_matches(file)
            dfs.append(df)
        
        df_join = self.join_data(dfs[0], dfs[1])
        # self.set_up_data(df_join)

        return df_join

    def load_past_matches(self, file):
        df = pd.read_csv(f'../../data/{file}')
        df.drop('Unnamed: 0', axis=1, inplace=True)
        df['date'] = pd.to_datetime(df['date']).dt.date

        return df

    def join_data(self, df1, df2):
        df = pd.merge(df1, df2,  how='inner',
            left_on=['league', 'date','team', 'opponent', 'home'],
            right_on=['league', 'date','team', 'opponent', 'home'])
        df.sort_values(by=['date', 'league', 'team', 'opponent'], inplace=True)
        df.reset_index(inplace=True, drop=True)
              
        return df

class Wavenet:

    def __init__(self, df, future=None, past_matches=7):
        self.df = df
        self.future = future
        self.X = None
        self.Y = None
        self.dfs = None
        self.dfs_future = None
        self.past_matches = past_matches

    def set_up_data(self, df):
        df.drop(['team_goals_scored',
            'opponent_goals_scored',
            'team_goals_conceded',
            'opponent_goals_conceded'], axis=1, inplace=True)

    def build_dataset(self, df):
        df_copy = df.copy()
        df_copy.reset_index(inplace=True, drop=True)
        date = df_copy[['date']].iloc[:,0]
        df_copy.drop(['league', 'date', 'team', 'opponent'], axis=1, inplace=True)
        df_copy['date'] = date
        df_copy.sort_values(by=['date'], inplace=True)
        df_copy = df_copy[df_copy['date']<future_date]
        df_copy.drop(['date'], axis=1, inplace=True)
        
        self.X = df_copy.drop(['result'], axis=1).to_numpy()
        self.Y = np.array(df_copy['result']) / 0.5
        
        self.X = torch.tensor(self.X).float()
        self.Y = torch.tensor(self.Y).long()

    def add_past_to_row(self, df, i):
        df_past = df.copy()
        df_past.index += i
        df_past.rename(columns={c: c+f'_{i}' for c in df_past.columns if c not in ['league',
                                                                                'date',
                                                                                'team',
                                                                                'opponent']}, inplace=True)
        return df_past

    def build_matches_dataset(self, df, past_matches, team):
        dfs_past = []
        df_team = df[df['team']==team]
        for i in range(1, past_matches+1):
            df_past = self.add_past_to_row(df_team, i)
            dfs_past.append(df_past)

        df_team_joined = df_team.copy()
        for df_past in dfs_past:
            df_team_joined = pd.concat([df_team_joined, df_past],
                                        axis=1,
                                        )
        df_team_joined = df_team_joined[past_matches:-past_matches]

        return df_team_joined

    def build_teams_dataset(self, df, past_matches):
        dfs = []
        for team in df['team'].unique():
            df_team_joined = self.build_matches_dataset(df, past_matches, team)
            dfs.append(df_team_joined)
        dfs = pd.concat(dfs)
        dfs.insert(5, 'result_0', 0)

        return dfs
    
    def team_to_opponent(self, df):
        df_opponent = df.copy()
        df_opponent = df_opponent.loc[:, df_opponent.columns.str.contains("team")]
        df_opponent.columns = df_opponent.columns.str.replace("team", "opponent")

        return df_opponent
    
    def add_stats_to_future(self, stats, future):
        stats = get_final_entry(stats, 'team')
        stats_opp = self.team_to_opponent(stats)

        df_future = pd.merge(future, stats, how='left', on='team')
        df_future = pd.merge(df_future, stats_opp, how='left', on='opponent')
        df_future['elo_diff'] = df_future['elo_team'] - df_future['elo_opponent']
        df_future['date'] = pd.to_datetime(df_future['date'], dayfirst=True)
        df_future['date'] = df_future['date'].dt.date
        df_future.sort_values(by='date', inplace=True)

        return df_future
    
    def remove_duplicate_columns(self, df):
        df = df.loc[:,~df.columns.duplicated()].copy()
        return df

    def build_wavenet_dataset(self):
        df_copy = self.df.copy()
        df_copy.sort_values(by=['team', 'date'], inplace=True)
        df_copy.reset_index(inplace=True, drop=True)
        self.dfs = self.build_teams_dataset(df_copy, self.past_matches)
        self.build_dataset(self.dfs)

    def build_wavenet_dataset_past_future(self):
        df_copy = self.df.copy()
        self.set_up_data(df_copy)
        df_copy.sort_values(by=['team', 'date'], inplace=True)
        df_copy.reset_index(inplace=True, drop=True)
        self.dfs = self.build_teams_dataset(df_copy, self.past_matches)
        self.dfs_future = self.add_stats_to_future(self.dfs, self.future)
        self.dfs_future = self.dfs_future[self.dfs.columns]
        self.dfs = self.dfs.loc[:,~self.dfs.columns.duplicated()].copy()
        self.dfs = self.dfs[self.dfs['date']<future_date]
        self.build_dataset(self.dfs)
        self.dfs = self.remove_duplicate_columns(self.dfs)

def load_future_matches():
    df = pd.read_csv('../../data/future_matches.csv', parse_dates=True, dayfirst=True)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df = duplicate_to_team_and_opponent(df)
    df.reset_index(inplace=True, drop=True)
    return df


def get_final_entry(df, team_or_opponent):
    df = df.copy()
    df = df.loc[:,~df.columns.duplicated()].copy()
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)
    df.drop_duplicates(subset=team_or_opponent, keep='last', inplace=True)
    df = df.loc[:, df.columns.str.contains(team_or_opponent) | df.columns.str.contains('league_') |
               df.columns.str.contains('elo_diff') | df.columns.str.contains('^home_\\d', regex=True) |
               df.columns.str.contains('result')]

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


def build_future_dataset(df):
    df_copy = df.copy()
    df_copy.reset_index(inplace=True, drop=True)
    date = df_copy[['date']].iloc[:,0]
    df_copy.drop(['league', 'date', 'team', 'opponent'], axis=1, inplace=True)
    df_copy['date'] = date
    df_copy.sort_values(by=['date'], inplace=True)
    df_copy.drop(['date'], axis=1, inplace=True)
    
    X = df_copy.drop(['result'], axis=1).to_numpy()
    X = torch.tensor(X).float()
    
    return X


FILES = ["elos_matches.csv", "goals_matches.csv"]
loader = Loader(FILES)
future = load_future_matches()
future_date = future['date'][0]
data = loader.get_data()
wavenet = Wavenet(data, future, 7)
wavenet.build_wavenet_dataset_past_future()
wavenet.dfs.to_csv('../../data/joined_matches.csv')
wavenet.dfs_future.to_csv('../../data/future_matches_processed.csv')
