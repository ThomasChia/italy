import asyncio
import code
from config import SCRAPED_LEAGUES_MAPPING
import pandas as pd
import numpy as np
from matches.matches import Matches, EnglishMatches, ItalianMatches, ScottishMatches
from multiprocessing import Process, Queue
from scrapers.scrapers import FlashScoreScraper
# from scrapers import FlashScoreScraper

# class MatchScraperFactory:
#     @staticmethod
#     def create_scraper(countries):
#         matches = Matches([])
#         for country in countries:
#             if country == "England":
#                 matches.add_league(EnglishMatches())
#             elif country == "Italy":
#                 matches.add_league(ItalianMatches())
#             # add more countries as necessary
#         return FlashScoreScraper(matches)

class ScraperFactory:
    @staticmethod
    def from_matches_list(matches_list):
        scraper_list = []
        for matches in matches_list:
            scraper_list.append(FlashScoreScraper(matches))
        return scraper_list

class MultiScraper:
    def __init__(self, countries):
        self.scraped_matches = pd.DataFrame()
        self.matches_list = []
        for country in countries:
            if country == 'England':
                self.matches_list.append(EnglishMatches())
            elif country == 'Italy':
                self.matches_list.append(ItalianMatches())
            if country == 'Scotland':
                self.matches_list.append(ScottishMatches())
            # Add more countries as necessary
        
    def scrape_all(self):
        scraper_list = ScraperFactory.from_matches_list(self.matches_list)
        q = Queue()
        processes = [Process(target=self.scrape_all_country, args=(q, scraper,)) for scraper in scraper_list]
        returns = []
        for process in processes:
            process.start()
        for process in processes:
            returns.append(q.get())
        for process in processes:
            process.join()

        self.scraped_matches = pd.concat(returns)

        self.clean_team_names()
        self.add_match_id()

    def scrape_all_country(self, queue: Queue, scraper: FlashScoreScraper):
        scraper.get_matches()
        scraper.matches.clean_future_matches()
        queue.put(scraper.matches.matches_df)

    def clean_team_names(self):
        self.scraped_matches['league'] = self.scraped_matches['league'].replace(SCRAPED_LEAGUES_MAPPING)

    def add_match_id(self):
        self.scraped_matches['match_id'] = self.scraped_matches['pt1'] + '_' + self.scraped_matches['pt2'] + '_' + self.scraped_matches['date'].astype(str).str.replace('.', '-', regex=False)


if __name__=="__main__":
    countries = ['England', 'Italy']
    scraper = MultiScraper(countries)

    code.interact(local=locals())