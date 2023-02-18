import pandas as pd
from loaders.loader import Loader


class Cleaner:
    def __init__(self, loader: Loader) -> None:
        self.matches = matches

    def get_result(self):
        conditions = [
            self.matches['score_pt1'] > self.matches['score_pt2'],
            self.matches['score_pt1'] < self.matches['score_pt2'],
            self.matches['score_pt1'] == self.matches['score_pt2'],
        ]

        outputs = [
            1,
            0,
            0.5
        ]

        self.matches['result'] = np.select(conditions, outputs)