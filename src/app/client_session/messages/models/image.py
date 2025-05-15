"""Module Containing ImageMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.models.base import WhatsAppRequestTo


class ImageBody(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    link: Optional[str] = None
    caption: Optional[str] = None


class ImageMessage(WhatsAppRequestTo):
    type_: Literal["image"] = Field(default="image", alias="type")
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

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["image"] = image_payload

        super().__init__(**init_data)
