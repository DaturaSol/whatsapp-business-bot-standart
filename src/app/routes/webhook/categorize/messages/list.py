from pydantic import BaseModel
from typing import Optional, Literal

from app.routes.webhook.categorize.messages.base import BaseMessageModel

class ListReplyObject(BaseModel):
    id: str
    title: str
    description: Optional[str] = None


class InteractiveListObject(BaseModel):
    type: Literal["list_reply"]
    list_reply: ListReplyObject


class ListMessageMessage(BaseMessageModel):
    type: Literal["interactive"]
    interactive: InteractiveListObject
