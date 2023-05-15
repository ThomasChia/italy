import pandas as pd

class RestDaysPostProcessor:
    def __init__(self, df):
        self.df = df
        self.team_list = self.get_team_list(df)

    def calculate_rest_days(self):
        self.df['rest_days'] = 0
        self.df = self.sort_dates(self.df)

        for index, row in self.df.iterrows():
            team = row['team']
            self.df.loc[index, 'rest_days'] = (row['date'] - self.team_list.loc[team, 'last_played']).days
            self.team_list.loc[team, 'last_played'] = row['date']

        self.df.sort_values(by='date', inplace=True)
        self.df.reset_index(inplace=True, drop=True)

        return self.df

    def get_team_list(self, df):
        team_list = df['team'].unique()
        team_list = pd.DataFrame(team_list)
        team_list = team_list.rename(columns={list(team_list)[0]: 'teams'})
        team_list['last_played'] = pd.to_datetime('')
        team_list = team_list.set_index('teams')

        return team_list

    def sort_dates(self, df):
        df = df.sort_values(by='date')
        df = df.reset_index(drop=True)
        return df