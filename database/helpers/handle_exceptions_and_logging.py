import time
from functools import wraps

from loguru import logger
from sqlalchemy.orm import Session

from helpers.exceptions import DBError


def handle_exceptions_and_logging(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        session: Session = getattr(self, "session", None)

        try:
            start = time.time()
            result = func(self, *args, **kwargs)
            finish = round(time.time() - start, 3)
            logger.debug(f"{func.__qualname__}(): OK. within {finish} sec.")

            return result

        except Exception as e:
            session.rollback()
            logger.error(
                f"{func.__qualname__}(): "
                "Failed to execute due to a database error. "
                f"(with e: {e})"
            )
            raise DBError(
                f"{func.__qualname__}(): "
                "Failed to execute due to a database error. "
                f"(with e: {e})"
            ) from e

        finally:
            session.close()

    return wrapper
