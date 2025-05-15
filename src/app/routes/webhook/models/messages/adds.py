from pydantic import BaseModel
from typing import Literal, Optional

from app.routes.webhook.models.messages.base import BaseMessageModel
from app.routes.webhook.models.messages.text import TextObject

class ReferalObject(BaseModel):
    source_url: str
    source_id: str
    source_type: str
    headline: str
    body: str
    media_type: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    ctwa_clid: Optional[str] = None


class AidsMessage(BaseMessageModel):
    type: Literal["text"]
    text: TextObject
    referral: ReferalObject