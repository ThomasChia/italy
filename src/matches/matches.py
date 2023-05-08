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
    leagues: List = ITALIAN_LEAGUES
    correct_names: dict = ITALIAN_CORRECT_NAMES

    def clean_future_matches(self):
        self.remove_spaces_in_teams()
        self.correct_teams()

    def correct_teams(self):
        self.matches_df['pt1'] = self.matches_df['pt1'].replace(ITALIAN_CORRECT_NAMES)
        self.matches_df['pt2'] = self.matches_df['pt2'].replace(ITALIAN_CORRECT_NAMES)



@dataclass
class EnglishMatches(Matches):
    country: str = 'england'
    leagues: List = ENGLISH_LEAGUES

    def correct_teams(self):
        self.matches_df['pt1'] = self.matches_df['pt1'].replace(ENGLISH_CORRECT_NAMES)
        self.matches_df['pt2'] = self.matches_df['pt2'].replace(ENGLISH_CORRECT_NAMES)

    def clean_future_matches(self):
        self.remove_spaces_in_teams()
        self.correct_teams()


@dataclass
class PastMatches:
    matches_df: pd.DataFrame = field(default_factory=pd.DataFrame)