"""Contains Text message Handdlers"""

from pydantic import BaseModel
from typing import Literal, List
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.routes.webhook.categorize.contacts import Contact
from app.routes.webhook.categorize.messages.base import BaseMessageModel


class TextObject(BaseModel):
    body: str


class TextMessage(BaseMessageModel):
    type: Literal["text"]
    text: TextObject

    async def handle(
        self,
        db_session: AsyncSession,
        client_session: ClientSession,
        contacts: List[Contact],
    ):
        """Most messages will be of this type.
        All Text Messages WebHooks comes with
        contacts information"""

        raise NotImplementedError(f"No handler for Text Message")
