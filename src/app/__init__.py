"""Module responsible for creating the app with default configurations"""

from fastapi import FastAPI
from app.logger import setup_logging
from app.events import register_events
from app.middleware import register_middleware
from app.routes import register_routes
import logging

log = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Register a FastAPI instance"""
    app = FastAPI()
    setup_logging()
    register_events(app)
    register_middleware(app)
    register_routes(app)
    
    return app