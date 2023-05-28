import config
import numpy as np
import pandas as pd
import logging


class Elo:
    def __init__(self, matches):
        self.matches: pd.DataFrame = matches
        self.elo_tracker = EloTracker(matches)
        self.team_and_opp_matches = pd.DataFrame()

    def calculate(self):
        self.calc_all_elos()
        self.get_team_and_opp_matches()

    def calc_all_elos(self):
        self.matches = self.matches.apply(lambda x: self.calc_elos(x), axis=1)

    def calc_elos(self, row):
        row_data = RowData(row, self.elo_tracker)

        self.update_league(row_data)
        self.check_and_set_date(row_data)

        row['elo_home'] = row_data.home_team_elo
        row['elo_away'] = row_data.away_team_elo
        row['elo_diff'] = row_data.home_team_elo - row_data.away_team_elo

        expected_result_home = self.calculate_expected_result(row_data.home_team_elo,
                                                              row_data.away_team_elo)
        expected_result_away = self.calculate_expected_result(row_data.away_team_elo,
                                                              row_data.home_team_elo)
        
        self.update_elos(row_data, expected_result_home, expected_result_away)

        if row.name % 5000 == 0:
            logging.info(f'{row.name} matches calculated.')

        return row

    def set_up_data(self):
        self.matches['elo_home'] = 0
        self.matches['elo_away'] = 0
        self.matches['elo_diff'] = 0
        self.matches['prediction'] = 0
        self.matches['date'] = pd.to_datetime(self.matches['date'], dayfirst=True)
        self.matches['date'] = self.matches['date'].dt.date
        self.sort_by_date(self.matches)
    
    def sort_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(by='date')
        df = df.reset_index(drop=True)
        return df
    
    def get_league_elos(self, league):
        return self.elo_tracker.tracker[self.elo_tracker.tracker['league'] == league]
    
    def get_league_average(self, league):
        league_elos = self.get_league_elos(league)
        if league_elos.empty:
            league_average = config.STARTING_ELO
        else:
            league_average = league_elos['pts'].mean()
        return league_average

    def changed_league_modification(self, row_data, home_team=True):
        league_average = self.get_league_average(row_data.league)
        if home_team:
            modified_rating = row_data.home_team_elo * (1 - (row_data.home_team_elo - league_average) / (league_average) * 0.1)
        else:
            modified_rating = row_data.away_team_elo * (1 - (row_data.away_team_elo - league_average) / (league_average) * 0.1)
        return modified_rating

    def check_league_change(self, row_data):
        if row_data.league != row_data.home_team_last_league:
            modified_rating = self.changed_league_modification(row_data, home_team=True)
            self.elo_tracker.tracker.loc[row_data.home_team, 'pts'] = modified_rating
        if row_data.league != row_data.away_team_last_league:
            modified_rating = self.changed_league_modification(row_data, home_team=False)
            self.elo_tracker.tracker.loc[row_data.home_team, 'pts'] = modified_rating

    def update_league(self, row_data):
        self.check_league_change(row_data)
        self.elo_tracker.tracker.loc[row_data.home_team, 'league'] = row_data.league
        self.elo_tracker.tracker.loc[row_data.away_team, 'league'] = row_data.league

    def check_and_set_date(self, row_data):
        self.elo_tracker.tracker.loc[row_data.home_team, 'last_played'] = row_data.match_date
        self.elo_tracker.tracker.loc[row_data.away_team, 'last_played'] = row_data.match_date

    def calculate_expected_result(self, team_elo, opponent_elo):
        expected_result = 1 / (1 + (10 ** ((opponent_elo - team_elo) / 400)))
        return expected_result
    
    def update_elos(self, row_data, expected_result_home, expected_result_away):
        if (row_data.match_date.month > 7) & (row_data.match_date.month < 10):
            home_team_elo_new, away_team_elo_new = self.calculate_updated_elo_start(row_data,
                                                                                expected_result_home,
                                                                                expected_result_away)
        else:
            home_team_elo_new, away_team_elo_new = self.calculate_updated_elo_end(row_data,
                                                                             expected_result_home,
                                                                             expected_result_away)
        self.elo_tracker.update_elo_tracker(home_team=row_data.home_team,
                                            home_team_elo_new=home_team_elo_new,
                                            away_team=row_data.away_team,
                                            away_team_elo_new=away_team_elo_new)
    
    def calculate_updated_elo_start(self, row_data, expected_result_home, expected_result_away):
        elo_home_new = row_data.home_team_elo + config.KFACTOR_QUICK * (row_data.result - expected_result_home)
        elo_away_new = row_data.away_team_elo + config.KFACTOR_QUICK * ((1 - row_data.result) - expected_result_away)
        return elo_home_new, elo_away_new
    
    def calculate_updated_elo_end(self, row_data, expected_result_home, expected_result_away):
        elo_home_new = row_data.home_team_elo + config.KFACTOR_SLOW * (row_data.result - expected_result_home)
        elo_away_new = row_data.away_team_elo + config.KFACTOR_SLOW * ((1 - row_data.result) - expected_result_away)
        return elo_home_new, elo_away_new
    
    def rename_columns_to_team_and_opp(self, df: pd.DataFrame, team=True):
        if team:
            df = df.rename(columns={'pt1': 'team', 'pt2': 'opponent', 'elo_home': 'elo_team',
                                    'elo_away': 'elo_opponent'})
        else:
            df = df.rename(columns={'pt2': 'team', 'pt1': 'opponent', 'elo_away': 'elo_team',
                                    'elo_home': 'elo_opponent'})
        return df
    
    def cut_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[['league', 'date', 'pt1', 'pt2', 'match_id', 'result', 'elo_home', 'elo_away', 'elo_diff']]
    
    def adjust_away_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df['elo_diff'] = df['elo_diff'] * -1
        df['result'] = 1 - df['result']
        df = df[['league', 'date', 'team', 'opponent', 'match_id', 'result', 'elo_team', 'elo_opponent', 'elo_diff']]
        df.loc[:, 'home'] = 0
        return df

    def get_team_and_opp_matches(self):
        team_matches = self.matches.copy(deep=True)
        opponent_matches = team_matches.copy(deep=True)

        team_matches = self.cut_columns(team_matches)
        opponent_matches = self.cut_columns(opponent_matches)

        team_matches = self.rename_columns_to_team_and_opp(team_matches, team=True)
        opponent_matches = self.rename_columns_to_team_and_opp(opponent_matches, team=False)

        opponent_matches = self.adjust_away_columns(opponent_matches)

        team_matches.loc[:, 'home'] = 1
 
        self.team_and_opp_matches = pd.concat([team_matches, opponent_matches])
        self.team_and_opp_matches = self.sort_by_date(self.team_and_opp_matches)


class EloTracker():
    def __init__(self, matches):
        self.matches = matches
        self.tracker = self.set_up_tracker()

    def set_up_tracker(self) -> pd.DataFrame:
        tracker = self.get_unique_teams()
        tracker = self.set_up_stats(tracker)
        return tracker
    
    def get_unique_teams(self) -> pd.DataFrame:
        unique_teams = pd.concat([self.matches['pt1'], self.matches['pt2']], axis=0).unique()
        return pd.DataFrame(unique_teams, columns=['team'])
    
    def set_up_stats(self, tracker) -> pd.DataFrame:
        tracker['pts'] = config.STARTING_ELO
        tracker['last_played'] = pd.to_datetime('')
        tracker['league'] = ''
        tracker.set_index('team', inplace=True)
        return tracker
    
    def update_elo_tracker(self, home_team, home_team_elo_new, away_team, away_team_elo_new):
        self.tracker.loc[home_team, 'pts'] = home_team_elo_new
        self.tracker.loc[away_team, 'pts'] = away_team_elo_new

class RowData:
    def __init__(self, row, elo_tracker: EloTracker):
        self.home_team = row['pt1']
        self.away_team = row['pt2']
        self.match_date = row['date']
        self.league = row['league']
        self.result = row['result']
        self.home_last_game = elo_tracker.tracker.loc[self.home_team, 'last_played']
        self.away_last_game = elo_tracker.tracker.loc[self.away_team, 'last_played']
        self.home_team_elo = elo_tracker.tracker.loc[self.home_team, 'pts']
        self.away_team_elo = elo_tracker.tracker.loc[self.away_team, 'pts']
        self.home_team_last_league = elo_tracker.tracker.loc[self.home_team, 'league']
        self.away_team_last_league = elo_tracker.tracker.loc[self.away_team, 'league']
        