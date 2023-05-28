from abc import ABC, abstractmethod
from config import SEASON_START
from loaders.loader import DBConnector
from loaders.query import Query
from loaders.writer import DBWriter
from matches.matches import PastMatches
import pandas as pd
from post_processing.config import LEAGUE_TARGETS_COLUMNS, RESULTS_COLUMNS, PAST_PREDICTIONS_COLUMNS, FUTURE_PREDICTIONS_COLUMNS, MATCH_IMPORTANCE_COLUMNS, FINISHING_POSITIONS_COLUMNS, OPPONENT_ANALYSIS_COLUMNS
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
                 opponent_analysis=pd.DataFrame()):
        super().__init__()
        self.league_targets: pd.DataFrame = league_targets
        self.results: PastMatches = results
        self.past_predictions = past_predictions
        self.future_predictions = future_predictions
        self.match_importance = match_importance
        self.finishing_positions = finishing_positions
        self.opponent_analysis = opponent_analysis

    def run(self):
        self.process_league_targets()
        self.process_results()
        self.process_past_predictions()
        self.process_future_predictions()
        self.process_match_importance()
        self.process_finishing_positions()
        self.process_opponent_analysis()

    def process_league_targets(self):
        if not self.league_targets.empty:
            self.league_targets['rounded'] = self.league_targets['points'].round(0)
            self.league_targets = self.league_targets[LEAGUE_TARGETS_COLUMNS]

    def process_results(self):
        if self.results:
            self.results.get_team_and_opp_matches()

    def process_past_predictions(self):
        pass
        # if not self.past_predictions.empty:

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
                 finishing_positions=pd.DataFrame()
                 ):
        self.league_targets: pd.DataFrame = league_targets
        self.future_predictions = future_predictions
        self.match_importance = match_importance
        self.finishing_positions = finishing_positions

    def run(self):
        self.process_league_targets()
        self.process_future_predictions()
        self.process_match_importance()
        self.process_finishing_positions()

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


