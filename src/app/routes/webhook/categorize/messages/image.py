
from typing import Optional, Literal

from app.routes.webhook.categorize.messages.base import MediaBaseObject, BaseMessageModel

class ImageObject(MediaBaseObject):
    caption: Optional[str] = None


class ImageMessage(BaseMessageModel):
    type: Literal["image"]
    image: ImageObject