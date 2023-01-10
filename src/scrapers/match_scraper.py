import requests
import pandas as pd
import datetime
import sqlite3


def update_names(df, team_names):
    for old_team in team_names:
        df['pt1'] = df['pt1'].str.replace(old_team, team_names[old_team], regex=True)
        df['pt2'] = df['pt2'].str.replace(old_team, team_names[old_team], regex=True)


print((datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
date = "2022-09-01"
today = str((datetime.datetime.today()).strftime('%Y-%m-%d'))
# date ran 2022-11-14
dates = pd.date_range("2022-09-01", today, freq='D')

matches = []
# Scraping new matches for the day.
for date in dates:
    url = f"https://prod-public-api.livescore.com/v1/api/app/date/soccer/{date.strftime('%Y-%m-%d').replace('-', '')}/1?MD=1"
    jsonData = requests.get(url).json()

    rows = []
    for stage in jsonData['Stages']:
        country = stage['Cnm']
        if country == 'Italy':
            competition = stage['Scd']
            events = stage['Events']
            for event in events:
                try:
                    if event['Eps'] == 'FT':
                        # print(event)
                        eid = event['Eid']
                        gameDateTime = event['Esd']
                        date_time_obj = datetime.datetime.strptime(str(gameDateTime), '%Y%m%d%H%M%S')
                        gameTime = date_time_obj.strftime("%H:%M")
                        homeTeam = event['T1'][0]['Nm']
                        homeScore = event['Tr1']

                        awayTeam = event['T2'][0]['Nm']
                        awayScore = event['Tr2']

                        row = {
                            'event_id': eid,
                            'pt1': homeTeam,
                            'score_pt1': homeScore,
                            'pt2': awayTeam,
                            'score_pt2': awayScore,
                            'league': competition,
                            'country': country,
                            'date': date
                        }
                        
                        rows.append(row)
                except KeyError:
                    print("Error.")
                    continue
        else:
            pass

    print('Scraped matches.')
    new_data = pd.DataFrame(rows)
    numeric_columns = [
                    'score_pt1',
                    'score_pt2',
                    ]
    string_columns = [
                    'pt1',
                    'pt2',
                    'league',
                    'country',
                    'date'
    ]
    # print(new_data)
    if not new_data.empty:
        new_data['event_id'] = new_data['event_id'].astype('int64')
        for column in numeric_columns:
            new_data[column] = new_data[column].astype('float')
        for column in string_columns:
            new_data[column] = new_data[column].astype('str')
        matches.append(new_data)


TEAM_NAMES = {
    "AC Reggiana":"reggiana",
    "Alessandria": "alessandria",
    "Aquila Montevarchi": "aquila_montevarchi",
    "Carrarese": "carrarese",
    "Cesena FC": "cesena",
    "Fermana": "fermana",
    "Fiorenzuola": "fiorenzuola",
    "Gubbio": "gubbio",
    "Imolese Calcio": "imolese",
    "Lucchese": "lucchese",
    "Olbia": "olbia",
    "Pontedera": "pontedera",
    "Recanatese": "recanatese",
    "Rimini": "rimini",
    "Robur Siena": "siena",
    "San Donato": "san_donato_tavarnelle",
    "Torres": "sassari_torres",
    "U.S. Ancona": "ancona",
    "Virtus Entella": "virtus_entella",
    "Vis Pesaro": "vis_pesaro"
}

matches = pd.concat(matches)
update_names(matches, TEAM_NAMES)
matches.reset_index(inplace=True, drop=True)
matches.to_csv("../../data/past_matches.csv")