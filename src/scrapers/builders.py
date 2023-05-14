import itertools
import pandas as pd


class SeasonBuilder:
    def __init__(self, teams):
        self.teams = teams
        self.matches: pd.DataFrame = pd.DataFrame()

    def get_all_matches(self, div, teams):
        matches = list(itertools.permutations(teams, 2))
        matches_df = pd.DataFrame(matches, columns=['home_team', 'away_team'])

        matches_df['league'] = div

        return matches_df
