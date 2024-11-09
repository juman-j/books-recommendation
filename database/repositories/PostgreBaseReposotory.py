from abc import ABC, abstractmethod

from loguru import logger
from sqlalchemy import Inspector, inspect
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from database.connections.PostgreDatabaseManager import postgre_manager


class PostgreBaseReposotory(ABC):

    def __init__(self) -> None:
        if not hasattr(self, "table"):
            raise ValueError("The child class must define table")
        self._engine: Engine = postgre_manager.engine
        self.session: Session = postgre_manager.session()
        self._inspector: Inspector = inspect(self._engine)

        self.setup()

    @property
    @abstractmethod
    def table(self):
        pass

    def __is_table_exist(self) -> bool:
        tables = self._inspector.get_table_names()
        table_name = self.table.__table__.name
        if table_name in tables:
            return True
        logger.debug(f"Table '{table_name}' does not exist in the database.")
        return False

    def __validate_table_schema(self) -> None:
        db_columns = self._inspector.get_columns(self.table.__tablename__)
        db_column_names = {col["name"] for col in db_columns}
        model_column_names = {col.name for col in self.table.__table__.columns}

        assert (
            db_column_names == model_column_names
        ), f"Model and schema in the database do not match. Table: '{self.table.__tablename__}'"

    def __create_table(self) -> None:
        self.table.__table__.create(self._engine)
        logger.debug(f"Table '{self.table.__table__.name}' has been created.")

    def _drop_table(self) -> None:
        try:
            self.table.__table__.drop(self._engine)
            logger.debug(f"Table '{self.table.__table__.name}' has been droped.")
        except ProgrammingError:
            logger.debug(f"Table '{self.table.__table__.name}' doesn't exist.")

    def setup(self) -> None:
        if self.__is_table_exist():
            self.__validate_table_schema()
        else:
            self.__create_table()
