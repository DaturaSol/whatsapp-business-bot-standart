from fastapi import Request, FastAPI
from aiohttp import ClientSession

async def get_async_client_session_dependency(
    request: Request,
) -> ClientSession:
    """Yields a client session
    to be used inside of FastApi 
    Post, routes."""
    app: FastAPI = request.app
    client_session = app.state.client_session
    return client_session
