import bs4 as bs
from collections import defaultdict
import logging
from matches.matches import Matches
import pandas as pd 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
            logging.info(f"Getting matches for {league} in {self.matches.country}")
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
        if self.check_if_matches_exist():
            times, years, home_teams, away_teams = self.get_fixture_elements()
            self.store_future_matches(times, years, home_teams, away_teams, league)
        else:
            logging.warning(f"No matches found for {league} in {self.matches.country}")
            self.matches.matches_df = pd.DataFrame(columns=['date', 'league', 'pt1', 'pt2'])

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
        
    def check_if_matches_exist(self):
        try:
            no_matches = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[1]/div/div/main/div[4]/div[2]/div[1]/div[1]/div')
            return False
        except NoSuchElementException:
            return True
        

class FiveThirtyEightScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.base_url = f'https://github.com/fivethirtyeight/data/tree/master/soccer-spi'
        self.matches = None

    def run(self):
        webpage = self.get_page(self.base_url)
        href_list = self.get_href_list(webpage)
        self.read_latest_matches_link(href_list)

    def get_page(self, site):
        driver = webdriver.Chrome(self.PATH)
        driver.get(site)
        webpage = bs.BeautifulSoup(driver.page_source, features='html.parser')
        driver.quit()
        return webpage


    def get_href_list(self, webpage):
        href_list = []
        table = webpage.find('table')
        rows = table.find_all('td')
        for row in rows:
            a = row.find('a')
            link = a['href']
            href_list.append(link)
        return href_list


    def read_latest_matches_link(self, links_list):
        latest_matches_link = [s for s in links_list if 'matches_latest' in s]
        self.matches = pd.read_csv(latest_matches_link[0])


if __name__ == '__main__':
    scraper = FiveThirtyEightScraper()
    webpage = scraper.get_page(scraper.base_url)
    href_list = scraper.get_href_list(webpage)
    scraper.read_links(href_list)