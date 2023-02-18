import config
import numpy as np
import pandas as pd


class Elo:
    def __init__(self, matches):
        self.matches: pd.DataFrame = matches
        self.starting_elo = config.STARTING_ELO
        self.kfactor_quick = config.KFACTOR_QUICK
        self.kfactor_slow = config.KFACTOR_SLOW
        self.home_ad = config.HOME_AD
        self.elo_tracker = EloTracker(matches)

    def calc_all_elos(self, matches):
        self.matches = self.matches.apply(lambda x: self.calc_elos(x, 
                                                            self.kfactor_quick,
                                                            self.kfactor_slow,
                                                            self.home_ad), axis=1)

    def calc_elos(self, row):
        row_data = RowData(row, self.elo_tracker)

        self.update_div(row_data)
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
            print(row.name, 'matches calculated.')

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
    
    def get_league_elos(self, div):
        return self.elo_tracker[self.elo_tracker['league'] == div]
    
    def get_league_average(self, div):
        div_elos = self.get_league_elos(div)
        if div_elos.empty:
            league_average = config.STARTING_ELO
        else:
            league_average = div_elos['pts'].mean()
        return league_average

    def changed_league_modification(self, row_data, home_team=True):
        league_average = self.get_league_average(row_data.div)
        if home_team:
            modified_rating = row_data.home_team_elo * (1 - (row_data.home_team_elo - league_average) / (league_average) * 0.1)
        else:
            modified_rating = row_data.away_team_elo * (1 - (row_data.away_team_elo - league_average) / (league_average) * 0.1)
        return modified_rating

    def check_div_change(self, row_data):
        if row_data.div != self.row_data.home_team_last_div:
            modified_rating = self.changed_league_modification(row_data, home_team=True)
            self.elo_tracker.loc[row_data.home_team, 'pts'] = modified_rating
        if row_data.div != self.row_data.away_team_last_div:
            modified_rating = self.changed_league_modification(row_data, home_team=False)
            self.elo_tracker.loc[row_data.home_team, 'pts'] = modified_rating

    def update_div(self, row_data):
        self.check_div_change(row_data)
        self.elo_tracker.loc[row_data.home_team, 'league'] = row_data.div
        self.elo_tracker.loc[row_data.away_team, 'league'] = row_data.div

    def check_and_set_date(self, row_data):
        self.elo_tracker.loc[row_data.home_team, 'last_played'] = row_data.date
        self.elo_tracker.loc[row_data.away_team, 'last_played'] = row_data.date

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
        self.elo_tracker.update_elo_tracker(row_data.home_team,
                                            home_team_elo_new,
                                            row_data.away_team,
                                            away_team_elo_new)
    
    def calculate_updated_elo_start(self, row_data, expected_result_home, expected_result_away):
        elo_home_new = row_data.home_team_elo + config.KFACTOR_QUICK * (row_data.result - expected_result_home)
        elo_away_new = row_data.away_team_elo + config.KFACTOR_QUICK * ((1 - row_data.result) - expected_result_away)
        return elo_home_new, elo_away_new
    
    def calculate_updated_elo_end(self, row_data, expected_result_home, expected_result_away):
        elo_home_new = row_data.home_team_elo + config.KFACTOR_SLOW * (row_data.result - expected_result_home)
        elo_away_new = row_data.away_team_elo + config.KFACTOR_SLOW * ((1 - row_data.result) - expected_result_away)
        return elo_home_new, elo_away_new



class EloTracker:
    def __init__(self, matches):
        self.matches = matches
        self.starting_elo = config.STARTING_ELO
        self.tracker = self.set_up_tracker()

    def set_up_tracker(self) -> pd.DataFrame:
        tracker = self.get_unique_teams()
        tracker = self.set_up_stats(tracker)
        return tracker
    
    def get_unique_teams(self) -> pd.DataFrame:
        unique_teams = pd.concat([self.matches['pt1'],
                                self.matches['pt2']], axis=0).unique()
        return pd.DataFrame(unique_teams, columns=['team'])
    
    def set_up_stats(self, tracker) -> pd.DataFrame:
        tracker['pts'] = self.starting_elo
        tracker['last_played'] = pd.to_datetime('')
        tracker['league'] = ''
        return tracker
    
    def update_elo_tracker(self, home_team, home_team_elo_new, away_team_elo_new, away_team):
        self.tracker.loc[home_team, 'pts'] = home_team_elo_new
        self.tracker.loc[away_team, 'pts'] = away_team_elo_new

class RowData:
    def __init__(self, row, elo_tracker: EloTracker):
        self.home_team = row['pt1']
        self.away_team = row['pt2']
        self.match_date = row['date']
        self.div = row['league']
        self.result = row['result']
        self.home_last_game = elo_tracker.loc[self.home_team, 'last_played']
        self.away_last_game = elo_tracker.loc[self.away_team, 'last_played']
        self.home_team_elo = elo_tracker.loc[self.home_team, 'pts']
        self.away_team_elo = elo_tracker.loc[self.away_team, 'pts']
        self.home_team_last_div = elo_tracker.loc[self.home_team, 'div']
        self.away_team_last_div = elo_tracker.loc[self.away_team, 'div']
        