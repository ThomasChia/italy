import pandas as pd
from loaders.connector import Connector
from loaders.query import Query, SaveQuery
import logging
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


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
        logging.info("Writing data to DB.")
        engine = self.connection.get_connection()
        session_made = sessionmaker(bind=engine)
        session = session_made()
        session.execute(text(query.create_query))
        session.commit()
        session.close()

        data.to_sql(query.table_name, engine, if_exists='append', index=False)

