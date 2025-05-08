"""This module is for the logger be able to register which Request is calling the log action
purely for aesthetics, the log file is a mess anyways """

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request
import contextvars
import uuid
import logging

log = logging.getLogger(__name__)


request_id_var = contextvars.ContextVar("request_id", default="NotSet")

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Resquest info for logger"""
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)