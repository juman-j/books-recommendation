import json

import init
from loguru import logger
from pydantic import ValidationError

from configurations.config import CHECKPOINT_STREAM, COMMAND_STREAM
from data_models.EventDataModel import EventDataModel
from providers.EventStoreProvider import EventStoreProvider
from services.RecommendationService import RecommendationService


class BookRecommendationEngine:
    _esb_provider = EventStoreProvider

    @classmethod
    def run(cls) -> None:
        subscription = cls._esb_provider.get_subscription(
            command_stream=COMMAND_STREAM,
            checkpoint_stream=CHECKPOINT_STREAM,
        )
        try:
            for event in subscription:
                logger.debug("Event received.")
                cls._esb_provider.update_current_stream_position(event.stream_position)

                try:
                    raw_event_data: dict = json.loads(event.data)
                    event_data = EventDataModel(**raw_event_data)
                except ValidationError as e:
                    logger.error(f"Validation error: {e}")
                    break

                try:
                    recommendation_service = RecommendationService(event_data)
                    recommendation_service.run()

                except KeyboardInterrupt:
                    subscription.stop()
                    logger.info("Keyboard Interrupt. Subscription stopped.")
                    break

                except Exception as e:
                    subscription.stop()
                    logger.error(f"Error: {e}. Subscription stopped.")
                    break

                finally:
                    # clean resources
                    cls._esb_provider.add_stream_position(
                        checkpoint_stream=CHECKPOINT_STREAM
                    )

        except KeyboardInterrupt:
            subscription.stop()
            logger.info("Keyboard Interrupt. Subscription stopped.")

        except Exception as e:
            subscription.stop()
            logger.error(f"Error: {e}. Subscription stopped.")


if __name__ == "__main__":
    BookRecommendationEngine.run()
