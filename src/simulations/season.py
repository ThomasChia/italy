import pandas as pd
import numpy as np
from simulations.match import Match

class Season:
    def __init__(self, matches_df):
        self.matches = []
        for _, row in matches_df.iterrows():
            self.matches.append(Match(row['home_team'], row['away_team'], row['win_prob'], row['draw_prob']))
    
    def simulate(self, num_sims):
        results = pd.DataFrame(columns=['team', 'win', 'draw', 'loss'])
        for i in range(num_sims):
            sim_results = {}
            for match in self.matches:
                winner, outcome = match.simulate()
                if winner != 'draw':
                    if winner not in sim_results:
                        sim_results[winner] = {'win': 0, 'draw': 0, 'loss': 0}
                    sim_results[winner][outcome] += 1
            for team, outcomes in sim_results.items():
                if team not in results['team']:
                    results = results.append({'team': team, 'win': 0, 'draw': 0, 'loss': 0}, ignore_index=True)
                results.loc[results['team'] == team, 'win'] += outcomes['win']
                results.loc[results['team'] == team, 'draw'] += outcomes['draw']
                results.loc[results['team'] == team, 'loss'] += outcomes['loss']
        return results