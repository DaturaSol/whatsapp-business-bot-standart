from typing import Literal

from app.routes.webhook.models.statuses.base import StatusesBaseModel, ConversationObject

class StatusSent(StatusesBaseModel):
    status: Literal["sent"]
    conversation: ConversationObject
