import pandas as pd
from elos.elos import Elo


class Preprocessor:
    def __init__(self) -> None:
        pass

class EloPreprocessor(Preprocessor):
    def __init__(self, elo: Elo) -> None:
        super().__init__()
        self.elo = elo
        self.processed_matches = None

    def calculate_elos(self):
        self.elo.calculate()
        self.preprocessed_matches = self.elo.team_and_opp_matches
