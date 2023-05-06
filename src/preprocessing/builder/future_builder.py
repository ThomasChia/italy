from matches.matches import Matches
import pandas as pd
from preprocessing.builder.builder import Builder
from scrapers.scrapers import Scraper


class FutureBuilder:
    def __init__(self, scraper: Scraper, future_matches: Matches, past_matches: Builder) -> None:
        self.scraper = scraper(future_matches)
        self.past_matches = past_matches
        self.future_matches = None
        self.preprocessed_future_matches = None

    def build_future_matches(self):
        self.future_matches = self.get_future_matches()
        self.add_past_stats_to_future_matches()

    def get_future_matches(self):
        self.scraper.get_matches()
        self.scraper.matches.clean_future_matches()
        return self.scraper.matches.matches_df

    def add_past_stats_to_future_matches(self):
        most_recent_team_df = self.get_latest_past_stats()
        most_recent_opponent_df = self.get_latest_opponent_stats()
        future_matches_pt1 = pd.merge(self.future_matches, most_recent_team_df, left_on='pt1', right_on='team', how='left').rename(columns={'pt1': 'team', 'pt2': 'opponent'})
        future_matches_pt1['home'] = 1
        future_matches_pt2 = pd.merge(self.future_matches, most_recent_team_df, left_on='pt2', right_on='team', how='left').rename(columns={'pt2': 'team', 'pt1': 'opponent'})
        future_matches_pt1['home'] = 0
        future_matches_team_and_league = pd.concat([future_matches_pt1, future_matches_pt2])
        self.preprocessed_future_matches = pd.merge(future_matches_team_and_league, most_recent_opponent_df, on=['opponent'], how='left')

    def get_latest_past_stats(self):
        sorted_past_matches = self.sort_past_matches()
        most_recent_team_df = self.get_final_team_entry(sorted_past_matches)
        most_recent_team_df = self.remove_columns_containing_string(most_recent_team_df, 'opponent')
        return most_recent_team_df

    def sort_past_matches(self):
        return self.past_matches.data.sort_values(by='date', ascending=True)
    
    def get_final_team_entry(self, df):
        return pd.groupby(df, by='team').last().reset_index()
    
    def remove_columns_containing_string(self, df, string):
        cols_to_drop = [col for col in df.columns if string in col]
        return df.drop(cols_to_drop, axis=1) 
    
    def get_latest_opponent_stats(self, team_and_league_df):
        team_df = self.remove_columns_containing_string(team_and_league_df, 'league')
        opponent_df = self.replace_string_in_column_name('team', 'opponent', team_df)
        return opponent_df
    
    def replace_string_in_column_name(self, old_string, new_string, df):
        new_cols = [col.replace(old_string, new_string) if old_string in col else col for col in df.columns]
        df.columns = new_cols
        return df