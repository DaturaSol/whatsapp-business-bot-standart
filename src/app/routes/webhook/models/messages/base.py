"""Module containing Base Models for Message types"""

from pydantic import BaseModel, Field
import logging


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

