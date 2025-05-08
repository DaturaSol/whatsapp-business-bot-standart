"""Process Events that should happen on startup"""

from fastapi import FastAPI
import logging

from app.client_session.startup import startup_client_session
from app.data_base.startup import startup_db

log = logging.getLogger(__name__)


def startup(app: FastAPI):
    log.info("Registering startup events")
    event_type = "startup"

    async def wrapper_startup_client_session():
        """Calls the actual client session startup with the app instance."""
        log.info("Registering Client Session")
        await startup_client_session(app=app)

    async def wrapper_startup_db():
        """Calls the actual db startup with the app instance."""
        log.info("Registering StartUp Data Base")
        await startup_db(app=app)

    app.add_event_handler(event_type, wrapper_startup_client_session)
    app.add_event_handler(event_type, wrapper_startup_db)
