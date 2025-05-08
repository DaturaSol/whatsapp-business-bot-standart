from typing import Literal

from app.routes.webhook.categorize.statuses.base import StatusesBaseModel, ConversationObject

class StatusDelivered(StatusesBaseModel):
    status: Literal["delivered"]
    conversation: ConversationObject