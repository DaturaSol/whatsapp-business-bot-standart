from pydantic import BaseModel
from typing import  Literal

from app.routes.webhook.categorize.messages.base import BaseMessageModel

class ButtonReplyObject(BaseModel):
    id: str
    title: str


class InteractiveButtonObject(BaseModel):
    type: Literal["button_reply"]
    button_reply: ButtonReplyObject


class ButtonMessageMessage(BaseMessageModel):
    type: Literal["interactive"]
    interactive: InteractiveButtonObject