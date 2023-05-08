from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from matches.config import ITALIAN_LEAGUES, ENGLISH_LEAGUES, ITALIAN_CORRECT_NAMES, ENGLISH_CORRECT_NAMES
import pandas as pd
from typing import List


@dataclass
class Matches(ABC):
    country: str
    leagues: List
    matches_dict: dict = field(default_factory=dict)
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

    def align_to_simultions(self):
        self.rename_columns()
        self.replicate_column('result', self.num_simulations)

    def replicate_column(self, col_name, num_replications):
        """
        Replicates the given column of a dataframe a specified number of times.
        
        Args:
        col_name (str): The name of the column to be replicated.
        num_replications (int): The number of times to replicate the column.
        
        Returns:
        pandas.DataFrame: A new dataframe with the replicated column(s).
        """

        col = self.matches_df[col_name]
        replicated_cols = [col] * num_replications
        replicated_df = pd.concat(replicated_cols, axis=1)
        new_col_names = [str(i) for i in range(1, num_replications+1)]
        replicated_df.columns = new_col_names
        self.matches_df = replicated_df

    def rename_columns(self):
        self.matches_df = self.matches_df.rename(columns={'pt1': 'home_team',
                                                          'pt2': 'away_team',
                                                          'score_pt1': 'home_score',
                                                          'score_pt2': 'away_score'})