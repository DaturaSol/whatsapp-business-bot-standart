from typing import Optional, Literal, List
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.routes.webhook.models.messages.base import MediaBaseObject, BaseMessageModel
from app.routes.webhook.models.contacts import Contact

log = logging.getLogger(__name__)


class VideoObject(MediaBaseObject):
    caption: Optional[str] = None


class VideoMessage(BaseMessageModel):
    type: Literal["video"]
    video: VideoObject
