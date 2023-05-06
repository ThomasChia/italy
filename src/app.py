import code
import config
from loaders.query import Query
from loaders.loader import DBLoader
import logging
from matches.matches import ItalianMatches, EnglishMatches
from model.model import Model
from preprocessing.builder.builder import Builder
from preprocessing.cleaners.cleaner import Cleaner
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
import pandas as pd
from scrapers.scrapers import FlashScoreScraper
import time
pd.options.mode.chained_assignment = None  # default='warn'



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    start_time = time.time()

    logging.info("Loading data.")
    query = Query()
    query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES)
    loader = DBLoader()
    loader.run_query(query)
    loader.data = loader.data.iloc[:5000, :]

    logging.info("Cleaning data.")
    cleaner = Cleaner(loader)
    cleaner.clean()

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

    logging.info("Training model.")
    model = Model(builder.data)
    model.train()

    logging.info("Predicting matches.") # TODO add in number of matches being predicted.
    future_matches = FlashScoreScraper(ItalianMatches)
    future_matches.get_matches()
    future_matches.matches.clean_future_matches()
    predictions, probabilities = model.predict(future_matches.matches.matches_df, config.FEATURES - config.ID_FEATURES)

    # logging.info("Running simulations.")

    # logging.info("Creating output.")

    # logging.info("Uploading output.")

    elapsed_time = time.time() - start_time
    logging.info(f"Programme completed in {elapsed_time:.2f} seconds.")
    code.interact(local=locals())