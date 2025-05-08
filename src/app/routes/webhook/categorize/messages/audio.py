from typing import Optional, Literal

from app.routes.webhook.categorize.messages.base import MediaBaseObject, BaseMessageModel

class AudioObject(MediaBaseObject):
    voice: Optional[bool] = None


class AudioMessage(BaseMessageModel):
    type: Literal["audio"]
    audio: AudioObject