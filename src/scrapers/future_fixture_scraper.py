"""
This file is to pull in future Italian fixtures for Serie C, Group B.
"""

from requests_html import AsyncHTMLSession
from collections import defaultdict
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def clean_data(df):
    df['date'] = df['date'].str[:-6]
    df['date'] = df['date'] + '2023'

    df['league'] = 'Serie C, Girone B'
    # df['league'] = 'Serie B'
    # df['league'] = 'Serie A'

    df = stand_names(df)

    return df

def stand_names(df):
    teams = {
        'entella': 'virtus_entella',
        'san_donato' :'san_donato_tavarnelle',
        'sassari_torres': 'torres',
        'montevarchi': 'aquila_montevarchi',
    }

    df['pt1'] = df['pt1'].replace(' ', '_', regex=True).str.lower()
    df['pt2'] = df['pt2'].replace(' ', '_', regex=True).str.lower()

    df['pt1'] = df['pt1'].replace(teams)
    df['pt2'] = df['pt2'].replace(teams)

    return df

url = 'https://www.flashscore.com/football/italy/serie-c-group-b/fixtures/'
# url = 'https://www.flashscore.com/football/italy/serie-b/fixtures/'
# url = 'https://www.flashscore.com/football/italy/serie-a/fixtures/'

PATH = '../../tools/chromedriver'
driver = webdriver.Chrome(PATH)
driver.get(url)
time.sleep(2)
cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
cookies.click()
button = driver.find_element(By.XPATH, '//*[@id="live-table"]/div[1]/div/div/a')
button.click()
time.sleep(2)

body = driver.find_element(By.XPATH, '//*[@id="live-table"]/div[1]/div/div')
times = body.find_elements(By.CSS_SELECTOR, "div.event__time")
home_teams = body.find_elements(By.CSS_SELECTOR, "div.event__participant.event__participant--home")
away_teams = body.find_elements(By.CSS_SELECTOR, "div.event__participant.event__participant--away")

dict_res = defaultdict(list)

for ind in range(len(times)):
    dict_res['date'].append(times[ind].text)
    dict_res['pt1'].append(home_teams[ind].text)
    # dict_res['scores'].append(scores[ind].text)
    dict_res['pt2'].append(away_teams[ind].text)
    # dict_res['event_part'].append(event_part[ind].text)

df_res = pd.DataFrame(dict_res)
df_res = clean_data(df_res)

# df_res.to_csv("../../data/future_matches_serie_a.csv")
# df_res.to_csv("../../data/future_matches_serie_b.csv")
df_res.to_csv("../../data/future_matches.csv")
print(df_res)

driver.quit()

