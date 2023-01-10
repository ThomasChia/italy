import requests
import pandas as pd
import datetime
import sqlite3

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
        competition = stage['Scd']
        if competition == 'serie-c-group-b':
            country = stage['Cnm']
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
                            'home': homeTeam,
                            'home_score': homeScore,
                            'away': awayTeam,
                            'away_score': awayScore,
                            'competition': competition,
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
                    'home_score',
                    'away_score',
                    ]
    string_columns = [
                    'home',
                    'away',
                    'competition',
                    'country',
                    'date'
    ]
    print(new_data)
    if not new_data.empty:
        new_data['event_id'] = new_data['event_id'].astype('int64')
        for column in numeric_columns:
            new_data[column] = new_data[column].astype('float')
        for column in string_columns:
            new_data[column] = new_data[column].astype('str')
        matches.append(new_data)

matches = pd.concat(matches)
matches.to_csv("../../data/past_matches.csv")