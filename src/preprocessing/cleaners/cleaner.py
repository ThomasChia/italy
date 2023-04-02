import numpy as np
import pandas as pd
from loaders.loader import Loader
from config import TEAM_NAMES_DICT, LEAGUE_NAMES_DICT


class Cleaner:
    def __init__(self, loader: Loader) -> None:
        self.loader = loader

    def get_result(self):
        conditions = [
            self.loader.data['score_pt1'] > self.loader.data['score_pt2'],
            self.loader.data['score_pt1'] < self.loader.data['score_pt2'],
            self.loader.data['score_pt1'] == self.loader.data['score_pt2'],
        ]

        outputs = [
            1,
            0,
            0.5
        ]

        self.loader.data['result'] = np.select(conditions, outputs)
        return self.loader
    
    def order_by_date(self):
        self.loader.data = self.loader.data.sort_values(by='date')
        self.loader.data = self.loader.data.reset_index(drop=True)
    
    def clean_league_names(self):
        self.loader.data['league'] = self.loader.data['league'].replace(LEAGUE_NAMES_DICT)
        self.loader.data['league'] = self.loader.data['league'].replace(LEAGUE_NAMES_DICT)

    def clean_team_names(self):
        self.loader.data['pt1'] = self.loader.data['pt1'].replace(TEAM_NAMES_DICT)
        self.loader.data['pt2'] = self.loader.data['pt2'].replace(TEAM_NAMES_DICT)