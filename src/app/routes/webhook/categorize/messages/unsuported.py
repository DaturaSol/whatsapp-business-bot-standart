from pydantic import BaseModel
from typing import List, Literal

from app.routes.webhook.categorize.messages.base import BaseMessageModel

class ErrorObject(BaseModel):
    code: int
    details: str
    title: str


class UnsupportedMessage(BaseMessageModel):
    type: Literal["unsupported"]
    errors: List[ErrorObject]