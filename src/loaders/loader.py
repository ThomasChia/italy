import pandas as pd
from loaders.connector import Connector
from loaders.query import Query, SaveQuery
import logging
from sqlalchemy.engine import Engine


class Loader:
    def __init__(self,):
        self.data: pd.DataFrame = pd.DataFrame()

class DBConnector(Loader):
    def __init__(self):
        super().__init__()
        self.connection = Connector()

    def run_query(self, query: Query):
        logging.info("Reading data from DB.")
        engine = self.connection.get_connection()
        self.data = pd.read_sql_query(query.query, engine)

    def run_save_query(self, query: SaveQuery, data: pd.DataFrame):
        logging.info("Writing data from DB.")
        engine = self.connection.get_connection()
        pd.read_sql_query(query.create_query, engine)
        data.to_sql(query.table_name, engine, if_exists='replace', index=False)

