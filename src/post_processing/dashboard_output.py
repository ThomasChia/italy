"""
This file transforms the existing data for upload into the dashboard.
"""


import pandas as pd


def add_features_to_future(df_future, df_features):

    df_features_team = get_final_entry(df_features, 'team')
    df_features_opponent = team_to_opponent(df_features_team)
    df_future = pd.merge(df_future, df_features_team, how='left', on='team')
    df_future = pd.merge(df_future, df_features_opponent, how='left', on='opponent')
    df_future['elo_diff'] = df_future['elo_team'] - df_future['elo_opponent']
    df_future['date'] = pd.to_datetime(df_future['date'])
    df_future['date'] = df_future['date'].dt.date

    return df_future


def check_fixtures(df_past, df_future, df_all):
    df_past['div'] = df_past['div'].str.lower()
    df_past = df_past[df_future.iloc[:, :5].columns]
    df_scraped = df_past.append(df_future, sort=True)[['team', 'opponent', 'div', 'home']]

    scraped_list = df_scraped[['team', 'opponent', 'div', 'home']].values.tolist()
    all_list = df_all.values.tolist()
    # print(len(scraped_list))
    # print(len(all_list))

    first_set = set(map(tuple, all_list))
    second_set = set(map(tuple, scraped_list))
    missing_matches = first_set.symmetric_difference(second_set)

    df_missing_matches = pd.DataFrame(list(missing_matches), columns=['team', 'opponent',
                                                                      'league', 'home'])
    df_missing_matches['date'] = '2023-05-06'

    df_future = df_future.append(df_missing_matches, sort=False).reset_index()
    df_future.drop(['index'], axis=1, inplace=True)
    # print('df_past length:', df_past.shape[0])
    # print('df_future length:', df_future.shape[0])


    return df_future


def team_to_opponent(df):
    df_opponent = df.copy()
    df_opponent.columns = df_opponent.columns.str.replace("team", "opponent")

    return df_opponent


def get_final_entry(df, team_or_opponent):
    df = df.sort_values(by='date')
    df = df.reset_index(drop=True)
    df = df.drop_duplicates(subset=team_or_opponent, keep='last')
    df = df.loc[:, df.columns.str.contains(team_or_opponent)]

    return df


def transform_to_home_and_away(df):
    df_home = df[df['home'] == 1]
    df_away = df[df['home'] == 0]
    if 'FTR' in df_away.columns:
        df_away.drop('FTR', axis=1, inplace=True)

    df_home.rename(columns={'team': 'home_team', 'opponent': 'away_team', 'elo_team': 'elo_home', 'elo_opponent': 'elo_away',
                            '0': 'A', '1': 'D', '2': 'H'}, inplace=True)
    df_away.rename(columns={'team': 'away_team', 'opponent': 'home_team', 'elo_team': 'elo_away', 'elo_opponent': 'elo_home',
                            '0': 'H', '1': 'D', '2': 'A'}, inplace=True)

    df_combined = df_home.append(df_away, sort=False)
    df_combined = df_combined.groupby(['league', 'date', 'home_team', 'away_team', 'elo_home', 'elo_away']).mean()
    df_combined.reset_index(inplace=True, drop=False)
    if 'FTR' in df_combined.columns:
        df_combined.drop(['FTR'], axis=1, inplace=True)
    df_combined['elo_diff'] = df_combined['elo_home'] - df_combined['elo_away']

    if 'team_goals_scored' not in df_home.columns:
        df_ftr = df_home.drop(['A', 'D', 'H', 'elo_diff', 'elo_home', 'elo_away', 'home'], axis=1)
        df_ftr['date'] = pd.to_datetime(df_ftr['date'])
    else:
        df_ftr = df_home.drop(['loss', 'draw', 'win', 'rest_days', 'team_goals_scored', 'opponent_goals_scored', 'elo_home', 'elo_away', 'home'], axis=1)
        df_ftr['date'] = pd.to_datetime(df_ftr['date'])

    df_combined = df_combined.merge(df_ftr, on=['league', 'date', 'home_team', 'away_team'], how='outer'
                                    )

    return df_combined


def duplicate_data(df):
    df_home = df[[
                'league',
                'date',
                'home_team',
                'away_team',
                'elo_home',
                'elo_away',
                'A',
                'D',
                'H',
                'FTR',
                ]]

    df_away = df_home.copy()
    df_home.rename(columns={
                        'home_team': 'team',
                        'away_team': 'opponent',
                        'elo_home': 'elo_team',
                        'elo_away': 'elo_opponent',
                        'A': 'loss',
                        'D': 'draw',
                        'H': 'win',
                        }, inplace=True)
    df_home['home'] = 1

    df_away.rename(columns={
        'home_team': 'opponent',
        'away_team': 'team',
        'elo_home': 'elo_opponent',
        'elo_away': 'elo_team',
        'A': 'win',
        'D': 'draw',
        'H': 'loss',
    }, inplace=True)
    df_away['home'] = 0

    df_combined = pd.concat([df_home, df_away])

    df_combined.loc[df['FTR'] == 0, ['FTR']] = 'A'
    df_combined.loc[df['FTR'] == 0.5, ['FTR']] = 'D'
    df_combined.loc[df['FTR'] == 1, ['FTR']] = 'H'

    return df_combined


def get_team_list(df):
    team_list = df['team'].unique()
    team_list = pd.DataFrame(team_list)
    team_list.rename(columns={list(team_list)[0]: 'teams'}, inplace=True)
    team_list.set_index('teams', inplace=True)

    return team_list


def create_rest_days(df):
    team_list = get_team_list(df)
    team_list['last_played'] = pd.to_datetime('2022-05-28')
    df['rest_days'] = 0
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)
    # print(df.head())

    for index, row in df.iterrows():
        team = row['team']
        # print(team)
        # print(row['Date'])
        # print(team_list.loc[team, 'Last Played'])
        # print((row['Date'] - team_list.loc[team, 'Last Played']).days)
        df.loc[index, 'rest_days'] = (row['date'] - team_list.loc[team, 'last_played']).days
        # print(row['Rest Days'])
        team_list.loc[team, 'last_played'] = row['date']

    return df

def limit_to_recent(df, matches_limit):
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)
    df = df[-matches_limit:]

    return df

def combine_home_and_away_and_goals(df_home_and_away, df_goals):
    df_home_and_away.loc[df_home_and_away['FTR'] == 0, ['FTR']] = 'A'
    df_home_and_away.loc[df_home_and_away['FTR'] == 0.5, ['FTR']] = 'D'
    df_home_and_away.loc[df_home_and_away['FTR'] == 1, ['FTR']] = 'H'
    
    df_goals = df_goals[df_goals['home'] == 1]
    df_goals.drop('home', axis=1, inplace=True)
    df_goals.rename(columns={'team': 'home_team', 'opponent': 'away_team'}, inplace=True)
    df_home_and_away_goals = pd.merge(df_home_and_away, df_goals, on=['div',
                                                                    'date',
                                                                    'home_team',
                                                                    'away_team'],
                                                                how='left').sort_values(by=['date', 'home_team', 'away_team'])

    return df_home_and_away_goals


predictions = pd.read_csv("../../data/future_predictions.csv", index_col=0)
elos = pd.read_csv("../../data/elos_matches.csv", index_col=0)
goals = pd.read_csv("../../data/goals_matches.csv", index_col=0)
simulations = pd.read_csv("../../data/simulated_season.csv", index_col=0)
match_importance = pd.read_csv("../../data/match_importance.csv", index_col=0).dropna(axis=1, how='all')

elos['league'] = elos['league'].str.lower()
