import config
import numpy as np
import pandas as pd


class Goals:
    team_stats = [
        'team_goals_scored',
        'team_goals_conceded',]
    opponent_stats = [
        'opponent_goals_scored',
        'opponent_goals_conceded',]
        
    def __init__(self, matches):
        self.matches: pd.DataFrame = matches

    def set_match_ids(self):
        self.matches['id'] = np.arange(1, len(self.matches)+1)