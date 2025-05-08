from typing import Literal

from app.routes.webhook.categorize.messages.base import MediaBaseObject, BaseMessageModel

class StickerMessage(BaseMessageModel):
    type: Literal["sticker"]
    sticker: MediaBaseObject
