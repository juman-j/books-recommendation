from abc import ABC, abstractmethod

from esdbclient.client import AbstractCatchupSubscription


class I_EventStoreProveder(ABC):

    @classmethod
    @abstractmethod
    def update_current_stream_position(cls, new_stream_position: int) -> None:
        pass

    @classmethod
    @abstractmethod
    def add_stream_position(
        cls,
        checkpoint_stream: str,
    ) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_subscription(
        cls, command_stream: str, checkpoint_stream: str
    ) -> AbstractCatchupSubscription | None:
        pass
