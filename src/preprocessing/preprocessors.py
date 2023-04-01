import pandas as pd
from preprocessing.elos.elos import Elo
from preprocessing.goals.goals import TeamGoals, LeagueGoals


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
        self.league_goals = None
        self.preprocessed_matches = None
        self.league_preprocessed_matches = None

    def calculate_goals_statistics(self):
        self.goals = TeamGoals(self.team_and_opp_matches)
        self.goals.calculate_team_averages()
        self.preprocessed_matches = self.goals.team_and_opponent_rolling

        self.league_goals = LeagueGoals(self.team_and_opp_matches)
        self.league_goals.calculate_league_averages()
        self.league_preprocessed_matches = self.league_goals.league_rolling

    def rename_columns_to_team_and_opp(self, df: pd.DataFrame, team=True):
        if team:
            df = df.rename(columns={'pt1': 'team', 'pt2': 'opponent',
                                    'score_pt1': 'team_goals_scored', 'score_pt2': 'opponent_goals_scored'})
        else:
            df = df.rename(columns={'pt2': 'team', 'pt1': 'opponent', 'score_pt2': 'team_goals_scored', 'score_pt1': 'opponent_goals_scored'})
        return df
    
    def cut_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[['league', 'date', 'pt1', 'pt2', 'result', 'score_pt1', 'score_pt2']]
    
    def adjust_away_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df['result'] = 1 - df['result']
        df = df[['league', 'date', 'team', 'opponent', 'result',
                 'team_goals_scored',
                 'opponent_goals_scored',
                 'team_goals_conceded',
                 'opponent_goals_conceded']]
        df.loc[:, 'home'] = 0
        return df
    
    def sort_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(by='date')
        df = df.reset_index(drop=True)
        return df
    
    def get_goals_conceded(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc[:, 'team_goals_conceded'] = df['opponent_goals_scored']
        df.loc[:, 'opponent_goals_conceded'] = df['team_goals_scored']
        return df

    def get_team_and_opp_matches(self, matches):
        team_matches = matches.copy(deep=True)
        opponent_matches = team_matches.copy(deep=True)

        team_matches = self.cut_columns(team_matches)
        opponent_matches = self.cut_columns(opponent_matches)

        team_matches = self.rename_columns_to_team_and_opp(team_matches, team=True)
        opponent_matches = self.rename_columns_to_team_and_opp(opponent_matches, team=False)

        team_matches = self.get_goals_conceded(team_matches)
        opponent_matches = self.get_goals_conceded(opponent_matches)

        opponent_matches = self.adjust_away_columns(opponent_matches)

        team_matches.loc[:, 'home'] = 1
 
        team_and_opp_matches = pd.concat([team_matches, opponent_matches])
        team_and_opp_matches = self.sort_by_date(team_and_opp_matches)

        return team_and_opp_matches
