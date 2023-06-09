import argparse
import code
import config
from loaders.query import Query
from loaders.loader import DBConnector
import logging
from logs import setup_logs
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

setup_logs()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
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
        logger.info("Running in debug mode.")
        DEBUG = True
    else:
        DEBUG = False
    planner_factory = PlannerFactory()
    planner = planner_factory.get_planner(parser.parse_args().plan)
    planner.run(debug=DEBUG)

    elapsed_time = time.time() - start_time
    logger.info(f"Programme completed in {elapsed_time:.2f} seconds.")
    code.interact(local=locals())