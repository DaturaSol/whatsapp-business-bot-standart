from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo

class TextBody(BaseModel):
    body: str
    preview_url: Optional[bool] = None

class TextMessage(WhatsAppRequestTo):
    type_: Literal["text"] = Field("text", alias="type")
    text: Optional[TextBody] = None
    
    def write_body(self, body:str, preview_url: Optional[bool]=None):
        self.text = TextBody(body=body, preview_url=preview_url)
        return self