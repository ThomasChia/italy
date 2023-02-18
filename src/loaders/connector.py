import config
import os
from sqlalchemy import create_engine


class Connector:
    def __init__(self) -> None:
        pass

    def get_connection():
        if "API_DB_USER" in os.environ:
            user = os.getenv("API_DB_USER")
            password = os.getenv("API_DB_PASSWORD")
            host = os.getenv("API_DB_HOST")
            port = os.getenv("API_DB_PORT")
            database = os.getenv("API_DB_DB")
        else:
            raise EnvironmentError("No Env Vars Supplied to Access DB")

        connection_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        return create_engine(
            connection_str, pool_pre_ping=True, pool_recycle=600
        )