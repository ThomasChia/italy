from copy import deepcopy
import config
from loaders.query import Query
from loaders.loader import DBLoader
import logging
from matches.matches import ItalianMatches, EnglishMatches, PastMatches
from model.model import Model
from planners.planner import Planner
from post_processing.post_processor import InSeasonPostProcessor
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
        loader = DBLoader()
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

        logging.info("Running simulations.")
        # simulator = MonteCarloSimulator(future_home_and_away_matches)
        # simulation_results = simulator.run_simulations(num_simulations=config.NUM_SIMULATIONS)

        # logging.info("Creating output.")
        # results = MonteCarloResults(simulation_results=simulation_results, past_results=deepcopy(past_matches), season_start=config.SEASON_START)
        # results.get_finishing_positions()

        logging.info("Saving past and future predictions to db.")
        # post_processor = ResetProcessor(league_targets=results.league_targets,
        #                                        results=past_matches,
        #                                        past_predictions=pd.DataFrame(),
        #                                        future_predictions=future_team_and_opponent,
        #                                        match_importance=results.match_importance,
        #                                        finishing_positions=results.finishing_positions,
        #                                        opponent_analysis=pd.DataFrame())
        # post_processor.run()
        # TODO upload output to gsheets.