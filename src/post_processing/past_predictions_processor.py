import pandas as pd

class PastPredictionsProcessor:
    def __init__(self, past_predictions: pd.DataFrame, future_predictions: pd.DataFrame):
        self.past_predictions: pd.DataFrame = past_predictions
        self.future_predictions: pd.DataFrame = future_predictions
        self.columns = future_predictions.columns
        self.latest_past_predictions = self.get_latest_past_predictions()

    def get_latest_past_predictions(self):
        self.past_predictions = self.align_team_name_format(self.past_predictions)
        merged = pd.merge(self.past_predictions, self.future_predictions, on=['match_id', 'team'], how='outer', suffixes=('_left', '_right'))
        latest_past_predictions_match_ids = merged[merged['league_left'] != merged['league_right']]['match_id'].to_list()
        latest_past_predictions = self.past_predictions[self.past_predictions['match_id'].isin(latest_past_predictions_match_ids)]
        latest_past_predictions = self.cut_columns(latest_past_predictions)
        return latest_past_predictions
    
    def cut_columns(self, df):
        return df[self.columns]
    
    def align_team_name_format(self, df):
        df['team'] = df['team'].str.replace(' ', '_').str.lower()
        df['opponent'] = df['opponent'].str.replace(' ', '_').str.lower()
        return df
