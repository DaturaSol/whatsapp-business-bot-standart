from pydantic import BaseModel
from typing import List, Literal

from app.routes.webhook.models.messages.base import  BaseMessageModel

class UnknownObject(BaseModel):
    code: int
    details: str
    title: str


class UnknownMessage(BaseMessageModel):
    type: Literal["unknown"]
    errors: List[UnknownObject]
