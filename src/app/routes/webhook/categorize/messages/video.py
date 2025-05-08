from typing import Optional, Literal

from app.routes.webhook.categorize.messages.base import MediaBaseObject, BaseMessageModel

class VideoObject(MediaBaseObject):
    caption: Optional[str] = None


class VideoMessage(BaseMessageModel):
    type: Literal["video"]
    video: VideoObject