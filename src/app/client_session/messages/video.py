"""Module Containing VideoMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class VideoBody(BaseModel):
    id_: Optional[str] = Field(None, alias="id")
    link: Optional[str] = None
    caption: Optional[str] = None


class VideoMessage(WhatsAppRequestTo):
    type_: Literal["video"] = Field("video", alias="type")
    video: VideoBody

    def __init__(
        self,
        *,
        to: str,
        id_: Optional[str] = None,
        link: Optional[str] = None,
        caption: Optional[str] = None,
        **kwargs,
    ):
        video_payload = VideoBody(id=id_, link=link, caption=caption)

        super().__init__(to=to, video=video_payload, **kwargs)

