from config import (PROMOTED_TEAMS,
                    RELEGATED_TEAMS, 
                    PROMOTION_ELO_ADJUSTMENT, 
                    RELEGATION_ELO_ADJUSTMENT,
                    PROMOTION_GOAL_ADJUSTMENT,
                    RELEGATION_GOAL_ADJUSTMENT)

class ManualAdjustor:
    def run(self, df):
        self.adjust_elos_promotion(df)
        self.adjust_elos_relegation(df)
        self.adjust_goals_promotion(df)
        self.adjust_goals_relegation(df)
        return df

    def adjust_elos_promotion(self, df):
        team_list = self.format_proper_team_names(PROMOTED_TEAMS)
        df['elo_team'] = df.apply(lambda row: row['elo_team'] + PROMOTION_ELO_ADJUSTMENT if row['team'] in team_list else row['elo_team'], axis=1)
        df['elo_opponent'] = df.apply(lambda row: row['elo_opponent'] + PROMOTION_ELO_ADJUSTMENT if row['opponent'] in team_list else row['elo_opponent'], axis=1)

    def adjust_elos_relegation(self, df):
        team_list = self.format_proper_team_names(RELEGATED_TEAMS)
        df['elo_team'] = df.apply(lambda row: row['elo_team'] + RELEGATION_ELO_ADJUSTMENT if row['team'] in team_list else row['elo_team'], axis=1)
        df['elo_opponent'] = df.apply(lambda row: row['elo_opponent'] + RELEGATION_ELO_ADJUSTMENT if row['opponent'] in team_list else row['elo_opponent'], axis=1)

    def adjust_goals_promotion(self, df):
        team_list = self.format_proper_team_names(PROMOTED_TEAMS)
        df['team_goals_scored_avg'] = df.apply(lambda row: row['team_goals_scored_avg'] * PROMOTION_GOAL_ADJUSTMENT if row['team'] in team_list else row['team_goals_scored_avg'], axis=1)
        df['opponent_goals_scored_avg'] = df.apply(lambda row: row['opponent_goals_scored_avg'] * PROMOTION_GOAL_ADJUSTMENT  if row['opponent'] in team_list else row['opponent_goals_scored_avg'], axis=1)
        df['team_attack_strength'] = df.apply(lambda row: row['team_attack_strength'] * PROMOTION_GOAL_ADJUSTMENT  if row['team'] in team_list else row['team_attack_strength'], axis=1)
        df['team_defense_strength'] = df.apply(lambda row: row['team_defense_strength'] * (1/PROMOTION_GOAL_ADJUSTMENT)  if row['team'] in team_list else row['team_defense_strength'], axis=1)
        df['opponent_attack_strength'] = df.apply(lambda row: row['opponent_attack_strength'] * PROMOTION_GOAL_ADJUSTMENT  if row['opponent'] in team_list else row['opponent_attack_strength'], axis=1)
        df['opponent_defense_strength'] = df.apply(lambda row: row['opponent_defense_strength'] * (1/PROMOTION_GOAL_ADJUSTMENT)  if row['opponent'] in team_list else row['opponent_defense_strength'], axis=1)

    def adjust_goals_relegation(self, df):
        team_list = self.format_proper_team_names(RELEGATED_TEAMS)
        df['team_goals_scored_avg'] = df.apply(lambda row: row['team_goals_scored_avg'] * RELEGATION_GOAL_ADJUSTMENT if row['team'] in team_list else row['team_goals_scored_avg'], axis=1)
        df['opponent_goals_scored_avg'] = df.apply(lambda row: row['opponent_goals_scored_avg'] * RELEGATION_GOAL_ADJUSTMENT  if row['opponent'] in team_list else row['opponent_goals_scored_avg'], axis=1)
        df['team_attack_strength'] = df.apply(lambda row: row['team_attack_strength'] * RELEGATION_GOAL_ADJUSTMENT  if row['team'] in team_list else row['team_attack_strength'], axis=1)
        df['team_defense_strength'] = df.apply(lambda row: row['team_defense_strength'] * (1/RELEGATION_GOAL_ADJUSTMENT)  if row['team'] in team_list else row['team_defense_strength'], axis=1)
        df['opponent_attack_strength'] = df.apply(lambda row: row['opponent_attack_strength'] * RELEGATION_GOAL_ADJUSTMENT  if row['opponent'] in team_list else row['opponent_attack_strength'], axis=1)
        df['opponent_defense_strength'] = df.apply(lambda row: row['opponent_defense_strength'] * (1/RELEGATION_GOAL_ADJUSTMENT)  if row['opponent'] in team_list else row['opponent_defense_strength'], axis=1)

    def format_proper_team_names(self, team_list):
        return [team.lower().replace(' ', '_') for team in team_list]