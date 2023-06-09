from abc import ABC, abstractmethod
from collections import defaultdict
from config import SEASON_START, TEAM_NAMES_DICT, LEAGUE_TEAMS_COUNT
from dataclasses import dataclass, field
import logging
from matches.config import ITALIAN_LEAGUES, ENGLISH_LEAGUES, ITALIAN_CORRECT_NAMES, ENGLISH_CORRECT_NAMES
import pandas as pd
from typing import List


@dataclass
class Matches(ABC):
    country: str
    leagues: List
    matches_dict: dict = field(default_factory=lambda: defaultdict(list))
    matches_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    def remove_spaces_in_teams(self):
        self.matches_df['pt1'] = self.matches_df['pt1'].replace(' ', '_', regex=True).str.lower()
        self.matches_df['pt2'] = self.matches_df['pt2'].replace(' ', '_', regex=True).str.lower()

    @abstractmethod
    def clean_future_matches(self):
        pass


@dataclass
class ItalianMatches(Matches):
    country: str = 'italy'
    leagues: List[str] = field(default_factory=lambda: ITALIAN_LEAGUES)
    correct_names: dict = field(default_factory=lambda: ITALIAN_CORRECT_NAMES)

    def clean_future_matches(self):
        self.remove_spaces_in_teams()
        self.correct_teams()

    def correct_teams(self):
        self.matches_df['pt1'] = self.matches_df['pt1'].replace(ITALIAN_CORRECT_NAMES)
        self.matches_df['pt2'] = self.matches_df['pt2'].replace(ITALIAN_CORRECT_NAMES)



@dataclass
class EnglishMatches(Matches):
    country: str = 'england'
    leagues: List = field(default_factory=lambda: ENGLISH_LEAGUES)

    def correct_teams(self):
        self.matches_df['pt1'] = self.matches_df['pt1'].replace(ENGLISH_CORRECT_NAMES)
        self.matches_df['pt2'] = self.matches_df['pt2'].replace(ENGLISH_CORRECT_NAMES)

    def clean_future_matches(self):
        self.remove_spaces_in_teams()
        self.correct_teams()


@dataclass
class PastMatches:
    matches_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    team_and_opp_matches: pd.DataFrame = field(default_factory=pd.DataFrame)

    def align_to_simultions(self, num_simulations):
        self.rename_columns()
        self.replicate_column('result', num_simulations)

    def replicate_column(self, col_name, num_replications):
        """
        Replicates the given column of a dataframe a specified number of times.
        
        Args:
        col_name (str): The name of the column to be replicated.
        num_replications (int): The number of times to replicate the column.
        
        Returns:
        pandas.DataFrame: A new dataframe with the replicated column(s).
        """

        self.matches_df['result'] = self.matches_df['result'].replace({1:3, 0.5:1})
        col = self.matches_df[col_name]
        replicated_cols = [col] * num_replications
        replicated_df = pd.concat(replicated_cols, axis=1)
        new_col_names = [i for i in range(1, num_replications+1)]
        replicated_df.columns = new_col_names
        self.matches_df = self.matches_df.merge(replicated_df, left_index=True, right_index=True)

    def rename_columns(self):
        self.matches_df = self.matches_df.rename(columns={'pt1': 'home_team',
                                                          'pt2': 'away_team',
                                                          'score_pt1': 'home_score',
                                                          'score_pt2': 'away_score'})
        
    def filter_by_date(self, filter_date):
        self.matches_df = self.matches_df[pd.to_datetime(self.matches_df['date']) > pd.to_datetime(filter_date)]

    def remove_in_season_duplicates(self):
        self.matches_df = self.matches_df.drop_duplicates(subset=['pt1', 'pt2'], keep='last')

    def get_team_and_opp_matches(self):
        season_matches = self.cut_from_date(self.matches_df, SEASON_START)
        team_matches = season_matches.copy(deep=True)
        opponent_matches = team_matches.copy(deep=True)

        team_matches = self.cut_columns(team_matches)
        opponent_matches = self.cut_columns(opponent_matches)

        team_matches = self.rename_columns_to_team_and_opp(team_matches, team=True)
        opponent_matches = self.rename_columns_to_team_and_opp(opponent_matches, team=False)

        opponent_matches = self.adjust_away_columns(opponent_matches)

        team_matches.loc[:, 'home'] = 1
 
        self.team_and_opp_matches = pd.concat([team_matches, opponent_matches])
        self.team_and_opp_matches = self.sort_by_date(self.team_and_opp_matches)

    def rename_columns_to_team_and_opp(self, df: pd.DataFrame, team=True):
        if team:
            df = df.rename(columns={'pt1': 'team', 'pt2': 'opponent', 'score_pt1': 'team_goals_scored', 'score_pt2': 'opponent_goals_scored'})
        else:
            df = df.rename(columns={'pt2': 'team', 'pt1': 'opponent', 'score_pt2': 'team_goals_scored', 'score_pt1': 'opponent_goals_scored'})
        return df
    
    def cut_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[['league', 'date', 'pt1', 'pt2', 'score_pt1', 'score_pt2', 'result']]
    
    def adjust_away_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df['result'] = 1 - df['result']
        df.loc[:, 'home'] = 0
        return df
    
    def sort_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(by='date')
        df = df.reset_index(drop=True)
        return df
    
    def cut_from_date(self, df, date):
        df = df[pd.to_datetime(df['date']) > pd.to_datetime(date)]
        return df


@dataclass
class FullSeasonMatches:
    matches_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    def clean(self):
        self.remove_spaces_in_teams()
        self.clean_team_names()
        self.check_number_of_teams()

    def remove_spaces_in_teams(self):
        self.matches_df['pt1'] = self.matches_df['pt1'].replace(' ', '_', regex=True).str.lower()
        self.matches_df['pt2'] = self.matches_df['pt2'].replace(' ', '_', regex=True).str.lower()

    def clean_team_names(self):
        logging.info(f"Cleaning team names")
        self.matches_df['pt1'] = self.matches_df['pt1'].replace(TEAM_NAMES_DICT)
        self.matches_df['pt2'] = self.matches_df['pt2'].replace(TEAM_NAMES_DICT)

    def check_number_of_teams(self):
        for league in LEAGUE_TEAMS_COUNT.keys():
            num_teams = self.matches_df[self.matches_df['league']==league][['pt1', 'pt2']].values.ravel('K')
            num_teams = len(pd.unique(num_teams))
            self.compare_league_teams_to_actual(num_teams, LEAGUE_TEAMS_COUNT[league], league)
            
    def compare_league_teams_to_actual(self, num_teams, actual_num_teams, league):
        if num_teams != actual_num_teams:
                logging.error(f"Number of teams is {num_teams} instead of {actual_num_teams} in {league}")
                raise ValueError(f"Number of teams is {num_teams} instead of {actual_num_teams} in {league}")