"""Module Containing Statuses types"""

from typing import Union, Optional, Literal, List
from pydantic import BaseModel, Field


# Base
class Pricing(BaseModel):
    billable: str
    pricing_model: str
    category: str


class StatusesBaseModel(BaseModel):
    id: str
    timestamp: str
    recipient_id: str
    pricing: Optional[Pricing] = None
    
    async def handle(self, **_):
        """Default fallback handler if no subclass overrides."""
        raise NotImplementedError(f"No handler for status {self.status!r}")


class OriginObject(BaseModel):
    type: str


class ConversationObject(BaseModel):
    id: str
    expiration_timestamp: Optional[str] = None
    origin: OriginObject


# Sent
class StatusSent(StatusesBaseModel):
    status: Literal["sent"]
    conversation: ConversationObject


# Delivered
class StatusDelivered(StatusesBaseModel):
    status: Literal["delivered"]
    conversation: ConversationObject


# Read
class StatusRead(StatusesBaseModel):
    status: Literal["read"]


# Failed
class ErrorData(BaseModel):
    details: str


class StatusErrorObject(
    BaseModel
):  # Renamed from ErrosObject to avoid clash and fix typo
    code: int  # Changed to int based on example
    title: str
    message: Optional[str] = None
    error_data: Optional[ErrorData] = None
    href: Optional[str] = None


class StatusFailed(StatusesBaseModel):
    status: Literal["failed"]
    errors: List[StatusErrorObject]


Status = Union[StatusSent, StatusDelivered, StatusRead, StatusFailed]
