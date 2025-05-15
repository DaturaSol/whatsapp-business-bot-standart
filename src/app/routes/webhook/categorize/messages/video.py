from typing import Optional, Literal, List
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.routes.webhook.categorize.messages.base import MediaBaseObject, BaseMessageModel
from app.routes.webhook.categorize.contacts import Contact

log = logging.getLogger(__name__)

class VideoObject(MediaBaseObject):
    caption: Optional[str] = None


class VideoMessage(BaseMessageModel):
    type: Literal["video"]
    video: VideoObject
    
    async def handle(
        self,
        db_session: AsyncSession,
        client_session: ClientSession,
        contacts: Optional[List[Contact]] = None,
    ):
        log.info(f"[SHA256]: {self.video.sha256}")
        
        # raise NotImplementedError("No implemantiotn for video")