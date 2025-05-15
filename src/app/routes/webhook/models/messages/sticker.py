from typing import Literal

from app.routes.webhook.models.messages.base import MediaBaseObject, BaseMessageModel

class StickerMessage(BaseMessageModel):
    type: Literal["sticker"]
    sticker: MediaBaseObject
