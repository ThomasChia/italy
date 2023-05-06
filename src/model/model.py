from config import FEATURES
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn import utils


class Model:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.x, self.y = self.split_features_results_data(FEATURES)
        self.scaler = None
        self.model = LogisticRegression(random_state=0, penalty='l2')


    def train(self) -> None:
        data_x_train, self.scaler = self.scale_features()
        self.model = self.train_model(data_x_train, self.y)

    def split_features_results_data(self, features_list):
        self.data = self.fill_and_sort(self.data)
        y = self.data[['result']].astype(float)
        x = self.data[features_list]
        lab = LabelEncoder()
        y = lab.fit_transform(y.values.ravel())

        return x, y

    def fill_and_sort(self, df):
        df.fillna(0, inplace=True)
        df.sort_values(by='date', inplace=True)
        return df

    def scale_features(self):
        scaler = StandardScaler()
        x_train_prepared = scaler.fit_transform(self.x)

        return x_train_prepared, scaler

    def train_model(self, x_train, y_train):
        print("Training model.")
        self.model.fit(x_train, y_train.ravel())

    def prepare_future_data(df, scaler, features_list):
        features_ = features_list
        df = df[features_]
        df.fillna(0, inplace=True)
        return scaler.transform(df)

    def predict(self, future_matches, features_list):
        df = self.prepare_future_data(future_matches, self.scaler, features_list)
        # predictions = self.model.predict(df)
        predictions_proba = self.model.predict_proba(df)
        future_matches = self.add_probabilities_to_matches(future_matches, predictions_proba)

        return future_matches
    
    def add_probabilities_to_matches(self, future_matches, probabilities):
        future_matches[['loss', 'draw', 'win']] = pd.DataFrame(probabilities)
        return future_matches