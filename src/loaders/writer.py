import pandas as pd
from loaders.connector import Connector
from loaders.query import Query, SaveQuery
import logging
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


class Writer:
    def __init__(self,):
        self.data: pd.DataFrame = pd.DataFrame()

class DBWriter(Writer):
    def __init__(self):
        super().__init__()
        self.connection = Connector()

    def run_update_query(self, data: pd.DataFrame):
        logging.info(f"Writing {data.shape[0]} rows to past predictions table.")
        engine = self.connection.get_connection()
        data.to_sql('football_dashboard_past_predictions', engine, if_exists='append', index=False)