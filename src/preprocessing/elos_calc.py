"""
Objective:
This file takes in all of the past match data and output pre-match ELO scores for the home and away side.
This file also produces a dataframe of teams and their current ELO at the time of running.
"""

import code
import numpy as np
import pandas as pd
import sqlite3


def set_up_data(df, past_data=True):
    df['elo_home'] = 0
    df['elo_away'] = 0
    df['elo_diff'] = 0
    df['prediction'] = 0
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['date'] = df['date'].dt.date
    df.sort_values(by='date', inplace=True)

    df.reset_index(inplace=True, drop=True)

    if past_data:
        df['correct'] = None

    df.reset_index(drop=True, inplace=True)
    print(f'Number of matches: {df.shape[0]}')

    return df


def get_team_list(df, start_rank):
    # Obtain a list of the teams we are looking at. This will be used to store a team's latest ELO data.
    team_list = pd.concat([df['pt1'], df['pt2']], axis=0).unique()
    team_list = pd.DataFrame(team_list)
    team_list.rename(columns={list(team_list)[0]: 'team'}, inplace=True)
    team_list.set_index('team', inplace=True)

    team_list['pts'] = start_rank
    team_list['last_played'] = pd.to_datetime('')
    team_list['league'] = 'E0'
    # team_list = pd.read_csv('Data/ELOs/Starting ELOs.csv', index_col='team')

    return team_list


def calculate_expected_result(rating, rating_opponent):
    expected_result = 1 / (1 + (10 ** ((rating_opponent - rating) / 400)))

    return expected_result


def update_elo(match_month, rating, actual_outcome, expected_outcome, k_factor1, k_factor2):
    if (match_month > 7) & (match_month < 10):
        new_rating = rating + k_factor1 * (actual_outcome - expected_outcome)
    else:
        new_rating = rating + k_factor2 * (actual_outcome - expected_outcome)

    return new_rating


def revert_mean(x):
    x2 = x * (1 - (x - 1500) / (1500) * 0.1)

    return x2


def change_league_revert(x, team_list1, div):
    team_list_div = team_list1[team_list1['league'] == div]
    if team_list_div.empty:
        new_league_avg = 1500
    else:
        new_league_avg = team_list_div['pts'].mean()
    x2 = x * (1 - (x - new_league_avg) / (new_league_avg) * 0.1)
    # print('Promotion/Relegation Reversion')

    return x2


def check_div_change(div, team_list, home_team, away_team):
    # Promotion/Relegation Adjustment
    if div != team_list.loc[home_team, 'league']:
        revert_rating = change_league_revert(team_list.loc[home_team, 'pts'], team_list, div)
        team_list.loc[home_team, 'pts'] = revert_rating
    if div != team_list.loc[away_team, 'league']:
        revert_rating = change_league_revert(team_list.loc[away_team, 'pts'], team_list, div)
        team_list.loc[away_team, 'pts'] = revert_rating

    return team_list


def check_and_set_date(date, previous_match, team_list, team, rating):
    # print(date)
    # print(previous_match)
    # if (date - previous_match).days > 200:
    #     team_list.loc[team, 'pts'] = rating

    team_list.loc[team, 'last_played'] = date

    return team_list


def check_result(result):
    if result == 1:
        result = 1
    elif result == 0:
        result = 0
    else:
        result = 0.5

    result_away = 1 - result

    return result, result_away


def get_result(row):
    if row['score_pt1'] > row['score_pt2']:
      return 1
    elif row['score_pt1'] < row['score_pt2']:
      return 0
    else:
      return 0.5


def make_prediction(elo1, home_advantage_, elo2):
    if elo1 + home_advantage_ > elo2:
        return 1
    elif elo1 + home_advantage_ < elo2:
        return 0
    else:
        return 0.5


def check_prediction(prediction, result):
    if prediction == result:
        return 1
    else:
        return 0


def calc_elos(row, kfactor_start, kfactor_rest, home_advantage):
    global teams
    home_team = row['pt1']
    away_team = row['pt2']

    match_date = row['date']
    match_date_month = match_date.month

    home_last_game = teams.loc[home_team, 'last_played']
    away_last_game = teams.loc[away_team, 'last_played']

    div = row['league']

    teams = check_div_change(div, teams, home_team, away_team)
    teams.loc[home_team, 'league'] = div
    teams.loc[away_team, 'league'] = div

    teams = check_and_set_date(match_date, home_last_game, teams, home_team, new_team_rating)
    teams = check_and_set_date(match_date, away_last_game, teams, away_team, new_team_rating)

    home_elo = teams.loc[home_team, 'pts']
    away_elo = teams.loc[away_team, 'pts']

    row['elo_home'] = home_elo
    row['elo_away'] = away_elo
    row['elo_diff'] = home_elo - away_elo

    home_result, away_result = check_result(row['result'])

    expected_result_home = calculate_expected_result(home_elo, away_elo)
    expected_result_away = calculate_expected_result(away_elo, home_elo)

    home_elo_new = update_elo(match_date_month, home_elo, home_result, expected_result_home, kfactor_start,
                              kfactor_rest)
    away_elo_new = update_elo(match_date_month, away_elo, away_result, expected_result_away, kfactor_start,
                              kfactor_rest)

    teams.loc[home_team, 'pts'] = home_elo_new
    teams.loc[away_team, 'pts'] = away_elo_new

    row['prediction'] = make_prediction(home_elo, home_advantage, away_elo)
    row['correct'] = check_prediction(row['prediction'], home_result)

    # if row.name % 2000 == 0:
    #     teams['Pts'] = teams['Pts'].apply(lambda x: revert_mean(x))
    #     print('Mean Reverted')

    if row.name % 5000 == 0:
        print(row.name, 'matches calculated.')

    return row


def update_elos(row, home_advantage):
    global teams
    home_team = row['pt1']
    away_team = row['pt2']

    match_date = row['date']

    home_last_game = teams.loc[home_team, 'last_played']
    away_last_game = teams.loc[away_team, 'last_played']

    teams = check_and_set_date(match_date, home_last_game, teams, home_team, new_team_rating)
    teams = check_and_set_date(match_date, away_last_game, teams, away_team, new_team_rating)

    home_elo = teams.loc[home_team, 'pts']
    away_elo = teams.loc[away_team, 'pts']

    row['elo_home'] = home_elo
    row['elo_away'] = away_elo
    row['prediction'] = make_prediction(home_elo, home_advantage, away_elo)

    return row   


def display_stats(df):
    print('Percentage Correct:', df['correct'].sum() / len(df['correct']))

    home_wins = df[df['result'] == '1']
    away_wins = df[df['result'] == '0']
    draws = df[df['result'] == '0.5']
    print('Home wins predicted correctly:', len(home_wins[home_wins['correct'] == 1]) / len(df))
    print('Away wins predicted correctly:', len(away_wins[away_wins['correct'] == 1]) / len(df))
    print('Draws predicted correctly:', len(draws[draws['correct'] == 1]) / len(df))
    
    test = df[int(len(df) / 2):]
    print('Percentage Correct in test set:', test['correct'].sum() / len(test['correct']))
    
    home_wins = test[test['result'] == '1']
    away_wins = test[test['result'] == '0']
    draws = test[test['result'] == '0.5']
    print('Home wins predicted correctly in test set:', len(home_wins[home_wins['correct'] == 1]) / len(test))
    print('Away wins predicted correctly in test set:', len(away_wins[away_wins['correct'] == 1]) / len(test))
    print('Draws predicted correctly in test set:', len(draws[draws['correct'] == 1]) / len(test))


def duplicate_to_team_and_opponent(df):
    df = df[['league', 'date', 'pt1', 'pt2', 'result', 'elo_home', 'elo_away', 'elo_diff']]
    # df['result'] = df.apply(lambda x: update_FTR(x), axis=1)

    df_copy = df.copy()
    df = df.rename(columns={'pt1': 'team', 'pt2': 'opponent', 'elo_home': 'elo_team',
                            'elo_away': 'elo_opponent'})
    df_copy = df_copy.rename(columns={'pt2': 'team', 'pt1': 'opponent', 'elo_away': 'elo_team',
                            'elo_home': 'elo_opponent'})
    # print(df_copy.head())
    df_copy['elo_diff'] = df_copy['elo_diff'] * -1
    df_copy['result'] = 1 - df_copy['result']
    df_copy = df_copy[['league', 'date', 'team', 'opponent', 'result', 'elo_team', 'elo_opponent', 'elo_diff'
                        ]]
    df.loc[:, 'home'] = 1
    df_copy.loc[:, 'home'] = 0
    df = pd.concat([df, df_copy])
    df.sort_values(by='date', inplace=True)

    return df


def update_FTR(row):
    if row['result'] == '1':
        return 1
    elif row['result'] == '0':
        return 0
    else:
        return 0.5


def load_past_matches():
    df = pd.read_csv('../data/football_matches_a.csv', dtype={'manager_pt1': str, 'manager_pt2': str}, parse_dates=['date'])
    df.drop('Unnamed: 0', axis=1, inplace=True)

    return df


data = load_past_matches()
data = set_up_data(data)
print(data.shape)
data['result'] = data.apply(lambda x: get_result(x), axis=1)

# TEST DATA
# data = data[-1000:]
data.dropna(subset=['pt1'], inplace=True)
data.reset_index(inplace=True, drop=True)

# Initial Values
elo = 1500
kfactor_quick = 40
kfactor_slow = 30
home_ad = 50
new_team_rating = 1500

# Setting the starting rank for all teams
teams = get_team_list(data, elo)
print('Calculating ELOs...')
data = data.apply(lambda row: calc_elos(row, kfactor_quick, kfactor_slow, home_ad), axis=1)
data = duplicate_to_team_and_opponent(data)
# teams['league'] = teams['league'].map(lambda x: x.lower() if isinstance(x,str) else x)
# save_elos_to_db(teams)
# save_past_matches_to_db(data)
# print(data.tail())
data.to_csv('../data/elos_matches.csv')
teams.to_csv('../data/elos_list.csv')

# code.interact(local=locals())
# # To update the elos daily and much faster, we can compare the date of the match to the 'last played' date and only update if the match is after the last_played value.