"""Module containing Base Models for Message types"""

from typing import Optional, List
from pydantic import BaseModel, Field
import logging
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.routes.webhook.categorize.contacts import Contact

log = logging.getLogger(__name__)


class MediaBaseObject(BaseModel):
    mime_type: str
    sha256: str
    id: str


class BaseMessageModel(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str

    async def handle(
        self,
        db_session: AsyncSession,
        client_session: ClientSession,
        contacts: Optional[List[Contact]] = None,
    ):
        """Default fallback handler if no subclass overrides."""
        # TODO: Add Data Base interaction, check:
        # Is user already register?
        # If not register it right away
        if contacts:
            contact = contacts[0]
            wa_id = contact.wa_id
            name = contact.profile.name
        raise NotImplementedError(f"No handler for Messages")
