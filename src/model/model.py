from config import FEATURES
import logging
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
        self.train_model(data_x_train, self.y)

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
        logging.info("Fitting model to training data.")
        self.model.fit(x_train, y_train.ravel())

    def prepare_future_data(self, df, scaler, features_list):
        features_ = features_list
        df = df[features_]
        df.fillna(0, inplace=True)
        return scaler.transform(df)

    def predict(self, future_matches, features_list, id_features):
        prediction_features = [x for x in features_list if x not in id_features]
        df = self.prepare_future_data(future_matches, self.scaler, prediction_features)
        # predictions = self.model.predict(df)
        predictions_proba = self.model.predict_proba(df)
        future_matches = self.add_probabilities_to_matches(future_matches, predictions_proba)
        home_and_away_matches, team_and_opponent_matches = self.average_probailities(future_matches)
        return home_and_away_matches, team_and_opponent_matches
    
    def add_probabilities_to_matches(self, future_matches, probabilities):
        future_matches[['loss', 'draw', 'win']] = pd.DataFrame(probabilities)
        return future_matches
    
    def average_probailities(self, future_matches):
        home_matches = future_matches[future_matches['home'] == 1].rename(columns={'team': 'home_team',
                                                                                   'opponent': 'away_team',
                                                                                   'win': 'home_win',
                                                                                   'loss': 'away_win'}).drop('home', axis=1)
        away_matches = future_matches[future_matches['home'] == 0].rename(columns={'team': 'away_team',
                                                                                   'opponent': 'home_team',
                                                                                   'win': 'away_win',
                                                                                   'loss': 'home_win'}).drop('home', axis=1)
        home_and_away_matches = pd.concat([home_matches, away_matches])
        home_and_away_average_matches = home_and_away_matches.groupby(['home_team', 'away_team', 'league']).mean().reset_index()

        team_matches = home_and_away_average_matches[['home_team', 'away_team', 'league', 'home_win', 'draw', 'away_win']].rename(columns={'home_team': 'team',
                                                                                                                                 'away_team': 'opponent',
                                                                                                                                 'home_win': 'win',
                                                                                                                                 'away_win': 'loss'})
        opponent_matches = home_and_away_average_matches[['away_team', 'home_team', 'league', 'home_win', 'draw', 'away_win']].rename(columns={'away_team': 'team',
                                                                                                                                     'home_team': 'opponent',
                                                                                                                                     'home_win': 'loss',
                                                                                                                                     'away_win': 'win'})
        team_and_opponent_matches = pd.concat([team_matches, opponent_matches])
        return home_and_away_average_matches, team_and_opponent_matches