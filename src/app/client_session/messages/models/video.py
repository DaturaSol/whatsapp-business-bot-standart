"""Module Containing VideoMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.models.base import WhatsAppRequestTo


class VideoBody(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    link: Optional[str] = None
    caption: Optional[str] = None


class VideoMessage(WhatsAppRequestTo):
    type_: Literal["video"] = Field(default="video", alias="type")
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

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["video"] = video_payload

        super().__init__(**init_data)
