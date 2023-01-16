"""
This file contains the code for running a monte_carlo simulation over the rest of the league season.
"""


import sys
sys.path.append("..")

import pandas as pd
import numba as nb
import numpy as np
from random import choices


def run_simulation(row, simulations, population):
    global results
    global i
    weights = [row['A'], row['D'], row['H']]
    weights = np.array(weights)
    weights /= weights.sum()
    if i == 0:
        i+=1
    else:
        # simulations_list = choices(population, weights, k=simulations)
        simulations_list = np.random.choice(population, size=simulations, p=weights)
        results.append(simulations_list)

    return row


def monte_carlo(df, simulations, population):
    df_copy = df.copy()
    df_copy = df_copy.apply(lambda x: run_simulation(x, no_simulations, points), axis=1)
    column_names = get_season_names(simulations)
    df_results = pd.DataFrame(results, columns=column_names)
    df_monte_carlo = pd.merge(df_copy, df_results, left_index=True, right_index=True)

    return df_monte_carlo


def get_season_names(no_simulations):
    column_names = ['season_' + str(s) for s in range(no_simulations)]
    
    return column_names


def get_finishing_positions(df, simulations):
    df_finishing_positions = df.groupby(['league', 'team']).sum(numeric_only=True)
    df_finishing_positions.reset_index(inplace=True)
    # The df above is a df of each simulated season and the number of points each team got.
    column_names = get_season_names(simulations)
    no_teams = len(df_finishing_positions)
    ranking = pd.DataFrame(range(0, no_teams), columns=['Lineup'])
    ranking = pd.concat([ranking, pd.DataFrame(fastRanks(df_finishing_positions[column_names].to_numpy()))], axis=1)
    simulated_season= ranking.apply(pd.Series.value_counts, axis=1)
    simulated_season['team'] = df_finishing_positions['team']
    simulated_season['league'] = df_finishing_positions['league']
    simulated_season.drop(0, axis=1, inplace=True)

    return simulated_season


def get_finishing_positions_importance(df, column_names):
    df_finishing_positions = df.groupby(['league', 'team']).sum(numeric_only=True)
    df_finishing_positions.reset_index(inplace=True)
    # The df above is a df of each simulated season and the number of points each team got.
    # column_names = get_season_names(simulations)
    no_teams = len(df_finishing_positions)
    ranking = pd.DataFrame(range(0, no_teams), columns=['Lineup'])
    ranking = pd.concat([ranking, pd.DataFrame(fastRanks(df_finishing_positions[column_names].to_numpy()))], axis=1)
    simulated_season= ranking.apply(pd.Series.value_counts, axis=1)
    simulated_season['team'] = df_finishing_positions['team']
    simulated_season['league'] = df_finishing_positions['league']
    simulated_season.drop(0, axis=1, inplace=True)

    return simulated_season


@nb.njit('int64[:,:](int64[:,:])', parallel=True)
def fastRanks(df):
    n, m = df.shape
    res = np.empty((n, m), dtype=np.int64)

    for col in nb.prange(m):
        dfCol = -df[:, col]
        order = np.argsort(dfCol)

        # Compute the ranks with the min method
        if n > 0:
            prevVal = dfCol[order[0]]
            prevRank = 1
            res[order[0], col] = 1

            for row in range(1, n):
                curVal = dfCol[order[row]]
                if curVal == prevVal:
                    res[order[row], col] = prevRank
                else:
                    res[order[row], col] = row + 1
                    prevVal = curVal
                    prevRank = row + 1

    return res


def merge_on_common_columns(df1, df2):
    common_columns = list(set(df1.columns).intersection(df2.columns))

    df = pd.merge(df1, df2, on=common_columns)

    return df


def get_single_match(df, past_or_future):
    df_home = df[df['home'] == 1].drop('home', axis=1)
    df_away = df[df['home'] == 0].drop('home', axis=1)
    if past_or_future:
        df_home.rename(columns={'team': 'home', 'opponent': 'away', '0': 'A', '1': 'D', '2': 'H'}, inplace=True)
        df_away.rename(columns={'opponent': 'home', 'team': 'away', '0': 'H', '1': 'D', '2': 'A'}, inplace=True)
    else:
        df_home.rename(columns={'team': 'home', 'opponent': 'away'}, inplace=True)
        df_away.rename(columns={'opponent': 'home', 'team': 'away'}, inplace=True)

    columns = df_home.columns.values.tolist()
    df = pd.concat([df_home, df_away], sort=False)
    df = df[columns]

    df_group = df.groupby(['date', 'league', 'home', 'away']).mean()
    df_group.reset_index(inplace=True)

    return df_group


def duplicate_to_team_and_opponent(df_matches):
    df_matches = df_matches[['league', 'date', 'home', 'away', 'home_score', 'away_score']]
    df_matches['home_conceded'] = df_matches['away_score']
    df_matches['away_conceded'] = df_matches['home_score']

    df_matches_copy = df_matches.copy()
    df_matches = df_matches.rename(columns={'home': 'team', 'away': 'opponent', 'home_score': 'team_goals_scored',
                                            'away_score': 'opponent_goals_scored', 'home_conceded': 'team_goals_conceded',
                                            'away_conceded': 'opponent_goals_conceded'})
    df_matches_copy = df_matches_copy.rename(columns={'away': 'team', 'home': 'opponent', 'away_score': 'team_goals_scored',
                                            'home_score': 'opponent_goals_scored', 'away_conceded': 'team_goals_conceded',
                                            'home_conceded': 'opponent_goals_conceded'})
    df_matches_copy = df_matches_copy[['league', 'date', 'team', 'opponent', 'team_goals_scored', 'opponent_goals_scored', 'team_goals_conceded', 'opponent_goals_conceded',
                        ]]
    df_matches.loc[:, 'home'] = 1
    df_matches_copy.loc[:, 'home'] = 0
    df_matches = df_matches.append(df_matches_copy)
    df_matches.sort_values(by='date', inplace=True)
    df_matches.reset_index(inplace=True, drop=True)

    return df_matches


# def convert_league_to_div_in_df(df):
#     league_dict = {'premier-league': 'e0',
#                     'championship': 'e1',
#                     'league-1': 'e2',
#                     'league-2': 'e3'}

#     df['competition'].replace(league_dict, inplace=True)
#     df.rename(columns={'competition': 'div'}, inplace=True)
    
#     return df


def cut_to_current_year_and_league(df, year, league):
    df = df[df['date'] >= f'{year}-07-15']
    df = df[df['league'] == league]
    df.reset_index(inplace=True, drop=True)

    return df


def get_points_match(row):
    if row['team_goals_scored'] > row['opponent_goals_scored']:
        return 3
    elif row['team_goals_scored'] < row['opponent_goals_scored']:
        return 0
    else:
        return 1


def get_points(df):
    # Column called season rather than points as this will be replicated x times for each simulted season
    df['season'] = df.apply(lambda x: get_points_match(x), axis=1)

    return df[['league', 'date', 'team', 'opponent', 'home', 'season']]


def add_simulated_season_for_past(df, simulations):
    df_copy = df.copy()
    df.drop('season', axis=1, inplace=True)
    df_copy = df_copy[['season']]
    df_season = df_copy[df_copy.columns.repeat(simulations)]
    df_season.columns = [f'{a}{b}' for a in df_copy
                            for b in ['']+[f'_{x+1}' for x in range(0,simulations-1)]]
    df_season = df_season.rename(columns={'season': 'season_0'})

    df_combined = pd.merge(df, df_season, left_index=True, right_index=True)

    return df_combined


def combined_past_and_future(df_past, df_future):
    df_future = df_future.drop(['A', 'D', 'H'], axis=1)
    # df_past = get_single_match(df_past, False)

    df = pd.concat([df_past, df_future])[df_past.columns.tolist()]
    df.reset_index(inplace=True, drop=True)

    return df


def split_to_team_and_opponent(df_future):
    df_copy = df_future.copy()

    df_future.rename(columns={'home': 'team',
                            'away': 'opponent'}, inplace=True)
    df_copy.rename(columns={'home': 'opponent',
                            'away': 'team'}, inplace=True)

    df_future.loc[:, 'home'] = 1
    df_copy.loc[:, 'home'] = 0

    away_columns = df_copy.columns.values.tolist()
    away_dict = {0: 3, 1: 1, 3: 0}
    for column in away_columns:
        if any(substring in column for substring in ['season']):
            df_copy[column] = df_copy[column].map(away_dict)

    df_future = pd.concat([df_future, df_copy])[df_future.columns.tolist()]
    # df_future = df_future.append(df_copy)[df_future.columns.tolist()]

    return df_future


def max_teams(df_future, df_past):
    if len(df_future) > len(df_past):
        divs = sorted(df_future['league'].unique())
        max_teams = 0
        for div in divs:
            current_teams = len(df_future[df_future['league']==div]['team'].unique())
            if current_teams > max_teams:
                max_teams = current_teams
    else:
        divs = sorted(df_past['league'].unique())
        max_teams = 0
        for div in divs:
            current_teams = len(df_past[df_past['league']==div]['team'].unique())
            if current_teams > max_teams:
                max_teams = current_teams

    return max_teams


def get_next_match_date(df_future, team_selected):
    df_future = df_future.sort_values(by='date')
    df_future = df_future[df_future['team'] == team_selected]
    df_future.reset_index(inplace=True, drop=True)
    next_match_date = pd.to_datetime(df_future['date'].dt.date[0])

    return next_match_date


def result_importance(next_match, df_sim, team, result, simulations):
    df_sim_team = df_sim[(df_sim['team'] == team)]
    df_sim_next_match = df_sim_team[(df_sim_team['date'] == next_match)]
    df_sim_match = df_sim_team[['league', 'date', 'team', 'opponent']]
    df_sim_team = df_sim_team.drop(['league', 'date', 'team', 'opponent'], axis=1)
    df_sim_team = df_sim_team.loc[:, (df_sim_next_match == result).any()]
    columns = df_sim_team.columns
    df_sim_team = pd.concat([df_sim_match, df_sim_team], axis=1)
    df_sim = df_sim[df_sim_team.columns]

    df_finishing_positions = get_finishing_positions_importance(df_sim, columns)

    return df_finishing_positions[df_finishing_positions['team']==team]


def get_match_importance(df_sim, df_future, team, simulations):
    next_match_date = get_next_match_date(df_future, team)
    win_positions = result_importance(next_match_date, df_sim, team, 3, simulations)
    draw_positions = result_importance(next_match_date, df_sim, team, 1, simulations)
    loss_positions = result_importance(next_match_date, df_sim, team, 0, simulations)

    win = get_groupings(win_positions, win_positions.iloc[0]['league'])
    draw = get_groupings(draw_positions, draw_positions.iloc[0]['league'])
    loss = get_groupings(loss_positions, loss_positions.iloc[0]['league'])

    importance_list = [team] + win + draw + loss

    # if win_positions.iloc[0]['div'] == 'e0':
    #     df_finishing_positions = pd.DataFrame([win, draw, loss], columns=['winner', 'champions_league', 'europa_league',
    #                                                                       'midtable', 'at_risk', 'relegation'])
    # else:
    #     df_finishing_positions = pd.DataFrame([win, draw, loss], columns=['promotion', 'playoffs', 'high_midtable',
    #                                                                         'low_midtable', 'at_risk', 'relegation'])

    # df_finishing_positions['result'] = pd.Series(['win', 'draw', 'loss'])
    # cols = df_finishing_positions.columns.tolist()
    # cols = cols[-1:] + cols[:-1]
    # df_finishing_positions = df_finishing_positions[cols]

    return importance_list


def get_groupings(df, league):
    df.fillna(0, inplace=True)
    total_simulations = df.sum(axis=1, numeric_only=True)

    if league == 'Serie C, Girone B':
        winning_chances = ((df.loc[:][1]) / total_simulations)
        second_fifth = ((df.loc[:][2]) +
                        (df.loc[:][3]) +
                        (df.loc[:][4]) +
                        (df.loc[:][5]) ) / total_simulations
        sixth_ninth = ((df.loc[:][6]) +
                       (df.loc[:][7]) +
                       (df.loc[:][8]) +
                       (df.loc[:][9]) ) / total_simulations
        tenth_fourteenth = ((df.loc[:][10]) +
                            (df.loc[:][11]) +
                            (df.loc[:][12]) +
                            (df.loc[:][13]) +
                            (df.loc[:][14]) ) / total_simulations
        at_risk = ((df.loc[:][15]) +
                    (df.loc[:][16]) +
                    (df.loc[:][17])) / total_simulations
        relegation = ((df.loc[:][18]) +
                    (df.loc[:][19]) +
                    (df.loc[:][20])) / total_simulations

        return [winning_chances.values[0], second_fifth.values[0], sixth_ninth.values[0], tenth_fourteenth.values[0], at_risk.values[0], relegation.values[0]]

    else:
        print("Error, league name incorrect.")
        # promotion_chances = ((df.loc[:][1]) +
        #                     (df.loc[:][2])) / total_simulations
        # playoffs = ((df.loc[:][3]) +
        #             (df.loc[:][4]) +
        #             (df.loc[:][5]) +
        #             (df.loc[:][6]) )/ total_simulations
        # high_midtable = ((df.loc[:][7]) +
        #                 (df.loc[:][8]) +
        #                 (df.loc[:][9]) +
        #                 (df.loc[:][10]) +
        #                 (df.loc[:][11]) +
        #                 (df.loc[:][12])) / total_simulations
        # low_midtable = ((df.loc[:][13]) +
        #                 (df.loc[:][14]) +
        #                 (df.loc[:][15]) +
        #                 (df.loc[:][16]) +
        #                 (df.loc[:][17]) +
        #                 (df.loc[:][18]) ) / total_simulations
        # at_risk = ((df.loc[:][19]) +
        #             (df.loc[:][20]) +
        #             (df.loc[:][21])) / total_simulations
        # relegation = ((df.loc[:][22]) +
        #             (df.loc[:][23]) +
        #             (df.loc[:][24])) / total_simulations

        # return [promotion_chances.values[0], playoffs.values[0], high_midtable.values[0], low_midtable.values[0], at_risk.values[0], relegation.values[0]]


def lists_of_positions_to_df(lists_of_positions, league):
    if league == 'Serie C, Girone B':
        df_all_positions = pd.DataFrame(lists_of_positions,
                                        columns=['Team',
                                                 'Winner - Win', 'Second:Fifth - Win', 'Sixth:Ninth - Win',
                                                 'Tenth:Fourteenth - Win', 'At Risk - Win', 'Relegation - Win',
                                                 'Winner - Draw', 'Second:Fifth - Draw', 'Sixth:Ninth - Draw',
                                                 'Tenth:Fourteenth - Draw', 'At Risk - Draw', 'Relegation - Draw',
                                                 'Winner - Loss', 'Second:Fifth - Loss', 'Sixth:Ninth - Loss',
                                                 'Tenth:Fourteenth - Loss', 'At Risk - Loss', 'Relegation - Loss'])
    else:
        print("Error, league name incorrect for finishing positions.")
        # df_all_positions = pd.DataFrame(lists_of_positions,
        #                                 columns=['Team',
        #                                      'Promotion - Win', 'Playoffs - Win', 'High Midtable - Win',
        #                                      'Low Midtable - Win', 'At Risk - Win', 'Relegation - Win',
        #                                      'Promotion - Draw', 'Playoffs - Draw', 'High Midtable - Draw',
        #                                      'Low Midtable - Draw', 'At Risk - Draw', 'Relegation - Draw',
        #                                      'Promotion - Loss', 'Playoffs - Loss', 'High Midtable - Loss',
        #                                      'Low Midtable - Loss', 'At Risk - Loss', 'Relegation - Loss'])

    return df_all_positions


data_future = pd.read_csv("../../data/future_predictions.csv", index_col=0, parse_dates=['date'], dayfirst=False)
data_past = pd.read_csv("../../data/joined_matches.csv", index_col=0, parse_dates=['date'], dayfirst=False)
data_past = cut_to_current_year_and_league(data_past, '2022', 'Serie C, Girone B')

data_future['league'] = 'Serie C, Girone B'
divs = data_future['league'].unique()
points = [0, 1, 3]
no_simulations = 10**3
max_teams = max_teams(data_future, data_past)
positions = list(range(0, int(max_teams+1)))
finishing_positions_combined = pd.DataFrame(columns=['league', 'team'] + positions)
data_match_importance_all_divs = pd.DataFrame(columns=[
                                                        'Team',
                                                        'Winner - Win',
                                                        'Second:Fifth - Win',
                                                        'Sixth:Ninth - Win',
                                                        'Tenth:Fourteenth - Win',
                                                        'At Risk - Win',
                                                        'Relegation - Win',
                                                        'Winner - Draw',
                                                        'Second:Fifth - Draw',
                                                        'Sixth:Ninth - Draw',
                                                        'Tenth:Fourteenth - Draw',
                                                        'At Risk - Draw',
                                                        'Relegation - Draw',
                                                        'Winner - Loss',
                                                        'Second:Fifth - Loss',
                                                        'Sixth:Ninth - Loss',
                                                        'Tenth:Fourteenth - Loss',
                                                        'At Risk - Loss',
                                                        'Relegation - Loss',
                                                        'League'
                                                            ])

for div in divs:
    data_past_div = data_past[data_past['league'] == div]
    data_future_div = data_future[data_future['league'] == div]
    # data_past_div = duplicate_to_team_and_opponent(data_past_div)
    data_past_div = get_points(data_past_div)
    results = []
    i = 0
    data_past_div = add_simulated_season_for_past(data_past_div, no_simulations)
    data_future_div = get_single_match(data_future_div, True)
    data_future_div = monte_carlo(data_future_div, no_simulations, points)

    data_future_div = split_to_team_and_opponent(data_future_div)
    data_div = combined_past_and_future(data_past_div, data_future_div)
    data_finishing_positions = get_finishing_positions(data_div, no_simulations)
    finishing_positions_combined = pd.concat([finishing_positions_combined, data_finishing_positions])

    data_match_importance_all = []
    teams = data_div['team'].unique()
    teams.sort()
    for team in teams:
        data_match_importance = get_match_importance(data_div, data_future, team, no_simulations)
        data_match_importance_all.append(data_match_importance)

    data_match_importance_all_teams = lists_of_positions_to_df(data_match_importance_all, div)
    data_match_importance_all_teams['league'] = div
    data_match_importance_all_divs = pd.concat([data_match_importance_all_divs, data_match_importance_all_teams])

[data_match_importance_all_divs.columns.tolist()]
finishing_positions_combined.drop(0, axis=1, inplace=True)

data_match_importance_all_divs.to_csv("../../data/match_importance.csv")
finishing_positions_combined.to_csv('../../data/simulated_season.csv')