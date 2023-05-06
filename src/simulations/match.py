import pandas as pd
import numpy as np

class Match:
    def __init__(self, home_team, away_team, win_prob, draw_prob):
        self.home_team = home_team
        self.away_team = away_team
        self.win_prob = win_prob
        self.draw_prob = draw_prob
    
    def simulate(self):
        outcome = np.random.choice(['win', 'draw', 'loss'], p=[self.win_prob, self.draw_prob, 1 - self.win_prob - self.draw_prob])
        if outcome == 'win':
            return (self.home_team, 'win')
        elif outcome == 'draw':
            return ('draw', 'draw')
        else:
            return (self.away_team, 'win')