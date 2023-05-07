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
            result = np.random.choice([3, 1, 0], size=num_simulations, p=[match['home_win'], match['draw'], match['away_win']])
            match_results = pd.DataFrame({
                'match_id': [match['match_id']] * num_simulations,
                'home_team': [match['home_team']] * num_simulations,
                'away_team': [match['away_team']] * num_simulations,
                'result': result,
                'season': np.arange(1, num_simulations+1)
            }).pivot_table(index=['match_id', 'home_team', 'away_team'],
                          columns='season', values='result',
                          aggfunc='sum', fill_value=0).reset_index()
            simulation_results.append(match_results)
        return pd.concat(simulation_results)


class MonteCarloResults:
    def __init__(self, simulation_results, season_simulation_results=None):
        self.simulation_results = simulation_results
        self.season_simulation_results = season_simulation_results

    def get_win_percentage(self, team):
        team_results = self.simulation_results[self.simulation_results['home_team'] == team]
        team_wins = (team_results['result'] == 'home_win').sum() + (team_results['result'] == 'away_win').sum()
        total_matches = len(team_results)
        return team_wins / total_matches



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

    simulator = MonteCarloSimulator(matches)
    simulation_results = simulator.run_simulations(num_simulations=1000)
    results = MonteCarloResults(simulation_results)

    # access the simulation results as an attribute of the class
    print(results.simulation_results.head())
    print(results.simulation_results.shape)

    end_time = time.time()
    print("Time elapsed: ", end_time - start_time, " seconds")