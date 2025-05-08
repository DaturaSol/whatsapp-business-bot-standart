"""Module responsible for registering middleware"""


from fastapi import FastAPI
from app.middleware.resquest_id import RequestIdMiddleware
import logging

log = logging.getLogger(__name__)


def register_middleware(app: FastAPI):
    """Registers middleware"""
    log.info("Registering Middle Ware")
    
    app.add_middleware(RequestIdMiddleware)