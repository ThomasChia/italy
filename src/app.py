import argparse
import code
import config
from loaders.query import Query
from loaders.loader import DBLoader
import logging
from matches.matches import ItalianMatches, EnglishMatches, PastMatches
from model.model import Model
import pandas as pd
from planners.planner_factory import PlannerFactory
from preprocessing.builder.builder import Builder
from preprocessing.builder.future_builder import FutureBuilder
from preprocessing.cleaners.cleaner import Cleaner
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
from scrapers.scraper_factory import MultiScraper
from scrapers.scrapers import FlashScoreScraper
from simulations.monte_carlo_simulator import MonteCarloSimulator, MonteCarloResults
import time
pd.options.mode.chained_assignment = None # default='warn'



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    start_time = time.time()

    parser = argparse.ArgumentParser(
        prog='football_prediction',
        description='Run the football prediction model.'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='Run in debug mode.')
    parser.add_argument('-p', '--plan', type=str, help='Run a specific plan.')

    print("""
     ______          _   _           _ _ _  _    _____          _   
    |  ____|        | | | |         | | | || |  / ____|        | |  
    | |__ ___   ___ | |_| |__   __ _| | | || |_| |     __ _ ___| |_ 
    |  __/ _ \ / _ \| __| '_ \ / _` | | |__   _| |    / _` / __| __|
    | | | (_) | (_) | |_| |_) | (_| | | |  | | | |___| (_| \__ \ |_ 
    |_|  \___/ \___/ \__|_.__/ \__,_|_|_|  |_|  \_____\__,_|___/\__|
                                                                                                                                                                                                                                                                                           
    """)

    if parser.parse_args().debug:
        logging.info("Running in debug mode.")
        DEBUG = True
    else:
        DEBUG = False
    planner_factory = PlannerFactory()
    planner = planner_factory.get_planner(parser.parse_args().plan)
    planner.run(debug=DEBUG)


    # logging.info("Loading data.")
    # query = Query()
    # query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES, config.COUNTRIES)
    # loader = DBLoader()
    # loader.run_query(query)
    # if parser.parse_args().debug:
    #     loader.data = loader.data[loader.data['date']>='2019-08-01']

    # logging.info("Scraping future matches.")
    # future_matches = MultiScraper(config.COUNTRIES)
    # future_matches.scrape_all()

    # logging.info("Cleaning data.")
    # cleaner = Cleaner(loader)
    # cleaner.clean()

    # logging.info("Storing past matches.")
    # past_matches = PastMatches(cleaner.data)

    # # TODO remove duplicates at each stage of the data pipeline. Can add in match_id to help this, as can always just remove duplicates with the same match_id.
    # logging.info("Calculating elo statistics.")
    # elos = EloPreprocessor(cleaner.data)
    # elos.calculate_elos()

    # logging.info("Calculating goals statistics.")
    # goals = GoalsPreprocessor(cleaner.data)
    # goals.calculate_goals_statistics()

    # logging.info("Building training set.")
    # builder = Builder([elos, goals], future_matches.scraped_matches)
    # builder.build_dataset()

    # logging.info("Building prediction set.")
    # future_builder = FutureBuilder(future_matches.scraped_matches, builder)
    # future_builder.build_future_matches()

    # logging.info("Training model.")
    # model = Model(builder.data)
    # model.train()

    # logging.info("Predicting matches.") # TODO add in number of matches being predicted.
    # future_home_and_away_matches, future_team_and_opponent = model.predict(future_builder.preprocessed_future_matches, config.FEATURES, config.ID_FEATURES)
    # # TODO add in something to tell which league we are looking at.

    # logging.info("Running simulations.")
    # simulator = MonteCarloSimulator(future_home_and_away_matches)
    # simulation_results = simulator.run_simulations(num_simulations=config.NUM_SIMULATIONS)

    # logging.info("Creating output.")
    # results = MonteCarloResults(simulation_results=simulation_results, past_results=past_matches, season_start=config.SEASON_START)
    # results.get_finishing_positions()

    # # logging.info("Uploading output.")

    elapsed_time = time.time() - start_time
    logging.info(f"Programme completed in {elapsed_time:.2f} seconds.")
    code.interact(local=locals())