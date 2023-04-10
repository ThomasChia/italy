import code
import config
from preprocessing.cleaners.cleaner import Cleaner
from loaders.query import Query
from loaders.loader import DBLoader
import logging
from preprocessing.builder.builder import Builder
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logging.info("Loading data.")
    query = Query()
    query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES)
    loader = DBLoader()
    loader.run_query(query)
    loader.data = loader.data.iloc[:5000, :]

    logging.info("Cleaning data.")
    cleaner = Cleaner(loader)
    cleaner.clean()

    logging.info("Calculating elo statistics.")
    elos = EloPreprocessor(cleaner.data)
    elos.calculate_elos()

    logging.info("Calculating goals statistics.")
    goals = GoalsPreprocessor(cleaner.data)
    goals.calculate_goals_statistics()

    logging.info("Building training set.")
    builder = Builder([elos, goals])
    builder.build_dataset()
    # TODO properly merge the preprocessed matches from elos and goals, and make flexible for any number of preprocesor objects.
    # elos.merge_on_common_columns()

    code.interact(local=locals())