import pandas as pd
from preprocessing.elos.elos import Elo
from preprocessing.goals.goals import Goals


class Preprocessor:
    def __init__(self) -> None:
        pass

class EloPreprocessor(Preprocessor):
    def __init__(self, matches: pd.DataFrame) -> None:
        super().__init__()
        self.elo = Elo(matches)
        self.processed_matches = None

    def calculate_elos(self):
        self.elo.calculate()
        self.preprocessed_matches = self.elo.team_and_opp_matches

class GoalsPreprocessor(Preprocessor):
    def __init__(self, matches: pd.DataFrame):
        super().__init__()
        self.team_and_opp_matches = self.get_team_and_opp_matches(matches)
        self.goals = None
        self.preprocessed_matches = None

    def calculate_goals_statistics(self):
        self.goals = Goals(self.team_and_opp_matches)
        self.goals.calculate()
        self.preprocessed_matches = self.elo.team_and_opp_matches

    def rename_columns_to_team_and_opp(self, df: pd.DataFrame, team=True):
        if team:
            df = df.rename(columns={'pt1': 'team', 'pt2': 'opponent', 'elo_home': 'elo_team',
                                    'elo_away': 'elo_opponent'})
        else:
            df = df.rename(columns={'pt2': 'team', 'pt1': 'opponent', 'elo_away': 'elo_team',
                                    'elo_home': 'elo_opponent'})
        return df
    
    def cut_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[['league', 'date', 'pt1', 'pt2', 'result', 'elo_home', 'elo_away', 'elo_diff']]
    
    def adjust_away_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df['elo_diff'] = df['elo_diff'] * -1
        df['result'] = 1 - df['result']
        df = df[['league', 'date', 'team', 'opponent', 'result', 'elo_team', 'elo_opponent', 'elo_diff']]
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
        self.team_and_opp_matches = self.sort_by_date(team_matches)
