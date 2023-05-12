import code
from config import DASHBOARD_LEAGUES
import pandas as pd
import numpy as np
import time
from matches.matches import PastMatches


class MonteCarloSimulator:
    def __init__(self, matches_df):
        self.matches_df = matches_df
        self.simulation_results = None

    def run_simulations(self, num_simulations):
        self.matches_df['match_id'] = np.arange(1, len(self.matches_df)+1)
        simulation_results = []
        for i in range(len(self.matches_df)):
            match = self.matches_df.iloc[i]
            result = np.random.choice([3, 1, 0], size=num_simulations, p=[match['home_win'], match['draw'], match['away_win']])
            match_results = pd.DataFrame({
                'match_id': [match['match_id']] * num_simulations,
                'league': [match['league']] * num_simulations,
                'home_team': [match['home_team']] * num_simulations,
                'away_team': [match['away_team']] * num_simulations,
                'result': result,
                'season': np.arange(1, num_simulations+1)
            }).pivot_table(index=['match_id', 'home_team', 'away_team', 'league'],
                          columns='season', values='result',
                          aggfunc='sum', fill_value=0).reset_index()
            simulation_results.append(match_results)
        return pd.concat(simulation_results)


class MonteCarloResults:
    def __init__(self, simulation_results, past_results=None, season_start=None):
        self.past_results: PastMatches = past_results
        self.simulation_results = simulation_results
        self.season_start = season_start
        self.num_simulations = self.get_num_simulations()
        self.str_columns = self.get_str_columns()
        self.finishing_positions = None
        self.league_targets = None
        self.match_importance = None
        self.next_match = None
        self.next_match_simulations = None

        if self.past_results:
            self.past_results.filter_by_date(self.season_start)
            self.past_results.align_to_simultions(num_simulations=self.num_simulations)
            self.full_season = pd.concat([self.past_results.matches_df, self.simulation_results])
        else:
            self.full_season = self.simulation_results
    
    def get_num_simulations(self):
        num_cols = [col for col in self.simulation_results.columns if str(col).isdigit()]
        return len(num_cols)
    
    def get_str_columns(self):
        self.simulation_results.columns.name = None
        return [col for col in self.simulation_results.columns if any(c.isalpha() for c in str(col))]

    def get_finishing_positions(self):
        self.get_next_match_simulated_result()
        for league in DASHBOARD_LEAGUES:
            league_full_season = self.full_season[self.full_season['league']==league]
            team_counts = {}
            position_counts = {}
            away_results = league_full_season.copy(deep=True).replace({3:0, 0:3})
            for simulation in range(1, self.num_simulations+1):
                home_points = league_full_season.groupby(by='home_team')[simulation].sum()
                away_points = away_results.groupby(by='away_team')[simulation].sum()
                total_points = pd.concat([home_points, away_points]).groupby(level=0).sum().sort_values(ascending=False)
                total_points = pd.DataFrame(total_points).reset_index()
                total_points['finishing_position'] = np.arange(1, len(total_points)+1)
                for j, row in total_points.iterrows():
                    team = row['index']
                    position = row['finishing_position']
                    points = row.iloc[1]
                    result = self.next_match_simulations.loc[team, simulation-1]
                    if team not in team_counts:
                        team_counts[team] = {str(position) + '_' + str(result): 1}
                    else:
                        if str(position) + '_' + str(result) not in team_counts[team]:
                            team_counts[team][str(position) + '_' + str(result)] = 1
                        else:
                            team_counts[team][str(position) + '_' + str(result)] += 1

                    if position not in position_counts:
                        position_counts[position] = np.array(points)
                    else:
                        position_counts[position] = np.append(position_counts[position], points)

            league_match_importance = pd.DataFrame(team_counts).sort_index().T.sort_index()
            league_match_importance['league'] = league
            single_league_targets = pd.DataFrame(position_counts).mean().reset_index(drop=True)
            single_league_targets['league'] = league

            if self.match_importance is None:
                self.match_importance = league_match_importance
            else:
                self.match_importance = pd.concat([self.match_importance, league_match_importance])
            if self.league_targets is None:
                self.league_targets = single_league_targets
            else:
                self.league_targets = pd.concat([self.league_targets, single_league_targets])
            self.combine_finishing_positions()
    
    def get_next_match(self):
        teams = pd.concat([self.simulation_results['home_team'], self.simulation_results['away_team']]).unique()
        next_match = {team: None for team in teams}
        for _, row in self.simulation_results.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            
            if next_match[home_team] is None:
                next_match[home_team] = (away_team, 'home')
                
            if next_match[away_team] is None:
                next_match[away_team] = (home_team, 'away')
        return next_match

    def get_next_match_simulated_result(self):
        next_matches = self.get_next_match()
        next_match_simulations = {}
        for team, next_match in next_matches.items():
            if next_match[1] == 'home':
                next_match_simulations[team] = self.simulation_results[(self.simulation_results['home_team']==team) &
                                                                       (self.simulation_results['away_team']==next_match[0])].iloc[:, 3:].values[0]
            elif next_match[1] == 'away':
                next_match_simulations[team] = self.simulation_results[(self.simulation_results['home_team']==next_match[0]) &
                                                                       (self.simulation_results['away_team']==team)].iloc[:, 3:].replace({3:0, 0:3}).values[0]
        self.next_match_simulations = pd.DataFrame(next_match_simulations).T

    def combine_finishing_positions(self):
        finishing_positions = self.match_importance.copy(deep=True)
        current_cols = finishing_positions.columns
        new_cols = [col.split('_')[0] for col in current_cols]
        finishing_positions.columns = new_cols
        finishing_positions = finishing_positions.groupby(axis=1, level=0).sum()
        if self.finishing_positions is None:
            self.finishing_positions = finishing_positions
        else:
            self.finishing_positions = pd.concat([self.finishing_positions, finishing_positions])
        



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
    simulation_results = simulator.run_simulations(num_simulations=10)
    results = MonteCarloResults(simulation_results)
    results.get_finishing_positions()

    # access the simulation results as an attribute of the class
    # print(results.simulation_results.head())
    # print(results.simulation_results.shape)
    # print(results.num_simulations)

    end_time = time.time()
    print("Time elapsed: ", end_time - start_time, " seconds")

    code.interact(local=locals())