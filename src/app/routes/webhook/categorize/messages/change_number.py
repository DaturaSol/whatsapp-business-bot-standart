from pydantic import BaseModel
from typing import Literal

from app.routes.webhook.categorize.messages.base import BaseMessageModel

class SystemObject(BaseModel):
    type: Literal["user_changed_number"]
    body: str
    new_wa_id: str


class ChangeNumberMessage(BaseMessageModel):
    type: Literal["system"]
    system: SystemObject