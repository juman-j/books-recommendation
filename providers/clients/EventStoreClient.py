from esdbclient import EventStoreDBClient
from esdbclient.exceptions import DiscoveryFailed
from loguru import logger

from configurations.config import LOCAL_CONNECTION_STRING
from helpers.exceptions import ESDBConnectionError


class EventStoreClient:

    @classmethod
    def __choose_client(cls, local_client: bool) -> tuple[str, str | None]:
        if local_client:
            uri = str(LOCAL_CONNECTION_STRING)
            root_certificates = None
        else:
            # space to retrieve cloud EventStore connection data
            uri = None
            root_certificates = None

        return uri, root_certificates

    @classmethod
    def get_client(cls, local_client: bool = True) -> EventStoreDBClient:
        uri, root_certificates = cls.__choose_client(local_client)
        try:
            client = EventStoreDBClient(uri, root_certificates=root_certificates)
            logger.debug("The EventStoreDB client has been set up.")
            return client

        except DiscoveryFailed as e:
            logger.critical("EventStoreDB connection error.")
            raise ESDBConnectionError("EventStoreDB connection error.") from e
