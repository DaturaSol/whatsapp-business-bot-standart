"""Module Containing AudioMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class AudioBody(BaseModel):
    id_: Optional[str] = Field(None, alias="id")
    link: Optional[str] = None


class AudioMessage(WhatsAppRequestTo):
    type_: Literal["audio"] = Field("audio", alias="type")
    audio: AudioBody

    def __init__(
        self,
        *,
        to: str,
        id_: Optional[str] = None,
        link: Optional[str] = None,
        **kwargs,
    ):

        audio_payload = AudioBody(id=id_, link=link)

        super().__init__(to=to, audio=audio_payload, **kwargs)
