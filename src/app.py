import code
import config
from preprocessing.cleaners.cleaner import Cleaner
from loaders.query import Query
from loaders.loader import DBLoader
from preprocessing.preprocessors import EloPreprocessor



if __name__ == "__main__":
    query = Query()
    query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES)
    loader = DBLoader()
    loader.run_query(query)
    print(loader.data)

    cleaner = 

    elos = EloPreprocessor(loader.data)
    elos.calculate_elos()

    code.interact(local=locals())

    
