"""Module responsible for creating the app with default configurations"""

from fastapi import FastAPI
from app.logger import setup_logging
from app.events import register_events
from app.middleware import register_middleware
from app.routes import register_routes
import logging
from dotenv import load_dotenv  # TODO: Remove load_dotenv when it comes to production.

log = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Register a FastAPI instance"""
    app = FastAPI()
    setup_logging()
    register_events(app)
    register_middleware(app)
    register_routes(app)
    
    return app


def ensure_dotenv():
    log.info("Loading dotenv")
    is_dotenv_loaded = (
        load_dotenv()
    )  # TODO: Remove load_dotenv when it comes to production.
    if is_dotenv_loaded:
        log.info("Loaded environment variables from .env file.")
    else:
        log.info("No .env file found or it was empty. Using existing environment.")
