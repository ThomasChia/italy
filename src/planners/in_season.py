from copy import deepcopy
import config
from loaders.gsheets.writer import GsheetsWriter
from loaders.query import Query, SaveQuery
from loaders.loader import DBConnector
import logging
from logs import setup_logs
from matches.matches import ItalianMatches, EnglishMatches, PastMatches
from model.model import Model
import multiprocessing
from planners.planner import Planner
from post_processing.post_processor import InSeasonPostProcessor
from post_processing.past_predictions_processor import PastPredictionsProcessor
from preprocessing.adjustor import ManualAdjustor
from preprocessing.builder.builder import Builder
from preprocessing.builder.future_builder import FutureBuilder
from preprocessing.cleaners.cleaner import Cleaner
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
from preprocessing.validators.validate_matches import ValidateMatches
import pandas as pd
from scrapers.scraper_factory import MultiScraper
from scrapers.scrapers import FiveThirtyEightScraper 
from simulations.monte_carlo_simulator import MonteCarloSimulator, MonteCarloResults
import time
pd.options.mode.chained_assignment = None

setup_logs()
logger = logging.getLogger(__name__)

class InSeasonPlanner(Planner):
    """
    Concrete class for in-season planner factory.
    This represents a combination of steps for outputting different types of plans.
    """

    def run(self, debug=False):
        """
        Run the in-season planner.
        """
        logger.info("Running in-season planner.")

        logger.info("Loading data.")
        query = Query()
        query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES, config.COUNTRIES)
        loader = DBConnector()
        loader.run_query(query)
        if debug:
            loader.data = loader.data[loader.data['date']>='2021-08-01']

        logger.info("Scraping future matches.")
        future_matches = MultiScraper(config.COUNTRIES)
        future_matches.scrape_all()

        logger.info("Scraping 538 predictions.")
        scraper = FiveThirtyEightScraper()
        scraper.run()

        logger.info("Cleaning data.")
        cleaner = Cleaner(loader)
        cleaner.clean()

        logger.info("Validating the number of matches in each league.")
        validator = ValidateMatches(past_matches=cleaner.data,
                                    future_matches=future_matches.scraped_matches,
                                    season_start=config.SEASON_START,
                                    season_end=config.SEASON_END)
        validator.run()

        logger.info("Storing past matches.")
        past_matches = PastMatches(cleaner.data)

        queue = multiprocessing.Queue()

        # TODO remove duplicates at each stage of the data pipeline. Can add in match_id to help this, as can always just remove duplicates with the same match_id.
        logger.info("Calculating elo statistics.")
        elos = EloPreprocessor(cleaner.data)
        elos_process = multiprocessing.Process(target=elos.calculate_elos, args=(queue, ))
        elos_process.start()
        # elos.calculate_elos()

        logger.info("Calculating goals statistics.")
        goals = GoalsPreprocessor(cleaner.data)
        goals_process = multiprocessing.Process(target=goals.calculate_goals_statistics, args=(queue, ))
        goals_process.start()
        # goals.calculate_goals_statistics()

        result_a = queue.get()
        result_b = queue.get()

        if isinstance(result_a, tuple):
            elos_tuple = result_a
            goals_data = result_b
        else:
            elos_tuple = result_b
            goals_data = result_a

        elos_process.join()
        goals_process.join()

        logger.info("Building training set.")
        elos_data, elo_tracker = elos_tuple
        builder = Builder([elos_data, goals_data])
        builder.build_dataset()

        logger.info("Building prediction set.")
        future_builder = FutureBuilder(validator.future_matches, builder)
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
            config.NUM_SIMULATIONS = 100
        logger.info(f"Running {config.NUM_SIMULATIONS} simulations.")
        simulator = MonteCarloSimulator(future_home_and_away_matches)
        simulation_results = simulator.run_simulations(num_simulations=config.NUM_SIMULATIONS)

        logger.info("Creating output.")
        results = MonteCarloResults(simulation_results=simulation_results, past_results=deepcopy(past_matches), season_start=config.SEASON_START)
        results.get_finishing_positions()

        logger.info("Reading past predictions from db.")
        query = Query()
        query.read_last_future_predictions()
        loader = DBConnector()
        loader.run_query(query)

        logger.info("Updating past predictions.")
        past_prediction_processor = PastPredictionsProcessor(past_predictions=loader.data, future_predictions=future_team_and_opponent)

        logger.info("Postprocessing output for gsheets.")
        post_processor = InSeasonPostProcessor(league_targets=results.league_targets,
                                               results=past_matches,
                                               past_predictions=past_prediction_processor.latest_past_predictions,
                                               future_predictions=future_team_and_opponent,
                                               match_importance=results.match_importance,
                                               finishing_positions=results.finishing_positions,
                                               opponent_analysis=pd.DataFrame(),
                                               elo_tracker=elo_tracker,
                                               elo_over_time=elos_data)
        post_processor.run()
        
        if not debug:
            # logger.info("Adding latest past predictions to db.")

            # logger.info("Uploading future predictions to db.")

            logger.info("Uploading to gsheets.")
            gsheets_writer = GsheetsWriter(data=[post_processor.league_targets,
                                                post_processor.future_predictions,
                                                post_processor.match_importance,
                                                post_processor.finishing_positions,
                                                post_processor.results,
                                                post_processor.past_predictions
                                                ])
            gsheets_writer.write_all_to_gsheets()
            gsheets_writer = GsheetsWriter(data=[post_processor.elo_tracker,
                                                post_processor.elo_over_time
                                                ],
                                            elos=True)
            gsheets_writer.write_all_to_gsheets()

        logging.info("Saving past and future predictions to db.")
        past_predictions_query = SaveQuery('football_dashboard_past_predictions')
        past_predictions_query.get_past_predictions_query()
        past_predictions_writer = DBConnector()
        if not debug:
            past_predictions_writer.run_save_query(past_predictions_query, post_processor.past_predictions)

        future_predictions_query = SaveQuery('football_dashboard_future_predictions')
        future_predictions_query.get_future_predictions_query()
        future_predictions_writer = DBConnector()
        if not debug:
            future_predictions_writer.run_save_query(future_predictions_query, post_processor.future_predictions)
        

        logger.info("In-season planner complete.")