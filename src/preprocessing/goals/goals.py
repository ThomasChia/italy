import config
import numpy as np
import pandas as pd


class TeamGoals:
    # team_stats = [
    #     'team_goals_scored',
    #     'team_goals_conceded',]
    # opponent_stats = [
    #     'opponent_goals_scored',
    #     'opponent_goals_conceded',]
        
    def __init__(self, matches):
        self.matches: pd.DataFrame = matches
        self.team_stats = ['team_goals_scored',
                           'team_goals_conceded',]
        self.opponent_stats = ['opponent_goals_scored',
                               'opponent_goals_conceded',]
        self.teams_list = self.get_team_list()
        self.team_rolling = None
        self.opponent_rolling = None
        self.team_and_opponent_rolling = None

    def set_match_ids(self):
        self.matches['id'] = np.arange(1, len(self.matches)+1)

    def get_team_list(self):
        return self.matches['team'].unique().tolist()
    
    def calculate_team_averages(self):
        self.team_rolling = self.get_all_rolling_averages(stats_list=self.team_stats, for_team=True)
        self.opponent_rolling = self.get_all_rolling_averages(stats_list=self.opponent_stats, for_team=False)
        self.team_and_opponent_rolling = self.merge_on_common_columns(self.team_rolling, self.opponent_rolling)

    def get_all_rolling_averages(self, stats_list, for_team):
        self.set_match_ids()
        matches_average = pd.DataFrame(columns=self.matches.columns)
        for team in self.teams_list:
            df_temp = self.get_team_rolling_average(team,
                                                    stats_list,
                                                    for_team)
            matches_average = pd.concat([matches_average, df_temp])
        matches_average = matches_average.drop(['id'], axis=1)
        return matches_average
    
    def merge_on_common_columns(self, df1, df2):
        common_columns = list(set(df1.columns).intersection(df2.columns))
        df = pd.merge(df1, df2, on=common_columns)
        return df
    
    def filter_to_team(self, team):
        df_stat = self.matches[self.matches['team'] == team]
        df_stat_home = self.matches[(self.matches['team'] == team) & (self.matches['home'] == 1)]
        df_stat_away = self.matches[(self.matches['team'] == team) & (self.matches['home'] == 0)]
        return df_stat, df_stat_home, df_stat_away
    
    def filter_to_opponent(self, team):
        df_stat = self.matches[self.matches['opponent'] == team]
        df_stat_home = self.matches[(self.matches['opponent'] == team) & (self.matches['home'] == 0)]
        df_stat_away = self.matches[(self.matches['opponent'] == team) & (self.matches['home'] == 1)]
        return df_stat, df_stat_home, df_stat_away

    def get_team_specific_df(self, team, for_team: bool):
        if for_team:
            df_stat, df_stat_home, df_stat_away = self.filter_to_team(team)
        else:
            df_stat, df_stat_home, df_stat_away = self.filter_to_opponent(team)
        return Statistics(df_stat, df_stat_home, df_stat_away)

    def get_team_rolling_average(self, team, stat_list, for_team=True):
        statistics = self.get_team_specific_df(team, for_team)
        
        for stat in stat_list:
            statistics.calc_rolling_average(stat)
            if not any(substring in stat for substring in ['home', 'away']):
                statistics.calc_rolling_average_home(stat)
                statistics.calc_rolling_average_away(stat)
        
        statistics.format_home_and_away()
        statistics.combine_neutral_home_and_away()
        
        return statistics.stat_processed
    
class LeagueGoals:
    def __init__(self, matches: pd.DataFrame) -> None:
        self.matches = matches
        self.matches_home = self.cut_to_home()
        self.matches_away = self.cut_to_away()
        self.league_rolling_scored = None
        self.league_rolling_conceded = None

    def calculate_league_averages(self, scored_or_conceded):
        self.set_match_ids()
        home_average, away_average = self.pivot_matches(scored_or_conceded)
        leagues = home_average.columns
        # statistics = Statistics(self.matches, home_average, away_average)
        for column in leagues:
            statistics = Statistics(self.matches, home_average[column], away_average[column])
            statistics.get_rolling_average_column(column)
            home_average = home_average.merge(statistics.stat_home, left_on='date', right_on='date')
            away_average = away_average.merge(statistics.stat_away, left_on='date', right_on='date')

        home_average = home_average.ffill().reset_index()
        away_average = away_average.ffill().reset_index()

        # Adding in the league goals scored/conceded each match day. Probably not needed in the model.
        home_average_merge = pd.merge(self.matches, home_average.melt(id_vars='date', var_name='league')
                                        , on=['league','date'])
        away_average_merge = pd.merge(self.matches, away_average.melt(id_vars='date', var_name='league')
                                        , on=['league','date'])

        home_average_merge.rename(columns={'value': 'league_home_goals_'  + scored_or_conceded}, inplace=True)
        away_average_merge.rename(columns={'value': 'league_away_goals_'  + scored_or_conceded}, inplace=True)

        df_merge = home_average_merge.copy()
        df_merge['league_away_goals_' + scored_or_conceded] = away_average_merge['league_away_goals_' + scored_or_conceded]

        # Adding in the league average goals scored/conceded
        home_average.drop(leagues, axis=1, inplace=True)
        away_average.drop(leagues, axis=1, inplace=True)
        for column in home_average.columns:
            if column[-9:] == '_avg_home':
                home_average.rename(columns={column: column[:-9]}, inplace=True)
        for column in away_average.columns:
            if column[-9:] == '_avg_away':
                away_average.rename(columns={column: column[:-9]}, inplace=True)
        
        home_average_merge = pd.merge(home_average_merge, home_average.melt(id_vars='date', var_name='league')
                                        , on=['league','date'])
        away_average_merge = pd.merge(away_average_merge, away_average.melt(id_vars='date', var_name='league')
                                        , on=['league','date'])

        home_average_merge.rename(columns={'value': 'league_home_goals_'  + scored_or_conceded + '_avg'}, inplace=True)
        away_average_merge.rename(columns={'value': 'league_away_goals_'  + scored_or_conceded + '_avg'}, inplace=True)

        df_merge_avg = home_average_merge.copy()
        df_merge_avg['league_away_goals_' + scored_or_conceded + '_avg'] = away_average_merge['league_away_goals_' + scored_or_conceded + '_avg']
        df_merge = self.merge_on_common_columns(df_merge, df_merge_avg)
        df_merge = df_merge.sort_values(by='date')
        df_merge = df_merge.reset_index(drop=True)
        df_merge = df_merge.drop('id', axis=1)

        return df_merge


    def calculate_single_stat_average(self, home_average, away_average, column):
        s_h = home_average[['date', column]].copy()
        s_a = away_average[['date', column]].copy()

    def set_match_ids(self):
        self.matches['id'] = np.arange(1, len(self.matches)+1)

    def cut_to_home(self):
        return self.matches[self.matches['home']==1]
    
    def cut_to_away(self):
        return self.matches[self.matches['home']==0]
    
    def pivot_matches(self, scored_or_conceded):
        home_pivot = self.matches_home.pivot_table('team_goals_' + scored_or_conceded, index='date', columns='league')
        away_pivot = self.matches_away.pivot_table('team_goals_' + scored_or_conceded, index='date', columns='league')
        return home_pivot, away_pivot
    
    def calc_rolling_average_home(self, stat_name: str):
        self.stat_home.loc[:, stat_name + '_avg_home'] = self.stat_home[stat_name].shift(1).rolling(19).mean()

    def calc_rolling_average_away(self, stat_name: str):
        self.stat_away.loc[:, stat_name + '_avg_away'] = self.stat_away[stat_name].shift(1).rolling(19).mean()

    def merge_on_common_columns(self, df1, df2):
        common_columns = list(set(df1.columns).intersection(df2.columns))
        return pd.merge(df1, df2, on=common_columns)
    
class PoissonGoals:
    def __init__(self, team_matches: pd.DataFrame, league_matches: pd.DataFrame):
        self.team_matches = team_matches
        self.league_matches = league_matches
        # self.poisson_matches = None

    def calculate_poisson_goals(self):
        all_matches = self.merge_on_common_columns(self.team_matches, self.league_matches)
        return self.calc_strength(all_matches)

    def merge_on_common_columns(self, df1, df2):
        common_columns = list(set(df1.columns).intersection(df2.columns))
        return pd.merge(df1, df2, on=common_columns)
    
    def calc_strength(self, df):
        conditions = [
            df['home'] == 1,
            df['home'] == 0
        ]

        output_team_score = [
            df['team_goals_scored_avg_home'] / df['league_home_goals_scored_avg'],
            df['team_goals_scored_avg_away'] / df['league_away_goals_scored_avg']
        ]

        output_team_concede = [
            df['team_goals_conceded_avg_home'] / df['league_home_goals_conceded_avg'],
            df['team_goals_conceded_avg_away'] / df['league_away_goals_conceded_avg']
        ]

        output_opponent_score = [
            df['opponent_goals_scored_avg_away'] / df['league_away_goals_scored_avg'],
            df['opponent_goals_scored_avg_home'] / df['league_home_goals_scored_avg']
        ]

        output_opponent_concede = [
            df['opponent_goals_conceded_avg_away'] / df['league_away_goals_conceded_avg'],
            df['opponent_goals_conceded_avg_home'] / df['league_home_goals_conceded_avg']
        ]

        df['team_attack_strength'] = np.select(conditions, output_team_score, 'Other').astype(float)
        df['team_defense_strength'] = np.select(conditions, output_team_concede, 'Other').astype(float)
        df['opponent_attack_strength'] = np.select(conditions, output_opponent_score, 'Other').astype(float)
        df['opponent_defense_strength'] = np.select(conditions, output_opponent_concede, 'Other').astype(float)

        df.replace(np.nan, 0, inplace=True)
        df.replace('nan', 0, inplace=True)
        df.replace([np.inf, -np.inf], 0, inplace=True)

        return df


class Statistics:
    def __init__(self, stat_neutral: pd.DataFrame, stat_home: pd.DataFrame, stat_away: pd.DataFrame):
        self.stat_neutral = stat_neutral
        self.stat_home = stat_home
        self.stat_away = stat_away
        self.stat_home_and_away = None
        self.stat_processed = None

    def calc_rolling_average(self, stat_name: str):
        self.stat_neutral.loc[:, stat_name + '_avg'] = self.stat_neutral[stat_name].shift(1).rolling(19, min_periods=1).mean()

    def calc_rolling_average_home(self, stat_name: str):
        self.stat_home.loc[:, stat_name + '_avg_home'] = self.stat_home[stat_name].shift(1).rolling(19, min_periods=1).mean()

    def calc_rolling_average_away(self, stat_name: str):
        self.stat_away.loc[:, stat_name + '_avg_away'] = self.stat_away[stat_name].shift(1).rolling(19, min_periods=1).mean()

    def calc_league_rolling_average_home(self, stat_name: str):
        rolling_average = pd.Series(self.stat_home.shift(1).rolling(50, min_periods=1).mean(), name=stat_name + '_avg_home')
        self.stat_home = pd.concat([self.stat_home, rolling_average], axis=1)
        # self.stat_home[stat_name + '_avg_home'] = self.stat_home.shift(1).rolling(19, min_periods=1).mean()

    def calc_league_rolling_average_away(self, stat_name: str):
        rolling_average = pd.Series(self.stat_away.shift(1).rolling(50, min_periods=1).mean(), name=stat_name + '_avg_away')
        self.stat_away = pd.concat([self.stat_away, rolling_average], axis=1)
        # self.stat_away.loc[:, stat_name + '_avg_away'] = self.stat_away.shift(1).rolling(19, min_periods=1).mean()

    def combine_home_and_away(self):
        self.stat_home_and_away = pd.concat([self.stat_home, self.stat_away])

    def cut_to_average_columns(self, columns):
        self.stat_home_and_away = self.stat_home_and_away[columns + ['team', 'date']]

    def format_home_and_away(self):
        average_columns = self.get_average_column_names()
        self.combine_home_and_away()
        self.cut_to_average_columns(average_columns)
        
    def combine_neutral_home_and_away(self):
        self.stat_processed = self.stat_neutral.merge(self.stat_home_and_away, 
                                                      on=['team', 'date'],
                                                      how='outer')
        self.sort_processed_by_date()
        self.backfill_stats_processed()
        self.forwardfill_stats_processed()

    def get_average_column_names(self):
        return [col for col in self.stat_home.columns if 'avg' in col] + [col for col in self.stat_away.columns if 'avg' in col]
    
    def sort_processed_by_date(self):
        self.stat_processed = self.stat_processed.sort_values(by='date')
        self.stat_processed = self.stat_processed.reset_index(drop=True)

    def backfill_stats_processed(self):
        average_columns = self.get_average_column_names()
        self.stat_processed.loc[:, average_columns] = self.stat_processed.loc[:,average_columns].bfill()

    def forwardfill_stats_processed(self):
        average_columns = self.get_average_column_names()
        self.stat_processed.loc[:, average_columns] = self.stat_processed.loc[:, average_columns].ffill()

    def get_avg_column(self, df):
        avg_column = [col for col in df.columns if 'avg' in col]
        return df.loc[:, avg_column]
    
    def get_rolling_average_column(self, column):
        self.calc_league_rolling_average_home(column)
        self.calc_league_rolling_average_away(column)
        self.stat_home = self.get_avg_column(self.stat_home)
        self.stat_away = self.get_avg_column(self.stat_away)