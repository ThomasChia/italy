import config
from loaders.gsheets.writer import GsheetsWriter
from loaders.loader import DBConnector
from loaders.query import Query
import logging
from matches.matches import PastMatches, FullSeasonMatches
from model.model import Model
from planners.planner import Planner
from post_processing.post_processor import FullSeasonPostProcessor
from preprocessing.adjustor import ManualAdjustor
from preprocessing.builder.builder import Builder
from preprocessing.builder.future_builder import FutureBuilder
from preprocessing.cleaners.cleaner import Cleaner
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
from preprocessing.validators.validate_matches import ValidateMatches
import pandas as pd
from scrapers.builders import SeasonBuilder
from simulations.monte_carlo_simulator import MonteCarloSimulator, MonteCarloResults
import time
pd.options.mode.chained_assignment = None

logger = logging.getLogger(__name__)

class FullSeasonPlanner(Planner):
    def run(self, debug=False):
        """
        Run the full-season planner.
        """
        logger.info("Running full-season planner.")

        logger.info("Loading data.")
        query = Query()
        query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES, config.COUNTRIES)
        loader = DBConnector()
        loader.run_query(query)
        if debug:
            loader.data = loader.data[loader.data['date']>='2021-08-01']

        logger.info("Building full season.")
        season_builder = SeasonBuilder(config.LEAGUE_TEAMS_MAPPING)
        season_builder.get_all_matches()
        future_matches = FullSeasonMatches(season_builder.matches)
        future_matches.clean()

        logger.info("Cleaning data.")
        cleaner = Cleaner(loader)
        cleaner.clean()

        logger.info("Validating the number of matches in each league.")
        validator = ValidateMatches(past_matches = cleaner.data, future_matches = future_matches.matches_df, season_start=config.SEASON_START, season_end=config.SEASON_END)
        validator.run()

        logger.info("Storing past matches.")
        past_matches = PastMatches(cleaner.data)

        # TODO remove duplicates at each stage of the data pipeline. Can add in match_id to help this, as can always just remove duplicates with the same match_id.
        logger.info("Calculating elo statistics.")
        elos = EloPreprocessor(cleaner.data)
        elos.calculate_elos()

        logger.info("Calculating goals statistics.")
        goals = GoalsPreprocessor(cleaner.data)
        goals.calculate_goals_statistics()

        logger.info("Building training set.")
        builder = Builder([elos, goals])
        builder.build_dataset()

        logger.info("Building prediction set.")
        future_builder = FutureBuilder(future_matches.matches_df, builder)
        future_builder.build_future_matches()

        logger.info("Manual adjustments.")
        adjustor = ManualAdjustor()
        future_builder.preprocessed_future_matches = adjustor.run(future_builder.preprocessed_future_matches)

        logger.info("Training model.")
        model = Model(builder.data)
        model.train()

        logger.info(f"Predicting {future_builder.preprocessed_future_matches.shape[0]} matches.") # TODO add in number of matches being predicted.
        future_home_and_away_matches, future_team_and_opponent = model.predict(future_builder.preprocessed_future_matches, config.FEATURES, config.ID_FEATURES)
        # TODO add in something to tell which league we are looking at.

        if debug:
            config.NUM_SIMULATIONS = 1000
        logger.info(f"Running {config.NUM_SIMULATIONS} simulations.")
        simulator = MonteCarloSimulator(future_home_and_away_matches)
        simulation_results = simulator.run_simulations(num_simulations=config.NUM_SIMULATIONS)

        logger.info("Creating output.")
        results = MonteCarloResults(simulation_results=simulation_results, season_start=config.SEASON_START)
        results.get_finishing_positions()
        # TODO update league targets output to ds_data; add in elos to team and opponent, home, rest days, goals; 538 scraper; opponent analysis

        logger.info("Processing output for gsheets.")
        post_processor = FullSeasonPostProcessor(league_targets=results.league_targets,
                                                 future_predictions=future_team_and_opponent,
                                                 match_importance=results.match_importance,
                                                 finishing_positions=results.finishing_positions,
                                                 elo_tracker=elos.elo.elo_tracker.tracker,
                                                 elo_over_time=elos.preprocessed_matches
                                                 )
        post_processor.run()
        
        
        if not debug:
            logger.info("Uploading to gsheets.")
            gsheets_writer = GsheetsWriter(data=[post_processor.league_targets,
                                                post_processor.future_predictions,
                                                post_processor.match_importance,
                                                post_processor.finishing_positions
                                                ])
            gsheets_writer.write_all_to_gsheets()
            gsheets_writer = GsheetsWriter(data=[post_processor.elo_tracker,
                                                post_processor.elo_over_time
                                                ],
                                            elos=True)
            gsheets_writer.write_all_to_gsheets()

        logger.info("Finished full-season planner.")