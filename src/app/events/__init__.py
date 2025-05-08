"""Register all events"""

from fastapi import FastAPI
import logging

from app.events.startup import startup
from app.events.shutdown import shutdown

log = logging.getLogger(__name__)

def register_events(app: FastAPI):
    log.info("Registering App events")
    
    startup(app)
    shutdown(app)