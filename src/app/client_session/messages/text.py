from pydantic import BaseModel, Field
from typing import Literal

from app.client_session.messages.base import WhatsAppRequest

class TextBody(BaseModel):
    body: str

class TextMessage(WhatsAppRequest):
    type: Literal["text"] = Field("text", alias="type")
    text: TextBody