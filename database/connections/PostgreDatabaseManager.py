from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, sessionmaker

from configurations.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from database.connections.I_DatabaseManager import I_DatabaseManager


class PostgreDatabaseManager(I_DatabaseManager):
    _connection_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"
    )

    def __init__(
        self,
        connection_string: str = _connection_string,
        echo: bool = False,
        autocommit: bool = False,
        autoflush: bool = False,
    ) -> None:
        self._engine = create_engine(url=connection_string, echo=echo)
        self._Session = sessionmaker(
            bind=self._engine, autocommit=autocommit, autoflush=autoflush
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session(self) -> Session:
        return self._Session


postgre_manager = PostgreDatabaseManager()
