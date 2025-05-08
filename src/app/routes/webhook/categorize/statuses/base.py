from typing import Optional
from pydantic import BaseModel
import logging

log = logging.getLogger(__name__)

class Pricing(BaseModel):
    billable: str
    pricing_model: str
    category: str


class StatusesBaseModel(BaseModel):
    id: str
    timestamp: str
    recipient_id: str
    pricing: Optional[Pricing] = None
    
    async def handle(self):
        """Default fallback handler if no subclass overrides."""
        log.info('Status captured by webhook')
        raise NotImplementedError(f"No handler for Statuses")


class OriginObject(BaseModel):
    type: str


class ConversationObject(BaseModel):
    id: str
    expiration_timestamp: Optional[str] = None
    origin: OriginObject