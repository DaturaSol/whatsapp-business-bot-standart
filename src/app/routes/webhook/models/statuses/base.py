from typing import Optional
from pydantic import BaseModel
import logging

log = logging.getLogger(__name__)

class Pricing(BaseModel):
    billable: bool
    pricing_model: str
    category: str


class StatusesBaseModel(BaseModel):
    id: str
    timestamp: str
    recipient_id: str
    pricing: Optional[Pricing] = None
    

class OriginObject(BaseModel):
    type: str


class ConversationObject(BaseModel):
    id: str
    expiration_timestamp: Optional[str] = None
    origin: OriginObject