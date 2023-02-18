import pandas as pd
from sqlalchemy.engine import Engine


class Loader:
    def __init__(self,):
        pass


class DBLoader(Loader):
    def __init__(self, connection: Engine):
        super().__init__()
        self.connection = connection

    def run_query(self, query: str):
        engine = self.connection.get_connection()
        data = pd.read_sql_query(query, engine)

        return data
