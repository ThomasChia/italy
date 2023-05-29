from config import (PROMOTED_TEAMS, PROMOTION_ELO_ADJUSTMENT, RELEGATED_TEAMS, RELEGATION_ELO_ADJUSTMENT)

class ManualAdjustor:
    def run(self, df):
        self.adjust_elos_promotion(df)
        self.adjust_elos_relegation(df)
        return df

    def adjust_elos_promotion(self, df):
        team_list = self.format_proper_team_names(PROMOTED_TEAMS)
        df['elo_team'] = df.apply(lambda row: row['elo_team'] + PROMOTION_ELO_ADJUSTMENT if row['team'] in team_list else row['elo_team'], axis=1)
        df['elo_opponent'] = df.apply(lambda row: row['elo_opponent'] + PROMOTION_ELO_ADJUSTMENT if row['opponent'] in team_list else row['elo_opponent'], axis=1)

    def adjust_elos_relegation(self, df):
        team_list = self.format_proper_team_names(RELEGATED_TEAMS)
        df['elo_team'] = df.apply(lambda row: row['elo_team'] + RELEGATION_ELO_ADJUSTMENT if row['team'] in team_list else row['elo_team'], axis=1)
        df['elo_opponent'] = df.apply(lambda row: row['elo_opponent'] + RELEGATION_ELO_ADJUSTMENT if row['opponent'] in team_list else row['elo_opponent'], axis=1)

    def format_proper_team_names(self, team_list):
        return [team.lower().replace(' ', '_') for team in team_list]