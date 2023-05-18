from abc import ABC
from config import SEASON_START
from matches.matches import PastMatches
import pandas as pd
from post_processing.rest_days_post_processor import RestDaysPostProcessor

class PostProcessor(ABC):
    def __init__(self):
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
            calculator = RestDaysPostProcessor(self.future_predictions)
            self.future_predictions = calculator.calculate_rest_days()

    def process_match_importance(self):
        if not self.match_importance.empty:
            self.match_importance = self.match_importance.reset_index()
            self.match_importance['team'] = self.match_importance['team'].str.replace('_', ' ')
            self.match_importance['team'] = self.match_importance['team'].str.title()
            self.match_importance = self.match_importance.fillna(0)

    def process_finishing_positions(self):
        if not self.finishing_positions.empty:
            self.finishing_positions = self.finishing_positions.reset_index()
            self.finishing_positions['team'] = self.finishing_positions['team'].str.replace('_', ' ')
            self.finishing_positions['team'] = self.finishing_positions['team'].str.title()

    def process_opponent_analysis(self):
        pass
        # if not self.opponent_analysis.empty:


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
        pass

    def process_results(self):
        if self.results:
            self.results.get_team_and_opp_matches()