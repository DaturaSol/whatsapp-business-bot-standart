"""Module containing Base Models for Message types"""

from typing import Optional, List
from pydantic import BaseModel, Field
import logging
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_base.db_helper.crud import get_or_create_user
from app.scripiter import ScriptBaseModel
from app.scripiter.models import registery
from app.routes.webhook.models.contacts import Contact

log = logging.getLogger(__name__)


class MediaBaseObject(BaseModel):
    mime_type: str
    sha256: str
    id: str


class BaseMessageModel(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str

    async def default_message(self):  # TODO: Implement a lazy method
        raise NotImplementedError("No default message set!")

    async def handle(
        self,
        db_session: AsyncSession,
        client_session: ClientSession,
        contacts: Optional[List[Contact]] | None = None,
    ):
        """Default fallback handler if no subclass overrides."""
        if (
            contacts
        ):  # This means the webhook recived is from an active user and there is someone to send something
            contact = contacts[0]  # Only interested in the first
            wa_id = contact.wa_id
            name = (
                contact.profile.name
            )  # Cauntion non UTF-8 characters will most likely cause some error
            user = await get_or_create_user(
                async_session=db_session, wa_id=wa_id, formatted_name=name
            )  # Fecthes fetid user from the data Base
            current_step = user.current_step  # Gets where they are on the conversation
            handle_cls = registery.get(current_step)  # Gets the current step

            if handle_cls:  # If there is one
                handle: ScriptBaseModel = handle_cls( # I will have circular import here if i fix 
                    db_session=db_session,
                    client_session=client_session,
                    registery=registery,
                )
                if (
                    self.__name__ in handle.expected_type
                ):  # If this current webhook is of the expected type, all is ok
                    await handle.handle(self) # TODO: Fix this shit, but i will have circular imports, 
                else:  # Default message for unexpected types
                    await self.default_message()
