from typing import Literal

from app.routes.webhook.models.statuses.base import StatusesBaseModel, ConversationObject

class StatusDelivered(StatusesBaseModel):
    status: Literal["delivered"] = "delivered"
    conversation: ConversationObject