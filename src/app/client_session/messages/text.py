"""Module Containing TextMesage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class TextBody(BaseModel):
    body: str
    preview_url: Optional[bool] = None


class TextMessage(WhatsAppRequestTo):
    type_: Literal["text"] = Field("text", alias="type")
    text: TextBody

    def __init__(self, *, to: str, body_text: str, preview_url: bool = None, **kwargs):

        text_payload = TextBody(body=body_text, preview_url=preview_url)

        super().__init__(to=to, text=text_payload, **kwargs)
