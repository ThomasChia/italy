from abc import ABC, abstractmethod
from config import SEASON_START, DASHBOARD_LEAGUES, DASHBOARD_TEAMS, LEAGUE_SCALING_MAPPING
from datetime import datetime
from loaders.loader import DBConnector
from loaders.query import Query
from loaders.writer import DBWriter
from matches.matches import PastMatches
import pandas as pd
from post_processing.config import (ELO_TRACKER_COLUMNS,
                                    ELO_OVER_TIME_COLUMNS,
                                    FINISHING_POSITIONS_COLUMNS,
                                    FUTURE_PREDICTIONS_COLUMNS,
                                    LEAGUE_TARGETS_COLUMNS, 
                                    MATCH_IMPORTANCE_COLUMNS,
                                    OPPONENT_ANALYSIS_COLUMNS,
                                    PAST_PREDICTIONS_COLUMNS,
                                    RESULTS_COLUMNS
                                    )
from post_processing.rest_days_post_processor import RestDaysPostProcessor

class PostProcessor(ABC):

    @abstractmethod
    def run(self):
        pass


class InSeasonPostProcessor(PostProcessor):
    def __init__(self, 
                 league_targets=pd.DataFrame(), 
                 results: PastMatches = PastMatches(), 
                 past_predictions=pd.DataFrame(),
                 future_predictions=pd.DataFrame(),
                 match_importance=pd.DataFrame(),
                 finishing_positions=pd.DataFrame(),
                 opponent_analysis=pd.DataFrame(),
                 elo_tracker=pd.DataFrame(),
                 elo_over_time=pd.DataFrame()):
        super().__init__()
        self.league_targets: pd.DataFrame = league_targets
        self.results: PastMatches = results
        self.past_predictions = past_predictions
        self.future_predictions = future_predictions
        self.match_importance = match_importance
        self.finishing_positions = finishing_positions
        self.opponent_analysis = opponent_analysis
        self.elo_tracker = elo_tracker
        self.elo_over_time = elo_over_time

    def run(self):
        self.process_league_targets()
        self.process_results()
        self.process_past_predictions()
        self.process_future_predictions()
        self.process_match_importance()
        self.process_finishing_positions()
        self.process_opponent_analysis()
        self.process_elo_tracker()
        self.process_elo_over_time()

    def process_league_targets(self):
        if not self.league_targets.empty:
            self.league_targets['rounded'] = self.league_targets['points'].round(0)
            self.league_targets = self.league_targets[LEAGUE_TARGETS_COLUMNS]

    def process_results(self):
        if not self.results.matches_df.empty:
            self.results = self.get_team_and_opp_matches(self.results.matches_df)
            self.results = self.cut_to_season(self.results)

    def get_team_and_opp_matches(self, matches: pd.DataFrame):
        matches_cut = self.cut_columns(matches)
        matches_cut = self.proper_case(matches_cut)
        matches_cut = self.filter_teams(matches_cut)
        matches_cut['result'] = matches_cut.apply(lambda x: self.get_result(x), axis=1)
        team_matches = matches_cut.copy(deep=True)
        opponent_matches = team_matches.copy(deep=True)

        team_matches = self.rename_columns_to_team_and_opp(team_matches, team=True)
        opponent_matches = self.rename_columns_to_team_and_opp(opponent_matches, team=False)

        opponent_matches = self.adjust_away_columns(opponent_matches)

        team_matches.loc[:, 'home'] = 1

        team_and_opp_matches = pd.concat([team_matches, opponent_matches])
        team_and_opp_matches = self.sort_by_date(team_and_opp_matches)



        return team_and_opp_matches
    
    def proper_case(self, df: pd.DataFrame):
        df['pt1'] = df['pt1'].str.replace('_', ' ')
        df['pt1'] = df['pt1'].str.title()
        df['pt2'] = df['pt2'].str.replace('_', ' ')
        df['pt2'] = df['pt2'].str.title()
        return df
    
    def filter_teams(self, df: pd.DataFrame):
        df = df[df['pt1'].isin(DASHBOARD_TEAMS)]
        df = df[df['pt2'].isin(DASHBOARD_TEAMS)]
        return df
    
    def get_result(self, row):
        if row['score_pt1'] > row['score_pt2']:
            return 1
        elif row['score_pt1'] < row['score_pt2']:
            return 0
        else:
            return 0.5
    
    def rename_columns_to_team_and_opp(self, df: pd.DataFrame, team=True):
        if team:
            df = df.rename(columns={'pt1': 'team',
                                    'pt2': 'opponent',
                                    'score_pt1': 'team_goals_scored',
                                    'score_pt2': 'opponent_goals_scored'})
        else:
            df = df.rename(columns={'pt2': 'team',
                                    'pt1': 'opponent',
                                    'score_pt2': 'team_goals_scored',
                                    'score_pt1': 'opponent_goals_scored'})
        return df
    
    def cut_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[['league', 'date', 'pt1', 'pt2', 'score_pt1', 'score_pt2']]
    
    def adjust_away_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df['result'] = 1 - df['result']
        df = df[['league', 'date', 'team', 'opponent', 'result', 'team_goals_scored', 'opponent_goals_scored']]
        df.loc[:, 'home'] = 0
        return df
    
    def adjust_result(self, df: pd.DataFrame) -> pd.DataFrame:
        df['result'] = df['result'].replace({1: 'H', 0: 'A', 0.5: 'D'})
        return df
    
    def sort_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(by='date')
        df = df.reset_index(drop=True)
        return df
    
    def cut_to_season(self, results: pd.DataFrame) -> pd.DataFrame:
        season_start_datetime = datetime.strptime(SEASON_START, '%Y-%m-%d')
        return results.loc[results['date'] >= season_start_datetime.date()]

    def process_past_predictions(self):
        if not self.past_predictions.empty:
            self.past_predictions['team'] = self.past_predictions['team'].str.replace('_', ' ')
            self.past_predictions['team'] = self.past_predictions['team'].str.title()
            self.past_predictions['opponent'] = self.past_predictions['opponent'].str.replace('_', ' ')
            self.past_predictions['opponent'] = self.past_predictions['opponent'].str.title()
            self.past_predictions['league'] = self.past_predictions['league'].str.replace('_', ' ')
            self.past_predictions['league'] = self.past_predictions['league'].str.title()
            calculator = RestDaysPostProcessor(self.past_predictions)
            self.past_predictions = calculator.calculate_rest_days()
            self.past_predictions = self.past_predictions[PAST_PREDICTIONS_COLUMNS]

    def process_future_predictions(self):
        if not self.future_predictions.empty:
            self.future_predictions['team'] = self.future_predictions['team'].str.replace('_', ' ')
            self.future_predictions['team'] = self.future_predictions['team'].str.title()
            self.future_predictions['opponent'] = self.future_predictions['opponent'].str.replace('_', ' ')
            self.future_predictions['opponent'] = self.future_predictions['opponent'].str.title()
            self.future_predictions['league'] = self.future_predictions['league'].str.replace('_', ' ')
            self.future_predictions['league'] = self.future_predictions['league'].str.title()
            calculator = RestDaysPostProcessor(self.future_predictions)
            self.future_predictions = calculator.calculate_rest_days()
            self.future_predictions = self.future_predictions[FUTURE_PREDICTIONS_COLUMNS]

    def process_match_importance(self):
        if not self.match_importance.empty:
            self.match_importance = self.match_importance.reset_index().rename(columns={'index': 'team'})
            self.match_importance['team'] = self.match_importance['team'].str.replace('_', ' ')
            self.match_importance['team'] = self.match_importance['team'].str.title()
            self.match_importance['league'] = self.match_importance['league'].str.replace('_', ' ')
            self.match_importance['league'] = self.match_importance['league'].str.title()
            self.match_importance = self.match_importance.fillna(0)
            self.match_importance = self.match_importance[MATCH_IMPORTANCE_COLUMNS]

    def process_finishing_positions(self):
        if not self.finishing_positions.empty:
            self.finishing_positions = self.finishing_positions.reset_index().rename(columns={'index': 'team'})
            self.finishing_positions['team'] = self.finishing_positions['team'].str.replace('_', ' ')
            self.finishing_positions['team'] = self.finishing_positions['team'].str.title()
            self.finishing_positions['league'] = self.finishing_positions['league'].str.replace('_', ' ')
            self.finishing_positions['league'] = self.finishing_positions['league'].str.title()
            self.finishing_positions = self.finishing_positions[FINISHING_POSITIONS_COLUMNS]

    def process_opponent_analysis(self):
        pass
        # if not self.opponent_analysis.empty:

    def split_old_new_predictions(self):
        query = Query()
        query.read_last_future_predictions()
        loader = DBConnector()
        loader.run_query(query)
        old_future_predictions = loader.data.copy(deep=True)
        merged = pd.merge(old_future_predictions, self.future_predictions, on=['match_id', 'team'], how='outer', suffixes=('_left', '_right'))
        new_past_predictions = merged[merged['opponent_left'] != merged['opponent_right']]

        writer = DBWriter()
        writer.run_update_query(new_past_predictions)

    def process_elo_tracker(self):
        if not self.elo_tracker.empty:
            self.elo_tracker = self.elo_tracker.reset_index()
            self.elo_tracker['team'] = self.elo_tracker['team'].str.replace('_', ' ')
            self.elo_tracker['team'] = self.elo_tracker['team'].str.title()
            self.elo_tracker['league'] = self.elo_tracker['league'].str.replace('_', ' ')
            self.elo_tracker['league'] = self.elo_tracker['league'].str.title()
            self.elo_tracker = self.elo_tracker[self.elo_tracker['team'].isin(DASHBOARD_TEAMS)]
            self.elo_tracker = self.normalize_elos_by_league(self.elo_tracker)
            self.elo_tracker = self.elo_tracker[ELO_TRACKER_COLUMNS]

    def normalize_elos_by_league(self, df: pd.DataFrame):
        league_stats = df.groupby('league')['pts'].agg(['mean', 'std'])
        normalize_elos = lambda group: (group['pts'] - league_stats.loc[group.name, 'mean']) / league_stats.loc[group.name, 'std']
        df['pts'] = df.groupby('league').apply(normalize_elos).reset_index(level=0, drop=True)
        df = df.apply(lambda x: self.scale_elos_by_league(x), axis=1)
        return df
    
    def scale_elos_by_league(self, row: pd.DataFrame):
        scaling_factor = LEAGUE_SCALING_MAPPING[str(row['league'])]
        row['pts'] = row['pts'] * 100 + scaling_factor
        return row

    def process_elo_over_time(self):
        if not self.elo_over_time.empty:
            self.elo_over_time = self.elo_over_time.sort_values(['team', 'date'])
            self.elo_over_time = self.elo_over_time.reset_index(drop=False)
            self.elo_over_time = self.elo_over_time.rename(columns={'elo_team': 'elo'})
            self.elo_over_time['team'] = self.elo_over_time['team'].str.replace('_', ' ')
            self.elo_over_time['team'] = self.elo_over_time['team'].str.title()
            self.elo_over_time['league'] = self.elo_over_time['league'].str.replace('_', ' ')
            self.elo_over_time['league'] = self.elo_over_time['league'].str.title()
            self.elo_over_time = self.elo_over_time[self.elo_over_time['league'].isin(DASHBOARD_LEAGUES)]
            self.elo_over_time = self.elo_over_time[ELO_OVER_TIME_COLUMNS]


class ResetPostProcessor(PostProcessor):
    def __init__(self, 
                 results: PastMatches = PastMatches(), 
                 past_predictions=pd.DataFrame(),
                 future_predictions=pd.DataFrame()
                 ):
        super().__init__()
        self.results: PastMatches = results
        self.past_predictions = past_predictions
        self.future_predictions = future_predictions

    def run(self):
        self.process_results()
        self.process_past_predictions()
        self.process_future_predictions()

    def process_results(self):
        if self.results:
            self.results.get_team_and_opp_matches()

    def process_past_predictions(self):
        self.past_predictions = self.past_predictions.reset_index(drop=True)

    def process_future_predictions(self):
        self.future_predictions = self.future_predictions.reset_index(drop=True)
        calculator = RestDaysPostProcessor(self.future_predictions)
        self.future_predictions = calculator.calculate_rest_days()


class FullSeasonPostProcessor(PostProcessor):
    def __init__(self, 
                 league_targets=pd.DataFrame(),  
                 future_predictions=pd.DataFrame(),
                 match_importance=pd.DataFrame(),
                 finishing_positions=pd.DataFrame(),
                 elo_tracker=pd.DataFrame(),
                 elo_over_time=pd.DataFrame()
                 ):
        self.league_targets: pd.DataFrame = league_targets
        self.future_predictions = future_predictions
        self.match_importance = match_importance
        self.finishing_positions = finishing_positions
        self.elo_tracker = elo_tracker
        self.elo_over_time = elo_over_time

    def run(self):
        self.process_league_targets()
        self.process_future_predictions()
        self.process_match_importance()
        self.process_finishing_positions()
        self.process_elo_tracker()
        self.process_elo_over_time()

    def process_league_targets(self):
        if not self.league_targets.empty:
            self.league_targets['rounded'] = self.league_targets['points'].round(0)
            self.league_targets = self.league_targets[LEAGUE_TARGETS_COLUMNS]

    def process_future_predictions(self):
        if not self.future_predictions.empty:
            self.future_predictions['team'] = self.future_predictions['team'].str.replace('_', ' ')
            self.future_predictions['team'] = self.future_predictions['team'].str.title()
            self.future_predictions['opponent'] = self.future_predictions['opponent'].str.replace('_', ' ')
            self.future_predictions['opponent'] = self.future_predictions['opponent'].str.title()
            self.future_predictions['league'] = self.future_predictions['league'].str.replace('_', ' ')
            self.future_predictions['league'] = self.future_predictions['league'].str.title()
            calculator = RestDaysPostProcessor(self.future_predictions)
            self.future_predictions = calculator.calculate_rest_days()
            self.future_predictions = self.future_predictions[FUTURE_PREDICTIONS_COLUMNS]

    def process_match_importance(self):
        if not self.match_importance.empty:
            self.match_importance = self.match_importance.reset_index().rename(columns={'index': 'team'})
            self.match_importance['team'] = self.match_importance['team'].str.replace('_', ' ')
            self.match_importance['team'] = self.match_importance['team'].str.title()
            self.match_importance['league'] = self.match_importance['league'].str.replace('_', ' ')
            self.match_importance['league'] = self.match_importance['league'].str.title()
            self.match_importance = self.match_importance.fillna(0)
            self.match_importance = self.match_importance[MATCH_IMPORTANCE_COLUMNS]

    def process_finishing_positions(self):
        if not self.finishing_positions.empty:
            self.finishing_positions = self.finishing_positions.reset_index().rename(columns={'index': 'team'})
            self.finishing_positions['team'] = self.finishing_positions['team'].str.replace('_', ' ')
            self.finishing_positions['team'] = self.finishing_positions['team'].str.title()
            self.finishing_positions['league'] = self.finishing_positions['league'].str.replace('_', ' ')
            self.finishing_positions['league'] = self.finishing_positions['league'].str.title()
            self.finishing_positions = self.finishing_positions[FINISHING_POSITIONS_COLUMNS]

    def process_elo_tracker(self):
        if not self.elo_tracker.empty:
            self.elo_tracker = self.elo_tracker.reset_index()
            self.elo_tracker['team'] = self.elo_tracker['team'].str.replace('_', ' ')
            self.elo_tracker['team'] = self.elo_tracker['team'].str.title()
            self.elo_tracker['league'] = self.elo_tracker['league'].str.replace('_', ' ')
            self.elo_tracker['league'] = self.elo_tracker['league'].str.title()
            self.elo_tracker = self.elo_tracker[self.elo_tracker['team'].isin(DASHBOARD_TEAMS)]
            self.elo_tracker = self.normalize_elos_by_league(self.elo_tracker)
            self.elo_tracker = self.elo_tracker[ELO_TRACKER_COLUMNS]

    def normalize_elos_by_league(self, df: pd.DataFrame):
        league_stats = df.groupby('league')['pts'].agg(['mean', 'std'])
        normalize_elos = lambda group: (group['pts'] - league_stats.loc[group.name, 'mean']) / league_stats.loc[group.name, 'std']
        df['pts'] = df.groupby('league').apply(normalize_elos).reset_index(level=0, drop=True)
        df = df.apply(lambda x: self.scale_elos_by_league(x), axis=1)
        return df
    
    def scale_elos_by_league(self, row: pd.DataFrame):
        scaling_factor = LEAGUE_SCALING_MAPPING[str(row['league'])]
        row['pts'] = row['pts'] * 100 + scaling_factor
        return row

    def process_elo_over_time(self):
        if not self.elo_over_time.empty:
            self.elo_over_time = self.elo_over_time.sort_values(['team', 'date'])
            self.elo_over_time = self.elo_over_time.reset_index(drop=True)
            self.elo_over_time = self.elo_over_time.rename(columns={'elo_team': 'elo'})
            self.elo_over_time['team'] = self.elo_over_time['team'].str.replace('_', ' ')
            self.elo_over_time['team'] = self.elo_over_time['team'].str.title()
            self.elo_over_time['league'] = self.elo_over_time['league'].str.replace('_', ' ')
            self.elo_over_time['league'] = self.elo_over_time['league'].str.title()
            self.elo_over_time = self.elo_over_time[self.elo_over_time['league'].isin(DASHBOARD_LEAGUES)]
            self.elo_over_time = self.elo_over_time[ELO_OVER_TIME_COLUMNS]


