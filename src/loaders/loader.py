import pandas as pd
from loaders.connector import Connector
from loaders.query import Query
from sqlalchemy.engine import Engine


class Loader:
    def __init__(self,):
        self.data: pd.DataFrame = None


class DBLoader(Loader):
    def __init__(self):
        super().__init__()
        self.connection = Connector()

    def run_query(self, query: Query()):
        engine = self.connection.get_connection()
        self.data = pd.read_sql_query(query.query, engine)
