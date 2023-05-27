import config
from loaders.query import Query
from loaders.loader import DBConnector
import logging
from matches.config import LEAGUE_TEAMS_MAPPING
from matches.matches import PastMatches, FullSeasonMatches
from model.model import Model
from planners.planner import Planner
from preprocessing.builder.builder import Builder
from preprocessing.builder.future_builder import FutureBuilder
from preprocessing.cleaners.cleaner import Cleaner
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
import pandas as pd
from scrapers.builders import SeasonBuilder
from simulations.monte_carlo_simulator import MonteCarloSimulator, MonteCarloResults
import time
pd.options.mode.chained_assignment = None


class FullSeasonPlanner(Planner):
    def run(self, debug=False):
        """
        Run the full-season planner.
        """
        logging.info("Running full-season planner.")

        logging.info("Loading data.")
        query = Query()
        query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES, config.COUNTRIES)
        loader = DBConnector()
        loader.run_query(query)
        if debug:
            loader.data = loader.data[loader.data['date']>='2021-08-01']

        logging.info("Building full season.")
        season_builder = SeasonBuilder(LEAGUE_TEAMS_MAPPING)
        season_builder.get_all_matches()
        future_matches = FullSeasonMatches(season_builder.matches)
        future_matches.clean()

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
        future_builder = FutureBuilder(future_matches.matches_df, builder)
        future_builder.build_future_matches()

        logging.info("Training model.")
        model = Model(builder.data)
        model.train()

        logging.info(f"Predicting {future_builder.preprocessed_future_matches.shape[0]} matches.") # TODO add in number of matches being predicted.
        future_home_and_away_matches, future_team_and_opponent = model.predict(future_builder.preprocessed_future_matches, config.FEATURES, config.ID_FEATURES)
        # TODO add in something to tell which league we are looking at.

        logging.info("Running simulations.")
        simulator = MonteCarloSimulator(future_home_and_away_matches)
        simulation_results = simulator.run_simulations(num_simulations=config.NUM_SIMULATIONS)

        logging.info("Creating output.")
        results = MonteCarloResults(simulation_results=simulation_results, season_start=config.SEASON_START)
        results.get_finishing_positions()
        # TODO update league targets output to ds_data; add in elos to team and opponent, home, rest days, goals; 538 scraper; opponent analysis

        logging.info("Uploading to gsheets.")
        

        logging.info("Finished full-season planner.")