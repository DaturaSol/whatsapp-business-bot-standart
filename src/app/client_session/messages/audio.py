"""Module Containing AudioMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class AudioBody(BaseModel):
    id: Optional[str] = None
    link: Optional[str] = None


class AudioMessage(WhatsAppRequestTo):
    type_: Literal["audio"] = Field("audio", alias="type")
    audio: Optional[AudioBody] = None

    def write_body(self, id: Optional[str] = None, link: Optional[bool] = None):
        self.audio = AudioBody(id=id, link=link)
        return self
