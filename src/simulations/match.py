import pandas as pd
import numpy as np

class MatchSimulator:
    def __init__(self, match_id, home_team, away_team, win_prob, draw_prob, loss_prob):
        self.match_id = match_id
        self.home_team = home_team
        self.away_team = away_team
        self.win_prob = win_prob
        self.draw_prob = draw_prob
        self.loss_prob = loss_prob

    def simulate(self, num_simulations):
        home = np.random.choice(['win', 'draw', 'loss'], size=num_simulations, p=[self.win_prob, self.draw_prob, self.loss_prob])
        away = np.random.choice(['win', 'draw', 'loss'], size=num_simulations, p=[1-self.win_prob, 1-self.draw_prob, 1-self.loss_prob])
        match_results = pd.DataFrame({
            'match_id': [self.match_id] * num_simulations,
            'home_team': [self.home_team] * num_simulations,
            'away_team': [self.away_team] * num_simulations,
            'result': home + '-' + away
        })
        return match_results