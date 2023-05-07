import code
import pandas as pd
import numpy as np
# from simulations.match import MatchSimulator

class SeasonSimulator:
    def __init__(self, matches):
        self.matches = matches
        self.match_results = None

    def run_season_simulations(self, num_simulations):
        simulation_results = []
        for s in range(num_simulations):
            season_results = self.simulate_season()
            simulation_results.append(season_results)
        self.simulation_results = pd.concat(simulation_results)

    def simulate_season(self):
        simulation_results = []
        teams = set(self.matches['home_team'].unique()).union(set(self.matches['away_team'].unique()))
        team_points = dict(zip(teams, [0]*len(teams)))

        for i in range(len(self.matches)):
            match = self.matches.iloc[i]
            result = np.random.choice(['home_win', 'draw', 'away_win'], p=[match['home_win'], match['draw'], match['away_win']])
            home_team = match['home_team']
            away_team = match['away_team']
            if result == 'home_win':
                team_points[home_team] += 3
            elif result == 'draw':
                team_points[home_team] += 1
                team_points[away_team] += 1
            else:
                team_points[away_team] += 3

        return pd.DataFrame({'team': list(team_points.keys()), 'points': list(team_points.values())})





if __name__ == "__main__":
    # create a dataframe of match probabilities
    matches = pd.DataFrame({
        'match_id': [1, 2, 3],
        'home_team': ['Arsenal', 'Chelsea', 'Manchester United'],
        'away_team': ['Liverpool', 'Tottenham', 'Leicester'],
        'home_win': [0.4, 0.5, 0.6],
        'draw': [0.3, 0.2, 0.2],
        'away_win': [0.3, 0.3, 0.2]
    })

    # create match simulator objects
    simulator = SeasonSimulator(matches)
    simulator.run_simulations(1000)

    code.interact(local=locals())