"""Module Containing ImageMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class ImageBody(BaseModel):
    id_: Optional[str] = Field(None, alias="id")
    link: Optional[str] = None
    caption: Optional[str] = None


class ImageMessage(WhatsAppRequestTo):
    type_: Literal["image"] = Field("image", alias="type")
    image: ImageBody

    def __init__(
        self,
        *,
        to: str,
        id_: Optional[str] = None,
        link: Optional[str] = None,
        caption: Optional[str] = None,
        **kwargs,
    ):
        image_payload = ImageBody(id=id_, link=link, caption=caption)

        super().__init__(to=to, image=image_payload, **kwargs)
        