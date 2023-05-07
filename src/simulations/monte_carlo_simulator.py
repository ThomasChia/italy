import pandas as pd
import numpy as np
import time


class MonteCarloSimulator:
    def __init__(self, matches_df):
        self.matches_df = matches_df
        self.simulation_results = None

    def run_simulations(self, num_simulations):
        simulation_results = []
        for i in range(len(self.matches_df)):
            match = self.matches_df.iloc[i]
            result = np.random.choice(['home_win', 'draw', 'away_win'], size=num_simulations, p=[match['home_win'], match['draw'], match['away_win']])
            # away = np.random.choice(['away_win', 'draw', 'home_win'], size=num_simulations, p=[match['away_win'], match['draw'], match['home_win']])
            match_results = pd.DataFrame({
                'match_id': [match['match_id']] * num_simulations,
                'home_team': [match['home_team']] * num_simulations,
                'away_team': [match['away_team']] * num_simulations,
                'result': result
            })
            simulation_results.append(match_results)
        self.simulation_results = pd.concat(simulation_results)


if __name__ == "__main__":
    start_time = time.time()
    # create a dataframe of match probabilities
    matches = pd.DataFrame({
        'match_id': [1, 2, 3],
        'home_team': ['Arsenal', 'Chelsea', 'Manchester United'],
        'away_team': ['Liverpool', 'Tottenham', 'Leicester'],
        'home_win': [0.4, 0.5, 0.6],
        'draw': [0.3, 0.2, 0.2],
        'away_win': [0.3, 0.3, 0.2]
    })

    # create an instance of the MonteCarloSimulator class
    simulator = MonteCarloSimulator(matches)

    # run 1000000 simulations
    num_simulations = 1000000
    simulator.run_simulations(num_simulations)

    # access the simulation results as an attribute of the class
    print(simulator.simulation_results.head())
    print(simulator.simulation_results.shape)

    end_time = time.time()
    print("Time elapsed: ", end_time - start_time, " seconds")