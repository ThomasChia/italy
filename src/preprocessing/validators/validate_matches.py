from config import DASHBOARD_LEAGUES, LEAGUE_TEAMS_COUNT, LEAGUE_TEAMS_MAPPING
from datetime import datetime
import pandas as pd
from matches.matches import FullSeasonMatches
import numpy as np
import logging
from logs import setup_logs
from scrapers.builders import SeasonBuilder


setup_logs()
logger = logging.getLogger(__name__)


class ValidateMatches:
    def __init__(self, past_matches: pd.DataFrame, future_matches: pd.DataFrame, season_start, season_end):
        self.past_matches = past_matches
        self.future_matches = future_matches
        self.season_start = datetime.strptime(season_start, '%Y-%m-%d').date()
        self.season_end = datetime.strptime(season_end, '%Y-%m-%d').date()
        self.expected_matches = self._get_expected_matches()
        self.full_season = pd.DataFrame()
        self.added_matches = 0

    def run(self):
        logger.info("Running match validator.")
        self._cut_past_matches()
        self._get_full_season()
        self._check_number_of_matches()

    def _cut_past_matches(self):
        self.past_matches = self.past_matches[self.past_matches['date'] >= self.season_start]

    def _get_full_season(self):
        self.full_season = pd.concat([self.past_matches, self.future_matches]).reset_index(drop=True)

    def _check_number_of_matches(self):
        for league in DASHBOARD_LEAGUES:
            league_expected_matches = self.expected_matches[self.expected_matches['league'] == league]
            actual_matches = self._get_actual_matches(league)
            if len(league_expected_matches) != len(actual_matches):
                no_missing_matches = len(league_expected_matches) - len(actual_matches)
                logger.warning(f"Expected {len(league_expected_matches)} matches for {league}, but got {len(actual_matches)}.")
                self._add_missing_matches_to_future(league_expected_matches, actual_matches)
                assert no_missing_matches == self.added_matches, logger.error(f"Expected {no_missing_matches} missing matches in {league}, but added {self.added_matches}.")
                

    def _get_expected_matches(self) -> pd.DataFrame:
        logger.info("Building full season.")
        season_builder = SeasonBuilder(LEAGUE_TEAMS_MAPPING)
        season_builder.get_all_matches()
        expected_matches = FullSeasonMatches(season_builder.matches)
        expected_matches.clean()
        return expected_matches.matches_df
    
    def _get_actual_matches(self, league) -> pd.DataFrame:
        teams = [team.lower().replace(' ', '_') for team in LEAGUE_TEAMS_MAPPING[league]]
        actual_matches = self.full_season[(self.full_season['league'] == league) & ((self.full_season['pt1'].isin(teams)) | (self.full_season['pt2'].isin(teams)))]
        # actual_matches = actual_matches[actual_matches['pt1'] != 'arsenal'].reset_index(drop=True)
        return actual_matches.drop_duplicates(subset=['pt1', 'pt2'])
    
    def _add_missing_matches_to_future(self, league_expected_matches: pd.DataFrame, actual_matches: pd.DataFrame):
        merged = league_expected_matches.merge(actual_matches, on=['pt1', 'pt2'], how='outer', indicator=True)
        diff = merged[merged['_merge'] != 'both']
        missing_matches = diff[['pt1', 'pt2']]
        missing_matches = self._update_missing_matches(missing_matches, league_expected_matches)
        self.added_matches = missing_matches.shape[0]
        self.future_matches = pd.concat([self.future_matches, missing_matches]).reset_index(drop=True)

    def _update_missing_matches(self, df, league_expected_matches):
        df['date'] = self.season_end
        df['league'] = league_expected_matches['league'].unique()[0]
        df['match_id'] = df['pt1'].str.lower() + '_' + df['pt2'].str.lower() + '_' + df['date'].astype(str)
        return df

