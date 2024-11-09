from abc import ABC, abstractmethod

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session


class I_DatabaseManager(ABC):
    @property
    @abstractmethod
    def engine(self) -> Engine:
        pass

    @property
    @abstractmethod
    def session(self) -> Session:
        pass
