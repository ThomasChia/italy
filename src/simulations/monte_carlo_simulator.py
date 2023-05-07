import pandas as pd
import numpy as np


class MonteCarloSimulator:
    def __init__(self, matches_df):
        self.matches_df = matches_df
        self.simulation_results = None

    def run_simulations(self, num_simulations):
        simulation_results = []
        for i in range(len(self.matches_df)):
            match = self.matches_df.iloc[i]
            home = np.random.choice(['win', 'draw', 'loss'], size=num_simulations, p=[match['win'], match['draw'], match['loss']])
            away = np.random.choice(['win', 'draw', 'loss'], size=num_simulations, p=[1-match['win'], 1-match['draw'], 1-match['loss']])
            match_results = pd.DataFrame({
                'match_id': [match['match_id']] * num_simulations,
                'home_team': [match['home_team']] * num_simulations,
                'away_team': [match['away_team']] * num_simulations,
                'result': home + '-' + away
            })
            simulation_results.append(match_results)
        self.simulation_results = pd.concat(simulation_results)


if __name__ == "__main__":
    # create a dataframe of match probabilities
    matches = pd.DataFrame({
        'match_id': [1, 2, 3],
        'home_team': ['Arsenal', 'Chelsea', 'Manchester United'],
        'away_team': ['Liverpool', 'Tottenham', 'Leicester'],
        'win': [0.4, 0.5, 0.6],
        'draw': [0.3, 0.2, 0.2],
        'loss': [0.3, 0.3, 0.2]
    })

    # create an instance of the MonteCarloSimulator class
    simulator = MonteCarloSimulator(matches)

    # run 1000000 simulations
    num_simulations = 100
    simulator.run_simulations(num_simulations)

    # access the simulation results as an attribute of the class
    print(simulator.simulation_results)