"""Module responsible for Startign up the DataBase"""

from fastapi import FastAPI
import logging
from sqlalchemy.ext.asyncio import AsyncEngine

from app.data_base.db_helper.core import init_db_engine
from app.data_base.db_helper.core import Base
import app.data_base.models

log = logging.getLogger(__name__)


async def startup_db(app: FastAPI):
    """Starts and register the Asynchronous db engine for the app"""
    log.info("Starting up Data Base")

    engine = init_db_engine()
    app.state.db_engine = engine
    await create_db_tables(engine)


async def create_db_tables(engine: AsyncEngine):
    """Creates all table classes registered under `Base`.

    Args:
        engine (AsyncEngine): Recieves and engine that should come from `init_db_engine`
    """
    log.info("Creating Tables")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
