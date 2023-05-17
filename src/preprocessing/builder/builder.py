import numpy as np
import pandas as pd
from preprocessing.preprocessors import Preprocessor
from config import DEPENDENT_FEATURE, ID_FEATURES, FEATURES
import logging

class Builder:
    def __init__(self, preprocessors: Preprocessor):
        self.preprocessed_matches = self.get_preprocessed_matches(preprocessors)
        self.data: pd.DataFrame = pd.DataFrame()

    def get_preprocessed_matches(self, preprocessors):
        matches = []
        for data in preprocessors:
            matches.append(data.preprocessed_matches)
        return matches

    def build_dataset(self):
        merged_data = self.merge_on_common_columns(self.preprocessed_matches)
        self.data = self.cut_to_features(merged_data, DEPENDENT_FEATURE + ID_FEATURES + FEATURES)
        logging.info(f"Dataset built with shape: {self.data.shape}.")

    def cut_to_features(self, df, features_list):
        return df[features_list]
    
    def merge_on_common_columns(self, dfs):
        """
        Merges an arbitrary number of data frames on common columns using an inner join.
        Args:
            *dfs: One or more data frames to merge.
        Returns:
            A merged data frame.
        """
        if len(dfs) < 2:
            raise ValueError("At least two data frames are required to perform a merge.")

        merged_df = dfs[0]
        for df in dfs[1:]:
            common_cols = list(set(merged_df.columns) & set(df.columns))
            if not common_cols:
                raise ValueError("No common columns found to merge data frames.")
            merged_df = pd.merge(merged_df, df, on=common_cols, how='inner')

        return merged_df