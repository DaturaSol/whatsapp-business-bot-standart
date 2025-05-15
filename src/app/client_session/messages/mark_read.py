from pydantic import BaseModel, Field
from typing import Literal

from app.client_session.messages.base import WhatsAppRequest


class MarkAsRead(WhatsAppRequest):
    status: Literal["read"] = "read"
    message_id: str
