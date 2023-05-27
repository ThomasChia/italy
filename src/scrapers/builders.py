import itertools
import pandas as pd
from typing import Dict


class SeasonBuilder:
    def __init__(self, leagues_mapping):
        self.leagues_mapping: Dict = leagues_mapping
        self.matches: pd.DataFrame = pd.DataFrame()

    def get_all_matches(self):
        for league in self.leagues_mapping.keys():
            teams = self.get_teams_in_league(league)
            matches = self.get_all_matches_in_league(league, teams)
            self.matches = pd.concat([self.matches, matches])
        self.set_match_id()

    def get_all_matches_in_league(self, league, teams):
        matches = list(itertools.permutations(teams, 2))
        matches_df = pd.DataFrame(matches, columns=['pt1', 'pt2'])
        matches_df['date'] = '2023-08-01'
        matches_df['league'] = league
        return matches_df

    def get_teams_in_league(self, league):
        return self.leagues_mapping[league]
    
    def set_match_id(self):
        self.matches['match_id'] = self.matches['pt1'] + '_' + self.matches['pt2'] + '_' + self.matches['date']
