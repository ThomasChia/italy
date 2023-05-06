from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from matches.config import ITALIAN_LEAGUES, ENGLISH_LEAGUES
from typing import List


@dataclass
class Matches(ABC):
    country: str
    leagues: List

    @abstractmethod
    def get_matches(self):
        pass


@dataclass
class ItalianMatches(Matches):
    country: str = 'italy'
    leagues: List = ITALIAN_LEAGUES


@dataclass
class EnglishMatches(Matches):
    country: str = 'england'
    leagues: List = ENGLISH_LEAGUES
