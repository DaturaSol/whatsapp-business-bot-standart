"""Module Containing ImageMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class ImageBody(BaseModel):
    id: Optional[str] = None
    link: Optional[str] = None
    caption: Optional[str] = None


class ImageMessage(WhatsAppRequestTo):
    type_: Literal["image"] = Field("image", alias="type")
    image: Optional[ImageBody] = None

    def write_body(
        self,
        id: Optional[str] = None,
        link: Optional[bool] = None,
        caption: Optional[str] = None,
    ):
        self.image = ImageBody(id=id, link=link, caption=caption)
        return self