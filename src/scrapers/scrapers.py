from collections import defaultdict
import logging
from matches.matches import Matches
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


class Scraper:
    def __init__(self):
        self.PATH = '../../tools/chromedriver'
        self.driver = None
        self.matches = None


class FlashScoreScraper(Scraper):
    def __init__(self, matches: Matches):
        super().__init__()
        self.base_url = f'https://www.flashscore.com/football/'
        self.matches = matches
        self.site_active = True

    def get_matches(self):
        for league in self.matches.leagues:
            logging.info(f"Getting matches for {league}")
            league_url = self.base_url + self.matches.country + '/' + league + '/fixtures/'
            self.driver = webdriver.Chrome(self.PATH)
            self.driver.get(league_url)
            self.click_cookies()
            if self.site_active:
                self.get_fixture_data(league=league)            

    def click_cookies(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-reject-all-handler"]')))
            cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
            cookies.click()
            self.site_active = True
        except Exception as e:
            self.site_active = False

    def get_fixture_data(self, league):
        times, years, home_teams, away_teams = self.get_fixture_elements()
        self.store_future_matches(times, years, home_teams, away_teams, league)

    def get_fixture_elements(self):
        body = self.driver.find_element(By.XPATH, '//*[@id="live-table"]/div[1]/div/div')
        years = body.find_elements(By.XPATH, '//*[@id="mc"]/div[4]/div[1]/div[2]/div[2]')[0].text
        times = body.find_elements(By.CSS_SELECTOR, "div.event__time")
        home_teams = body.find_elements(By.CSS_SELECTOR, "div.event__participant.event__participant--home")
        away_teams = body.find_elements(By.CSS_SELECTOR, "div.event__participant.event__participant--away")

        return times, years, home_teams, away_teams
    
    def store_future_matches(self, times, years, home_teams, away_teams, league):
        for ind in range(len(times)):
            date = self.get_date(times, years, ind)
            self.matches.matches_dict['date'].append(date)
            self.matches.matches_dict['league'].append(league)
            self.matches.matches_dict['pt1'].append(home_teams[ind].text)
            self.matches.matches_dict['pt2'].append(away_teams[ind].text)

        self.matches.matches_df = pd.DataFrame(self.matches.matches_dict)

    def get_date(self, times, years, ind):
        first_year = years.split('/')[0]
        second_year = years.split('/')[1]
        day_month = times[ind].text.split(' ', 1)[0]
        month = day_month.split('.')[1]
        if int(month) >= 7:
            return f"{day_month}{first_year}"
        else:
            return f"{day_month}{second_year}"