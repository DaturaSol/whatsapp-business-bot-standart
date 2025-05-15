"""Module Containing TextMesage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class TextBody(BaseModel):
    body: str
    preview_url: Optional[bool] = None


class TextMessage(WhatsAppRequestTo):
    type_: Literal["text"] = Field(default="text", alias="type")
    text: TextBody

    def __init__(self, *, to: str, body_text: str, preview_url: bool = False, **kwargs):

        text_payload = TextBody(body=body_text, preview_url=preview_url)

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["text"] = text_payload

        super().__init__(**init_data)
