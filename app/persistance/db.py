"""Database connection and setup"""

import os

from typing import Optional
from pathlib import Path

from sqlmodel import SQLModel, create_engine, Session

from configs.logging_config import get_logger

logger = get_logger(__name__)

# local stored database
DATABASE_DIRECTORY = Path(__file__).parents[1]

# * Local database
DATABASE_URL = "sqlite:///" + str(DATABASE_DIRECTORY / "app.db")

# * In-memory database for testing
TEST_DATABASE_URL = "sqlite:///" + str(DATABASE_DIRECTORY / "test.db")

if os.getenv("ENV") == "PRODUCTION":
    DB_URL_TO_USE = DATABASE_URL
else:
    DB_URL_TO_USE = TEST_DATABASE_URL

engine = create_engine(DB_URL_TO_USE, echo=True)


def create_db_and_tables() -> None:
    """Create database tables if they don't exist"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Error creating database tables: %s", str(e))
        raise


def get_session() -> Session:
    """Get a database session"""
    return Session(engine)


# Initialize database
create_db_and_tables()
logger.info("Using database located at: %s", DB_URL_TO_USE)
