"""
This file creates and trains a WaveNet model, based on this paper from DeepMind:
https://arxiv.org/pdf/1609.03499.pdf
"""

import code
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

pd.options.mode.chained_assignment = None  # default='warn'

print(torch.backends.mps.is_available())
print(torch.backends.mps.is_built())
torch.device("mps")

PYTORCH_ENABLE_MPS_FALLBACK=1

class Loader:

    def __init__(self, files):
        self.files = files

    def get_data(self):
        dfs = []
        for file in self.files:
            df = self.load_past_matches(file)
            dfs.append(df)
        
        df_join = self.join_data(dfs[0], dfs[1])

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

    def __init__(self, df, future=None, past_matches=7, future_date=None):
        self.df = df
        self.future = future
        self.X = None
        self.Y = None
        self.dfs = None
        self.dfs_future = None
        self.past_matches = past_matches
        self.future_date = future_date
        self.index_columns = ['league', 'date', 'team', 'opponent', 'result']

    def set_up_data(self, df):
        df.drop_duplicates(subset=['date', 'team', 'opponent'], inplace=True)
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
        df_copy = df_copy[df_copy['date']<self.future_date]
        df_copy.drop(['date'], axis=1, inplace=True)
        
        self.X = df_copy.drop(['result'], axis=1).to_numpy()
        self.Y = np.array(df_copy['result']) / 0.5
        
        self.X = torch.tensor(self.X).float().to("mps")
        self.Y = torch.tensor(self.Y).long().to("mps")

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
        dfs = self.add_opponent_past_matches(dfs)
        dfs = self.ordering_columns(dfs)

        return dfs
    
    def add_opponent_past_matches(self, df):
        df = df.loc[:,~df.columns.duplicated()].copy()
        df_copy = df.copy()
        keep_same = {'league', 'date', 'team', 'opponent', 'result'}
        df_copy.columns = ['{}{}'.format(c, '' if c in keep_same else '_y') for c in df_copy.columns]
        df_copy['result'] = 1 - df_copy['result']
        df_copy.rename(columns={'team': 'opponent', 'opponent': 'team'}, inplace=True)
        df_combined = pd.merge(df, df_copy, how='left',
                              left_on=['league', 'date', 'team', 'opponent', 'result'],
                              right_on=['league', 'date', 'team', 'opponent', 'result'])
        return df_combined

    def ordering_columns(self, df):
        index_columns = self.index_columns
        template_columns = ['result', 'elo_team', 'elo_opponent', 'elo_diff', 'home', 'team_goals_scored_avg',
                           'team_goals_conceded_avg', 'team_goals_scored_avg_home',
                           'team_goals_conceded_avg_home', 'team_goals_scored_avg_away',
                           'team_goals_conceded_avg_away', 'opponent_goals_scored_avg',
                           'opponent_goals_conceded_avg', 'opponent_goals_scored_avg_home',
                           'opponent_goals_conceded_avg_home', 'opponent_goals_scored_avg_away',
                           'opponent_goals_conceded_avg_away', 'league_home_goals_scored',
                           'league_away_goals_scored', 'league_home_goals_scored_avg',
                           'league_away_goals_scored_avg', 'league_home_goals_conceded',
                           'league_away_goals_conceded', 'league_home_goals_conceded_avg',
                           'league_away_goals_conceded_avg', 'team_attack_strength',
                           'team_defense_strength', 'opponent_attack_strength',
                           'opponent_defense_strength', 'team_lambda', 'opponent_lambda']
        template_columns_y = [s + f'_y' for s in template_columns]
        columns = [[index_columns + ['result_0'] + template_columns[1:] + ['result_0_y'] + template_columns_y[1:]]]
        for i in range(1, self.past_matches+1):
            team_cols = [s + f'_{i}' for s in template_columns]
            opp_cols = [s + f'_{i}_y' for s in template_columns]
            columns.append([team_cols, opp_cols])

        columns = [subitem for sublist in columns for item in sublist for subitem in item]
        df = df[columns]
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)
        return df
    
    def get_final_entry(self, df, team_or_opponent):
        df = df.copy()
        df = df.loc[:,~df.columns.duplicated()].copy()
        df.sort_values(by='date', inplace=True)
        df.reset_index(inplace=True, drop=True)
        df.drop_duplicates(subset=team_or_opponent, keep='last', inplace=True)
        df = df.loc[:, ~df.columns.str.contains('_y')]
        df = df.drop(['home'], axis=1)
        return df
    
    def team_to_opponent(self, df):
        df_opponent = df.copy()     
        keep_same = {'league', 'date', 'team', 'opponent', 'result'}
        df_opponent.columns = ['{}{}'.format(c, '' if c in keep_same else '_y') for c in df_opponent.columns]
        df_opponent['result'] = 1 - df_opponent['result']
        df_opponent = self.drop_common_columns(df_opponent, 'opponent')
        return df_opponent
    
    def drop_common_columns(self, df, team_or_opp):
        columns_to_drop = [item for item in self.index_columns if item not in [team_or_opp]]
        df.drop(columns=columns_to_drop, axis=1, inplace=True)
        return df
    
    def add_stats_to_future(self, stats, future):
        stats = self.get_final_entry(stats, 'team')
        stats_opp = self.team_to_opponent(stats)
        stats = self.drop_common_columns(stats, 'team')

        df_future = pd.merge(future, stats, how='left', on='team')
        df_future = pd.merge(df_future, stats_opp, how='left', on='opponent')
        df_future['home_y'] = 1 - df_future['home']
        df_future['date'] = pd.to_datetime(df_future['date'], dayfirst=True)
        df_future['date'] = df_future['date'].dt.date
        df_future.sort_values(by='date', inplace=True)
#         df_future.drop_duplicates(subset=['team', 'opponent'], inplace=True)

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
        
    def order_date(self, df):
        df = df.sort_values(by=['team', 'date'])
        df = df.reset_index(drop=True)
        return df
    
    def drop_results(self, df):
        return df[df.drop(['result'], axis=1).columns]
    
    def remove_future_matches(self, df):
        return df[df['date']<future_date]

    def build_wavenet_dataset_past_future(self):
        df_copy = self.df.copy()
        self.set_up_data(df_copy)
        df_copy = self.order_date(df_copy)
        self.dfs = self.build_teams_dataset(df_copy, self.past_matches)
        self.dfs_future = self.add_stats_to_future(self.dfs, self.future)
        # self.dfs_future = self.drop_results(self.dfs_future)
        self.dfs_future = self.order_date(self.dfs_future)
        self.dfs = self.remove_duplicate_columns(self.dfs)
        self.dfs = self.remove_future_matches(self.dfs)
        self.build_dataset(self.dfs)
        self.dfs = self.remove_duplicate_columns(self.dfs)
    

def load_future_matches():
    df = pd.read_csv('../../data/future_matches_serie_a.csv', parse_dates=True, dayfirst=True)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df.drop('Unnamed: 0', axis=1, inplace=True)
    df = duplicate_to_team_and_opponent(df)
    df.reset_index(inplace=True, drop=True)
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

    X = df_copy.to_numpy()
    X = torch.tensor(X).float()
    
    return X

def add_stats_to_future(stats, future):
    columns = stats.drop(['result'], axis=1).columns
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

def define_split(X, Y, tr_split, val_split):
    n1 = int(0.8 * X.shape[0])
    n2 = int(0.9 * X.shape[0])

    Xtr, Ytr = X[:n1], Y[:n1]
    Xdev, Ydev = X[n1:n2], Y[n1:n2]
    Xte, Yte = X[n2:], Y[n2:]


FILES = ["elos_matches.csv", "goals_matches.csv"]
loader = Loader(FILES)
future = load_future_matches()
future_date = future['date'][0]
data = loader.get_data()
wavenet = Wavenet(data, future, 7, future_date)
wavenet.build_wavenet_dataset_past_future()

n1 = int(0.8 * wavenet.X.shape[0])
n2 = int(0.9 * wavenet.X.shape[0])

Xtr, Ytr = wavenet.X[:n1], wavenet.Y[:n1]
Xdev, Ydev = wavenet.X[n1:n2], wavenet.Y[n1:n2]
Xte, Yte = wavenet.X[n2:], wavenet.Y[n2:]

inputs_per_match = data.drop(['league', 'date', 'team', 'opponent',
                              'team_goals_scored',
                              'opponent_goals_scored',
                              'team_goals_conceded',
                              'opponent_goals_conceded'], axis=1).shape[1]*2


torch.manual_seed(1337)
conv1 = 16*2
conv2 = 32*2
conv3 = 64*2
conv4 = 128*2
n_hidden = 25

model = torch.nn.Sequential(
    torch.nn.Conv1d(1, conv1, kernel_size=inputs_per_match, stride=inputs_per_match), torch.nn.BatchNorm1d(conv1), torch.nn.Tanh(),
    torch.nn.Conv1d(conv1, conv2, kernel_size=2, stride=2), torch.nn.BatchNorm1d(conv2), torch.nn.Tanh(),
    torch.nn.Conv1d(conv2, conv3, kernel_size=2, stride=2), torch.nn.BatchNorm1d(conv3), torch.nn.Tanh(),
#     torch.nn.Conv1d(conv3, conv3, kernel_size=2, stride=2), torch.nn.BatchNorm1d(conv3), torch.nn.Tanh(),
    torch.nn.Flatten(),
    torch.nn.Linear(conv4, 3)
)

model.to('mps')

with torch.no_grad():
    model[-1].weight *= 0.1

parameters = [p for layer in model for p in layer.parameters()]
print(sum(p.nelement() for p in parameters))
for p in parameters:
    p.retain_grad()
    p.requires_grad = True


max_steps = 300000
batch_size = 32
lossi = []

for i in range(max_steps):
    
    ix = torch.randint(0, Xtr.shape[0], (32, ))
    X, Y = Xtr[ix], Ytr[ix]
    
    X = X[:, None, :]
    logits = model(X)
    loss = F.cross_entropy(logits, Y)
    
    # backward pass
    for p in parameters:
        p.grad = None
    loss.backward()
    
    # update weights
    lr = 0.1 if i < 50000 else 0.01
    for p in parameters:
        p.data += -lr * p.grad
        
    # track stats
    if i % 10000 == 0:
        print(f"{i:7d}/{max_steps:7d}: {loss.item():.4f}")
    lossi.append(loss.log10().item())

@torch.no_grad()
def split_loss(split):
    x, y = {
        'train': [Xtr, Ytr],
        'val'  : [Xdev, Ydev],
        'test' : [Xte, Yte]
    }[split]
    
    x = x[:, None, :]
    logits = model(x)
    loss = F.cross_entropy(logits, y)
    print(split, loss.item())

@torch.no_grad()
def accuracy(split):
    x, y = {
        'train': [Xtr, Ytr],
        'val'  : [Xdev, Ydev],
        'test' : [Xte, Yte]
    }[split]
    
    x = x[:, None, :]
    logits = model(x)
    preds = []
    preds = torch.argmax(logits, dim=1)

    i = 0
    for pred, true in zip(preds, y):
        if pred == true:
            i += 1
    
    print(f"----{split}----")
    print(f"Correctly predicted {i} out of {y.shape[0]} in {split}.")
    print(f"{i / y.shape[0]:.4f}")
    # print(f"Guessing would give an accuracy of {1 / len(torch.unique(y))}")

model.eval()
split_loss('train')
split_loss('val')

accuracy('train')
accuracy('val')

model.train()
split_loss('train')
split_loss('val')

accuracy('train')
accuracy('val')

# PATH = "trained_models/wavenet_10.pt"
# torch.save(model, PATH)

code.interact(local=locals())