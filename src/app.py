import config
from loaders.query import Query
from loaders.loader import DBLoader



if __name__ == "__main__":
    query = Query()
    query.leagues_specific(config.TABLE_NAME_PAST, config.LEAGUES)
    loader = DBLoader()
    loader.run_query(query)
    print(loader.data.head())

    
