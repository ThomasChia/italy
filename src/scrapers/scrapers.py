from collections import defaultdict
from matches.matches import Matches
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class Scraper:
    def __init__(self):
        self.PATH = '../../tools/chromedriver'
        self.driver = webdriver.Chrome(self.PATH)
        self.matches = None


class FlashScoreScraper(Scraper):
    def __init__(self, matches: Matches):
        super().__init__()
        self.base_url = f'https://www.flashscore.com/football/'
        self.matches = matches

    def get_matches(self):
        for league in self.matches.leagues:
            league_url = self.base_url + self.matches.country + '/' + league + '/fixtures/'
            self.driver.get(league_url)
            self.click_cookies()
            self.get_fixture_data()            

    def click_cookies(self):
        cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
        cookies.click()

    def get_fixture_data(self):
        times, home_teams, away_teams = self.get_fixture_elements()
        self.store_future_matches(times, home_teams, away_teams)

    def get_fixture_elements(self):
        body = self.driver.find_element(By.XPATH, '//*[@id="live-table"]/div[1]/div/div')
        times = body.find_elements(By.CSS_SELECTOR, "div.event__time")
        home_teams = body.find_elements(By.CSS_SELECTOR, "div.event__participant.event__participant--home")
        away_teams = body.find_elements(By.CSS_SELECTOR, "div.event__participant.event__participant--away")

        return times, home_teams, away_teams
    
    def store_future_matches(self, times, home_teams, away_teams):
        for ind in range(len(times)):
            self.matches.matches_dict['date'].append(times[ind].text)
            self.matches.matches_dict['pt1'].append(home_teams[ind].text)
            self.matches.matches_dict['pt2'].append(away_teams[ind].text)

        self.matches.matches_df = pd.DataFrame(self.matches.matches_dict)