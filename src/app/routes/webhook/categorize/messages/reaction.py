from pydantic import BaseModel
from typing import Literal

from app.routes.webhook.categorize.messages.base import BaseMessageModel

class ReactionObject(BaseModel):
    message_id: str
    emoji: str


class ReactionMessage(BaseMessageModel):
    type: Literal["reaction"]
    reaction: ReactionObject