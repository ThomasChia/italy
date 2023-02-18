import numpy as np
import pandas as pd
from loaders.loader import Loader


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
    
    def clean_league_names(self):
        pass