import code
import config
from preprocessing.cleaners.cleaner import Cleaner
from loaders.query import Query
from loaders.loader import DBLoader
import logging
from preprocessing.preprocessors import EloPreprocessor
from preprocessing.preprocessors import GoalsPreprocessor



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Loading data.")
    query = Query()
    query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES)
    loader = DBLoader()
    loader.run_query(query)
    print(loader.data)

    cleaner = Cleaner(loader)
    loader = cleaner.get_result()

    # logging.info("Calculating elo statistics.")
    # elos = EloPreprocessor(loader.data)
    # elos.calculate_elos()

    logging.info("Calculating goals statistics.")
    goals = GoalsPreprocessor(loader.data)
    goals.calculate_goals_statistics()

    code.interact(local=locals())