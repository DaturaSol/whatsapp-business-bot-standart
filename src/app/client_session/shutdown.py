"""Module responsible for shutting down an Asynchronous HTTP Client Session"""

from aiohttp import ClientSession
from fastapi import FastAPI
import logging

log = logging.getLogger(__name__)

async def shutdown_client_session(app: FastAPI): # Take FastAPI app as argument
    """Closes the aiohttp ClientSession on app shutdown."""
    log.info("Shutting Down Client Session")
    
    client_session: ClientSession = app.state.client_session
    
    if client_session and not client_session.closed:
        await client_session.close()