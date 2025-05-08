"""File responsible for carrying core
concepts when it comes to creating the Data Base.

## Responsible for

1. Make sure db folder exists;
2. Load all information from the enviroment;
3. Call the Declarative Base;
4. Contain core functions such as:
[init_db_engine, create_db_tables, create_async_session, get_async_session]"""

import os
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)
from fastapi import FastAPI, Request
from pathlib import Path
import logging

log = logging.getLogger(__name__)

DB_FOLDER_NAME = "db"
DB_URL = None

# NOTE: This is only for local SQLite
try:
    CURRENT_DIR = Path.cwd()

    DB_FOLDER_PATH = CURRENT_DIR / DB_FOLDER_NAME

    if not DB_FOLDER_PATH.exists():
        log.warning(f"Database folder '{DB_FOLDER_PATH}' does not exist. Creating.")

        try:
            DB_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
            log.info(f"Successfully ensured database folder exists: {DB_FOLDER_PATH}")

        except OSError as e:
            log.error(f"Failed to create database folder '{DB_FOLDER_PATH}': {e}")
            raise RuntimeError(
                f"Could not create database directory: {DB_FOLDER_PATH}"
            ) from e

    else:
        log.info(f"Database folder found: {DB_FOLDER_PATH}")

    DB_URL = os.environ.get("DB_URL")

    if DB_URL is None:
        log.error("Required environment variable 'DB_URL' is not set.")

        DB_URL = "sqlite+aiosqlite:///./db/db.db"  # NOTE: Wont work for postergres

        log.warning(f"DB_URL not set, using default local path: {DB_URL}")
    else:
        log.info("DB_URL successfully retrieved from environment.")

except (ValueError, RuntimeError) as e:
    log.critical(f"Configuration failed: {e}")
    raise

except Exception as e:
    log.exception(f"An unexpected error occurred during setup: {e}")
    raise

log.info(f"Setup complete. Using DB_URL: {DB_URL[:15]}...")


Base = declarative_base()


# TODO: Handle exceptions for all functions bellow.
# TODO: Implement logging


def init_db_engine(db_url: str = DB_URL) -> AsyncEngine:
    """Creates an Asynchronous Engine to be used
    with `async_sessionmaker` as it is connects to the data base
    declared on enviroment.

    Returns:
        AsyncEngine: _description_
    """
    log.info("Creating Engine")

    engine = create_async_engine(db_url, echo=False)
    return engine


def create_async_session(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Creates an `async_sessionmaker` used to access `AsyncSession`

    Args:
        engine (AsyncEngine): Should be recieving from `init_db_engine`

    Returns:
        async_sessionmaker[AsyncSession]: A `async_sessionmaker` containing
        a list of `AsyncSession` to be used.
    """
    log.info(f"Creating async Session")

    local_async_session = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    return local_async_session


async def get_async_session(engine: AsyncEngine):
    """Deliveres an Iterator

    Args:
        engine (AsyncEngine): Should be recieving from `init_db_engine`

    Yields:
        async_session (Iterator[AsyncGenerator[AsyncSession, None]]): An iterator over all `async_session`
    """
    local_async_session = create_async_session(engine)
    async with local_async_session() as async_session:
        try:
            log.info(f"Starting async Session")
            yield async_session
            await async_session.commit()
            log.info(f"Commiting Session")
        except Exception as e:
            log.warning(f"Rolling back Session")
            log.exception(f"Exception: {e}")
            await async_session.rollback()
            raise e
        finally:
            log.info(f"Closing async Session")
            await async_session.close()


async def get_async_session_dependency(
    request: Request,
):
    """Provides a `AsyncSession` for `FastAPI`.

    Args:
        request (Request): FastAPI Handles this.

    Yields:
        db_session (Iterator[AsyncGenerator[AsyncSession, None]]): Iterator for `FastAPI` to use.
    """
    app: FastAPI = request.app
    engine = app.state.db_engine
    async for db_session in get_async_session(engine):
        yield db_session
