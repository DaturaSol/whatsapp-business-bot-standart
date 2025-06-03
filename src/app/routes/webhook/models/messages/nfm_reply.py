"""This works, but is not specific at alll"""
from pydantic import BaseModel, Field
from typing import Literal

from app.routes.webhook.models.contacts import Contact
from app.routes.webhook.models.messages.base import BaseMessageModel



class NfmReplyObject(BaseModel):
    response_json: str
    body: str
    name: str

class InteractiveNfmObject(BaseModel):
    type_: Literal["nfm_reply"] = Field(default="nfm_reply", alias="type")
    nfm_reply: NfmReplyObject

class NfmReplyMessage(BaseMessageModel):
    type_: Literal["interactive"] = Field(default="interactive", alias="type")
    interactive: InteractiveNfmObject