"""Process Events that should happen on shutdown"""

from fastapi import FastAPI
from app.client_session.shutdown import shutdown_client_session
import logging

log = logging.getLogger(__name__)


def shutdown(app: FastAPI):
    log.info("Registering Shutdown Events")

    event_type = "shutdown"

    async def wrapper_shutdown_client_session():
        """Calls the actual client session shutdown with the app instance."""
        log.info("Registering shutdown Client Session")
        await shutdown_client_session(app=app)

    app.add_event_handler(event_type, wrapper_shutdown_client_session)
