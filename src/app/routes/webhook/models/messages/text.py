"""Contains Text message Handdlers"""

from pydantic import BaseModel
from typing import Literal, List
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.routes.webhook.models.contacts import Contact
from app.routes.webhook.models.messages.base import BaseMessageModel

log = logging.getLogger(__name__)

class TextObject(BaseModel):
    body: str


class TextMessage(BaseMessageModel):
    type: Literal["text"]
    text: TextObject

