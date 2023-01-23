"""
This file transforms the existing data for upload into the dashboard.
"""

import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
pd.options.mode.chained_assignment = None  # default='warn'


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
    df_past['league'] = df_past['league'].str.lower()
    df_past = df_past[df_future.iloc[:, :5].columns]
    df_scraped = pd.concat([df_past, df_future])[['team', 'opponent', 'league', 'home']]

    scraped_list = df_scraped[['team', 'opponent', 'league', 'home']].values.tolist()
    all_list = df_all.values.tolist()

    first_set = set(map(tuple, all_list))
    second_set = set(map(tuple, scraped_list))
    missing_matches = first_set.symmetric_difference(second_set)

    df_missing_matches = pd.DataFrame(list(missing_matches), columns=['team', 'opponent',
                                                                      'league', 'home'])
    df_missing_matches['date'] = '2023-05-06'

    df_future = pd.concat([df_future, df_missing_matches]).reset_index()
    df_future.drop(['index'], axis=1, inplace=True)

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
    df['date'] = pd.to_datetime(df['date'])
    df_home = df[df['home'] == 1]
    df_away = df[df['home'] == 0]
    if 'result' in df_away.columns:
        df_away.drop('result', axis=1, inplace=True)

    df_home.rename(columns={'team': 'home_team', 'opponent': 'away_team', 'elo_team': 'elo_home', 'elo_opponent': 'elo_away',
                            '0': 'A', '1': 'D', '2': 'H'}, inplace=True)
    df_away.rename(columns={'team': 'away_team', 'opponent': 'home_team', 'elo_team': 'elo_away', 'elo_opponent': 'elo_home',
                            '0': 'H', '1': 'D', '2': 'A'}, inplace=True)

    df_combined = pd.concat([df_home, df_away])
    df_combined = df_combined.groupby(['league', 'date', 'home_team', 'away_team', 'elo_home', 'elo_away']).mean()
    df_combined.reset_index(inplace=True, drop=False)
    if 'result' in df_combined.columns:
        df_combined.drop(['result'], axis=1, inplace=True)
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
                'result',
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

    df_combined.loc[df['result'] == 0, ['result']] = 'A'
    df_combined.loc[df['result'] == 0.5, ['result']] = 'D'
    df_combined.loc[df['result'] == 1, ['result']] = 'H'

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
    df_home_and_away.loc[df_home_and_away['result'] == 0, ['result']] = 'A'
    df_home_and_away.loc[df_home_and_away['result'] == 0.5, ['result']] = 'D'
    df_home_and_away.loc[df_home_and_away['result'] == 1, ['result']] = 'H'
    
    df_goals = df_goals[df_goals['home'] == 1]
    df_goals.drop('home', axis=1, inplace=True)
    df_goals.rename(columns={'team': 'home_team', 'opponent': 'away_team'}, inplace=True)
    df_home_and_away_goals = pd.merge(df_home_and_away, df_goals, on=['league',
                                                                    'date',
                                                                    'home_team',
                                                                    'away_team'],
                                                                how='left').sort_values(by=['date', 'home_team', 'away_team'])

    return df_home_and_away_goals


def limit_to_league(df, league, date=True):
    df = df[df['league'] == league]
    df.loc[:, 'league'] = df.loc[:, 'league'].str.lower()

    if date:
        start_date = pd.to_datetime("2022-07-30")
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].dt.date
        df = df[df['date'] >= start_date]

    return df


def drop_future(df, date):
    df = df[df['date']<date]
    return df


def write_df_to_gsheets(gsheet_name, tab_name, df):
    df = df.apply(lambda x: x.astype(str).str.title())
    df = df.apply(lambda x: x.astype(str).str.replace('_', ' '))
    df = df.apply(lambda x: x.astype(str).str.replace('Nan', ''))
    gc = gspread.service_account(filename='../../tools/gsheet_s4c_creds/italy-football-373515-95398f188c18.json')
    sh = gc.open(gsheet_name) 
    worksheet = sh.worksheet(tab_name)
    set_with_dataframe(worksheet, df)


all_matches = pd.read_csv("../../data/all_match_combinations.csv", index_col=0)
past_predictions = pd.read_csv("../../data/past_predictions.csv", index_col=0, parse_dates=['date'], dayfirst=False)
predictions = pd.read_csv("../../data/future_predictions.csv", index_col=0, parse_dates=['date'], dayfirst=False)
elos = pd.read_csv("../../data/elos_matches.csv", index_col=0, parse_dates=['date'], dayfirst=False)
goals = pd.read_csv("../../data/goals_matches.csv", index_col=0, parse_dates=['date'], dayfirst=False)
simulations = pd.read_csv("../../data/simulated_season.csv", index_col=0)
match_importance = pd.read_csv("../../data/match_importance.csv", index_col=0).dropna(axis=1, how='all')
streaks = pd.read_csv("../../data/dashboard_output/streaks.csv", index_col=0)
league_targets = pd.read_csv("../../data/dashboard_output/league_targets.csv", index_col=0)

future_date = predictions['date'][0]
elos = drop_future(elos, future_date)
goals = drop_future(goals, future_date)

all_matches = limit_to_league(all_matches, 'Serie C, Girone B', date=False)
predictions = limit_to_league(predictions, 'Serie C, Girone B')
elos = limit_to_league(elos, 'Serie C, Girone B')
goals = limit_to_league(goals, 'Serie C, Girone B')
simulations = limit_to_league(simulations, 'Serie C, Girone B', date=False)
match_importance = limit_to_league(match_importance, 'Serie C, Girone B', date=False)
past_predictions = limit_to_league(past_predictions, 'Serie C, Girone B')
past_predictions.drop(['result'], axis=1, inplace=True)
data_future = check_fixtures(elos, predictions, all_matches)
data_future = add_features_to_future(data_future, elos)

elos_preds = pd.concat([elos.set_index(['league', 'date', 'team', 'opponent', 'home']),
                        past_predictions.set_index(['league', 'date', 'team', 'opponent', 'home'])],
                        axis=1,
                        ).reset_index()
data_predictions_combined = pd.concat([elos_preds, data_future]).reset_index(drop=True)
data_predictions_home_and_away = transform_to_home_and_away(data_predictions_combined)
data_predictions_team_and_opponent = duplicate_data(data_predictions_home_and_away)
data_predictions_team_and_opponent_days = create_rest_days(data_predictions_team_and_opponent)

data_predictions_team_and_opponent_days = data_predictions_team_and_opponent_days[['league',
                                                                                  'date',
                                                                                  'team',
                                                                                  'opponent',
                                                                                  'elo_team',
                                                                                  'elo_opponent',
                                                                                  'loss',
                                                                                  'draw',
                                                                                  'win',
                                                                                  'home',
                                                                                  'rest_days',
                                                                                  'result',
                                                                                  ]]

data_goals_existing = goals.copy()
data_goals_existing = limit_to_recent(data_goals_existing, 10000)
data_goals_added_stats_removed = goals[['league',
                                        'date',
                                        'team', 
                                        'opponent',
                                        'team_goals_scored',
                                        'opponent_goals_scored',
                                        'home'
                                        ]]
data_goals_added_stats_removed['league'] = data_goals_added_stats_removed['league'].str.lower()

data_predictions_team_and_opponent_days['date'] = pd.to_datetime(data_predictions_team_and_opponent_days['date'])
data_goals_added_stats_removed['date'] = pd.to_datetime(data_goals_added_stats_removed['date'])
data_predictions_team_and_opponent_days_goals = data_predictions_team_and_opponent_days.merge(data_goals_added_stats_removed,
                                                                                                on=['league',
                                                                                                    'date',
                                                                                                    'team', 
                                                                                                    'opponent',
                                                                                                    'home'],
                                                                                                how='left').sort_values(by=['date', 'team', 'opponent'])

data_predictions_home_and_away_goals = combine_home_and_away_and_goals(data_predictions_home_and_away, data_goals_added_stats_removed)

elos_list = pd.read_csv('../../data/elos_list.csv')

elos_list.to_csv('../../data/dashboard_output/list_elos.csv')
simulations.to_csv('../../data/dashboard_output/simulations.csv')
match_importance.to_csv('../../data/dashboard_output/match_importance.csv')
data_predictions_home_and_away_goals.to_csv('../../data/dashboard_output/predictions_home_and_away.csv')
data_predictions_team_and_opponent_days_goals.to_csv('../../data/dashboard_output/predictions_team_and_opponent.csv')
data = [league_targets, data_predictions_home_and_away_goals, data_predictions_team_and_opponent_days_goals, elos_list, match_importance, simulations, streaks]
tabs = ['league_targets', 'preds_home_away_in', 'preds_team_opp_in', 'current_elos', 'match_importance', 'sim_season', 'streaks']

for i in range(len(data)):
    write_df_to_gsheets('i2_data', tabs[i], data[i])