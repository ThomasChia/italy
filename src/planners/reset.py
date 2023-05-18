from copy import deepcopy
import config
from loaders.query import Query, SaveQuery
from loaders.loader import DBConnector
import logging
from matches.matches import ItalianMatches, EnglishMatches, PastMatches
from model.model import Model
from planners.planner import Planner
from post_processing.post_processor import ResetPostProcessor
from preprocessing.builder.builder import Builder
from preprocessing.builder.future_builder import FutureBuilder
from preprocessing.cleaners.cleaner import Cleaner
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
import pandas as pd
from scrapers.scraper_factory import MultiScraper
from scrapers.scrapers import FiveThirtyEightScraper 
from simulations.monte_carlo_simulator import MonteCarloSimulator, MonteCarloResults
import time
pd.options.mode.chained_assignment = None


class ResetPlanner(Planner):
    """
    Class for reset planner factory.
    This is to reset all of the statistics and predictions that are calculated and stored in the database.
    """

    def run(self, debug=False):
        """
        Run the in-season planner.
        """
        logging.warning("Running RESET planner.")

        confirmation = input("Are you sure you want to run this script? (y/n) ")
        if confirmation.lower() != 'y':
            logging.info("Script execution cancelled.")
            return
        else:
            logging.info("RESET planner is now running.")

        logging.info("Loading data.")
        query = Query()
        query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES, config.COUNTRIES)
        loader = DBConnector()
        loader.run_query(query)
        if debug:
            loader.data = loader.data[loader.data['date']>='2021-08-01']

        logging.info("Scraping future matches.")
        future_matches = MultiScraper(config.COUNTRIES)
        future_matches.scrape_all()

        logging.info("Scraping 538 predictions.")
        scraper = FiveThirtyEightScraper()
        scraper.run()

        logging.info("Cleaning data.")
        cleaner = Cleaner(loader)
        cleaner.clean()

        logging.info("Storing past matches.")
        past_matches = PastMatches(cleaner.data)

        # TODO remove duplicates at each stage of the data pipeline. Can add in match_id to help this, as can always just remove duplicates with the same match_id.
        logging.info("Calculating elo statistics.")
        elos = EloPreprocessor(cleaner.data)
        elos.calculate_elos()

        logging.info("Calculating goals statistics.")
        goals = GoalsPreprocessor(cleaner.data)
        goals.calculate_goals_statistics()

        logging.info("Building training set.")
        builder = Builder([elos, goals])
        builder.build_dataset()

        logging.info("Building prediction set.")
        future_builder = FutureBuilder(future_matches.scraped_matches, builder)
        future_builder.build_future_matches()

        logging.info("Training model.")
        model = Model(builder.data)
        model.train()

        logging.info(f"Predicting {builder.data.shape[0]} past matches and {future_builder.preprocessed_future_matches.shape[0]} future matches.") # TODO add in number of matches being predicted.
        past_home_and_away_matches, past_team_and_opponent = model.predict(builder.data, config.FEATURES, config.ID_FEATURES)
        future_home_and_away_matches, future_team_and_opponent = model.predict(future_builder.preprocessed_future_matches, config.FEATURES, config.ID_FEATURES)

        logging.info("Running postprocessor.")
        post_processor = ResetPostProcessor(results=past_matches,
                                            past_predictions=past_team_and_opponent,
                                            future_predictions=future_team_and_opponent)
        post_processor.run()
        
        logging.info("Saving past and future predictions to db.")
        past_predictions_query = SaveQuery('football_dashboard_past_predictions')
        past_predictions_query.get_past_predictions_query()
        past_predictions_writer = DBConnector()
        past_predictions_writer.run_save_query(past_predictions_query, post_processor.past_predictions)

        future_predictions_query = SaveQuery('football_dashboard_future_predictions')
        future_predictions_query.get_future_predictions_query()
        future_predictions_writer = DBConnector()
        future_predictions_writer.run_save_query(future_predictions_query, post_processor.future_predictions)

        logging.info("Past and future predictions have been reset.")
