import pandas as pd
import numpy as np
from simulations.match import MatchSimulator

class SeasonSimulator:
    def __init__(self, matches):
        self.matches = matches

    def simulate(self, num_simulations):
        simulation_results = []
        for match in self.matches:
            match_simulator = MatchSimulator(match['match_id'], match['home_team'], match['away_team'], match['win'], match['draw'], match['loss'])
            match_results = match_simulator.simulate(num_simulations)
            simulation_results.append(match_results)
        simulation_results = pd.concat(simulation_results)
        return simulation_results

    def simulate_and_save(self, num_simulations):
        simulation_results = self.simulate(num_simulations)
        for match_id in simulation_results['match_id'].unique():
            match_results = simulation_results[simulation_results['match_id'] == match_id]
            match_results.to_csv(f'match_{match_id}_simulations.csv', index=False)


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

    # create match simulator objects
    match_simulators = []
    for i in range(len(matches)):
        match = matches.iloc[i]
        match_simulator = MatchSimulator(match['match_id'], match['home_team'], match['away_team'], match['win'], match['draw'], match['loss'])
        match_simulators.append(match_simulator)

    # create season simulator object and simulate the season
    season_simulator = SeasonSimulator(matches)
    # num_simulations = 1000000
    num_simulations = 10
    season_simulator.simulate_and_save(num_simulations)