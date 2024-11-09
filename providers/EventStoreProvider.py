import re

from esdbclient import NewEvent, ReadResponse, StreamState
from esdbclient.client import AbstractCatchupSubscription
from esdbclient.exceptions import NotFound
from loguru import logger

from configurations.config import CHECKPOINT_STREAM_EVENT_TYPE
from helpers.exceptions import ValueNotFoundError
from providers.clients.EventStoreClient import EventStoreClient
from providers.interfaces.I_EventStoreProveder import I_EventStoreProveder


class EventStoreProvider(I_EventStoreProveder):
    client = EventStoreClient.get_client(local_client=True)
    current_stream_position: int

    @classmethod
    def update_current_stream_position(cls, new_stream_position: int) -> None:
        cls.current_stream_position = new_stream_position

    @classmethod
    def __try_to_read(cls, command_stream: str = None, checkpoint_stream: str = None):
        read_response = None
        if command_stream:
            read_response = cls.client.read_stream(stream_name=command_stream)
        elif checkpoint_stream:
            read_response = cls.client.read_stream(stream_name=checkpoint_stream)
        assert read_response is not None, "'read_response' cant be None."

        try:
            recorded_event = tuple(read_response)
            return recorded_event
        except NotFound:
            return None

    @classmethod
    def __add_stream(cls, checkpoint_stream: str):
        event = NewEvent(
            type=CHECKPOINT_STREAM_EVENT_TYPE,
            data=b'{"stream_position": 0}',
        )

        cls.client.append_to_stream(
            stream_name=checkpoint_stream,
            current_version=StreamState.NO_STREAM,
            events=[event],
        )

        logger.info(f'Stream "{checkpoint_stream}" added.')

    @staticmethod
    def __parse_start_position(recorded_event: tuple[ReadResponse]):
        data: bytes = recorded_event[-1].data
        decoded_data = data.decode("utf-8")
        match = re.search(r'"stream_position":\s*(\d+)', decoded_data)

        if match:
            start_stream_position = int(match.group(1))
            assert isinstance(start_stream_position, int)
            return start_stream_position
        else:
            logger.error("Stream position in the data was not found.")
            raise ValueNotFoundError("Stream position in the data was not found.")

    @classmethod
    def __get_start_position(cls, checkpoint_stream: str) -> None:
        response = cls.__try_to_read(checkpoint_stream=checkpoint_stream)
        if response:
            cls.current_stream_position = cls.__parse_start_position(
                recorded_event=response
            )
            logger.debug(f"start_position = {cls.current_stream_position}")
        else:
            cls.__add_stream(checkpoint_stream=checkpoint_stream)
            cls.current_stream_position = 0

    @classmethod
    def add_stream_position(cls, checkpoint_stream: str) -> None:
        data_string = '{"stream_position": ' + str(cls.current_stream_position) + "}"
        data_bytes = data_string.encode("utf-8")

        event = NewEvent(
            type=CHECKPOINT_STREAM_EVENT_TYPE,
            data=data_bytes,
        )
        cls.client.append_to_stream(
            stream_name=checkpoint_stream, events=event, current_version=StreamState.ANY
        )
        logger.debug(
            f"Stream position {cls.current_stream_position} "
            f"added to the '{checkpoint_stream}'."
        )

    @classmethod
    def get_subscription(
        cls, command_stream: str, checkpoint_stream: str
    ) -> AbstractCatchupSubscription | None:
        cls.__get_start_position(checkpoint_stream)
        response = cls.__try_to_read(command_stream=command_stream)

        if response is None:
            logger.critical(f"There is no '{command_stream}' in EventstoreDB")
            return None

        catchup_subscription = cls.client.subscribe_to_stream(
            stream_name=command_stream, stream_position=cls.current_stream_position
        )
        logger.debug(f"Subscription to the '{command_stream}' stream is done.")

        return catchup_subscription
