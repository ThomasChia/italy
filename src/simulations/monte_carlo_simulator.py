import code
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
        self.num_simulations = self.get_num_simulations()
        self.str_columns = self.get_str_columns()
        self.finishing_positions = None
        self.league_targets = None
    
    def get_num_simulations(self):
        num_cols = [col for col in self.simulation_results.columns if str(col).isdigit()]
        return len(num_cols)
    
    def get_str_columns(self):
        self.simulation_results.columns.name = None
        return [col for col in self.simulation_results.columns if any(c.isalpha() for c in str(col))]

    def get_finishing_positions(self):
        team_counts = {}
        position_counts = {}
        away_results = self.simulation_results.copy(deep=True).replace({3:0, 0:3})
        for simulation in range(1, self.num_simulations+1):
            home_points = self.simulation_results.groupby(by='home_team')[simulation].sum()
            away_points = away_results.groupby(by='away_team')[simulation].sum()
            total_points = pd.concat([home_points, away_points]).groupby(level=0).sum().sort_values(ascending=False)
            total_points = pd.DataFrame(total_points).reset_index()
            total_points['finishing_position'] = np.arange(1, len(total_points)+1)
            for j, row in total_points.iterrows():
                team = row['index']
                position = row['finishing_position']
                if team not in team_counts:
                    team_counts[team] = {position: 1}
                else:
                    if position not in team_counts[team]:
                        team_counts[team][position] = 1
                    else:
                        team_counts[team][position] += 1

            for j, row in total_points.iterrows():
                position = row['finishing_position']
                points = row[0]
                if position not in position_counts:
                    position_counts[position] = {position: np.array(points)}
                else:
                    position_counts[position].append(points)

        self.finishing_positions = pd.DataFrame(team_counts).T.sort_index().sort_index()
        self.league_targets = pd.DataFrame(position_counts)
    
    def get_league_targets(self):
        away_results = self.simulation_results.copy(deep=True).replace({3:0, 0:3})
        for simulation in range(1, self.num_simulations+1):
            home_points = self.simulation_results.groupby(by='home_team')[simulation].sum()
            away_points = away_results.groupby(by='away_team')[simulation].sum()
            total_points = pd.concat([home_points, away_points]).groupby(level=0).sum().sort_values(ascending=False)
            total_points = pd.DataFrame(total_points).reset_index()




if __name__ == "__main__":
    start_time = time.time()
    # create a dataframe of match probabilities
    matches = pd.DataFrame({
        'match_id': [1, 2, 3, 4],
        'home_team': ['Arsenal', 'Chelsea', 'Manchester United', 'Manchester City'],
        'away_team': ['Liverpool', 'Tottenham', 'Leicester', 'Arsenal'],
        'home_win': [0.4, 0.5, 0.6, 0.7],
        'draw': [0.3, 0.2, 0.2, 0.1],
        'away_win': [0.3, 0.3, 0.2, 0.2]
    })

    simulator = MonteCarloSimulator(matches)
    simulation_results = simulator.run_simulations(num_simulations=100)
    results = MonteCarloResults(simulation_results)
    results.get_finishing_positions()

    # access the simulation results as an attribute of the class
    # print(results.simulation_results.head())
    # print(results.simulation_results.shape)
    # print(results.num_simulations)

    end_time = time.time()
    print("Time elapsed: ", end_time - start_time, " seconds")

    code.interact(local=locals())