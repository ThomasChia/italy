from matches.matches import Matches
import pandas as pd
from preprocessing.builder.builder import Builder
from scrapers.scrapers import Scraper


class FutureBuilder:
    def __init__(self, future_matches: pd.DataFrame, past_matches: Builder) -> None:
        self.past_matches = past_matches
        self.future_matches = future_matches
        self.preprocessed_future_matches: pd.DataFrame = pd.DataFrame()

    def build_future_matches(self):
        self.add_past_stats_to_future_matches()

    def add_past_stats_to_future_matches(self):
        most_recent_team_df = self.get_latest_past_stats()
        most_recent_opponent_df = self.get_latest_opponent_stats(most_recent_team_df)
        future_matches_pt1 = pd.merge(self.future_matches, most_recent_team_df, left_on=['pt1', 'league'], right_on=['team', 'league'], how='left').rename(columns={'pt2': 'opponent'}).drop('pt1', axis=1)
        future_matches_pt1['home'] = 1
        future_matches_pt2 = pd.merge(self.future_matches, most_recent_team_df, left_on=['pt2', 'league'], right_on=['team', 'league'], how='left').rename(columns={'pt1': 'opponent'}).drop('pt2', axis=1)
        future_matches_pt2['home'] = 0
        future_matches_team_and_league = pd.concat([future_matches_pt1, future_matches_pt2]).reset_index(drop=True)
        self.preprocessed_future_matches = pd.merge(future_matches_team_and_league, most_recent_opponent_df, on=['opponent'], how='left')

    def get_latest_past_stats(self):
        sorted_past_matches = self.sort_past_matches()
        most_recent_team_df = self.get_final_team_entry(sorted_past_matches)
        most_recent_team_df = self.remove_columns_containing_string(most_recent_team_df, 'opponent')
        most_recent_team_df = self.remove_date_and_result(most_recent_team_df)
        most_recent_team_df = self.remove_match_id(most_recent_team_df)
        return most_recent_team_df

    def sort_past_matches(self):
        return self.past_matches.data.sort_values(by='date', ascending=True)
    
    def get_final_team_entry(self, df):
        return df.groupby('team').last().reset_index()
    
    def remove_columns_containing_string(self, df, string):
        cols_to_drop = [col for col in df.columns if string in col]
        return df.drop(cols_to_drop, axis=1) 
    
    def get_latest_opponent_stats(self, team_and_league_df):
        team_df = self.remove_columns_containing_string(team_and_league_df, 'league')
        opponent_df = self.replace_string_in_column_name('team', 'opponent', team_df)
        opponent_df = self.remove_match_id_elo_diff_home(opponent_df)
        return opponent_df
    
    def replace_string_in_column_name(self, old_string, new_string, df):
        new_cols = [col.replace(old_string, new_string) if old_string in col else col for col in df.columns]
        df.columns = new_cols
        return df
    
    def remove_date_and_result(self, df):
        return df.drop(['date', 'result'], axis=1)
    
    def remove_match_id_elo_diff_home(self, df):
        return df.drop(['match_id', 'elo_diff', 'home'], axis=1)
    
    def remove_match_id(self, df):
        return df.drop('match_id', axis=1)