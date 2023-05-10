import numpy as np
import pandas as pd
from loaders.loader import Loader
import logging
from config import TEAM_NAMES_DICT, LEAGUE_NAMES_MAPPING


class Cleaner:
    def __init__(self, loader: Loader) -> None:
        # self.loader = loader
        self.data = loader.data

    def clean(self):
        self.clean_league_names()
        self.clean_team_names()
        self.get_result()
        self.order_by_date()

    def get_result(self):
        logging.info(f"Converting score to result")
        conditions = [
            self.data['score_pt1'] > self.data['score_pt2'],
            self.data['score_pt1'] < self.data['score_pt2'],
            self.data['score_pt1'] == self.data['score_pt2'],
        ]

        outputs = [
            1,
            0,
            0.5
        ]

        self.data['result'] = np.select(conditions, outputs)
        return self.data
    
    def order_by_date(self):
        logging.info(f"Ordering by date")
        self.data = self.data.sort_values(by='date')
        self.data = self.data.reset_index(drop=True)
    
    def clean_league_names(self):
        logging.info(f"Cleaning league names")
        self.data['league'] = self.data['league'].replace(LEAGUE_NAMES_MAPPING)
        self.data['league'] = self.data['league'].replace(LEAGUE_NAMES_MAPPING)

    def clean_team_names(self):
        logging.info(f"Cleaning team names")
        self.data['pt1'] = self.data['pt1'].replace(TEAM_NAMES_DICT)
        self.data['pt2'] = self.data['pt2'].replace(TEAM_NAMES_DICT)