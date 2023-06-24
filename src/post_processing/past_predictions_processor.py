import pandas as pd

class PastPredictionsProcessor:
    def __init__(self, past_predictions_df, future_predictions_df):
        self.past_predictions_df = past_predictions_df
        self.future_predictions_df = future_predictions_df
        self.latest_past_predictions = self.get_latest_past_predictions()

    def get_latest_past_predictions(self):
        merged = pd.merge(self.past_predictions_df, self.future_predictions_df, on=['match_id', 'team'], how='outer', suffixes=('_left', '_right'))
        diff = merged[merged['league_left'] != merged['league_right']]
        return diff