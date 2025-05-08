"""Module responsible for registering routes"""

from fastapi import FastAPI

from app.routes.home import home_bp
from app.routes.webhook import webhook_bp

def register_routes(app: FastAPI):
    app.include_router(home_bp)
    app.include_router(webhook_bp)