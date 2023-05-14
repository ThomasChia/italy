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