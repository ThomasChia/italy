import config
from loaders.query import Query
from loaders.loader import DBLoader
import logging
from matches.matches import ItalianMatches, EnglishMatches, PastMatches
from model.model import Model
from planners.planner import Planner
from preprocessing.builder.builder import Builder
from preprocessing.builder.future_builder import FutureBuilder
from preprocessing.cleaners.cleaner import Cleaner
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
import pandas as pd
from simulations.monte_carlo_simulator import MonteCarloSimulator, MonteCarloResults
import time
pd.options.mode.chained_assignment


class FullSeasonPlanner(Planner):
    def run(self, debug=False):
        """
        Run the full-season planner.
        """
        print("Running full-season planner.")

        logging.info("Loading data.")
        query = Query()
        query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES, config.COUNTRIES)
        loader = DBLoader()
        loader.run_query(query)
        if debug:
            loader.data = loader.data[loader.data['date']>='2019-08-01']

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
        builder = Builder([elos, goals], future_matches.scraped_matches)
        builder.build_dataset()

        logging.info("Training model.")
        model = Model(builder.data)
        model.train()