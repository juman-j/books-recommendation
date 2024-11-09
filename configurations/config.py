import os

from dotenv import load_dotenv

load_dotenv()

# APPSETTINGS
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PASS = os.environ.get("DB_PASS")
DB_PORT = os.environ.get("DB_PORT")

# EventStore
COMMAND_STREAM = os.environ.get("COMMAND_STREAM")
CHECKPOINT_STREAM = os.environ.get("CHECKPOINT_STREAM")
CHECKPOINT_STREAM_EVENT_TYPE = os.environ.get("CHECKPOINT_STREAM_EVENT_TYPE")
LOCAL_CONNECTION_STRING = os.environ.get("LOCAL_CONNECTION_STRING")

BOOKS_DF = os.environ.get("BOOKS_DF")
RATINGS_DF = os.environ.get("RATINGS_DF")
USERS_DF = os.environ.get("USERS_DF")

TEST_SIZE = float(os.environ.get("TEST_SIZE"))
VALIDATION_SIZE = float(os.environ.get("VALIDATION_SIZE"))

RATING_SCALE_MIN = int(os.environ.get("RATING_SCALE_MIN"))
RATING_SCALE_MAX = int(os.environ.get("RATING_SCALE_MAX"))
