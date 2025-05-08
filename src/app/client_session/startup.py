"""Module responsible for starting up an Asynchronous HTTP Client Session"""

from fastapi import FastAPI
from aiohttp import ClientSession
import logging

log = logging.getLogger(__name__)

async def startup_client_session(app: FastAPI):
    """Starts up a aiohttp Client session and register it to app.state"""
    log.info("Starting Up and registering Client Session")
    
    client_session = ClientSession()
    app.state.client_session = client_session