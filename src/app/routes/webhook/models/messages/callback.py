from pydantic import BaseModel, Field
from typing import Literal

from app.routes.webhook.models.messages.base import MediaBaseObject, BaseMessageModel

class CallBackContext(BaseModel):
    from_: str = Field(..., alias="from")
    id: str


class CallBackButtonObject(BaseModel):
    text: str
    payload: str


class CallBackButtonMessage(BaseMessageModel):
    context: CallBackContext
    type: Literal["button"]
    button: CallBackButtonObject