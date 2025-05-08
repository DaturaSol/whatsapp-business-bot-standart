"""Module Containing DocumentMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class DocumentBody(BaseModel):
    id: Optional[str] = None
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: str


class DocumentMessage(WhatsAppRequestTo):
    type_: Literal["document"] = Field("document", alias="type")
    document: Optional[DocumentBody] = None

    def write_body(
        self,
        filename: str,
        id: Optional[str] = None,
        link: Optional[bool] = None,
        caption: Optional[str] = None,
    ):
        self.document = DocumentBody(
            id=id, link=link, caption=caption, filename=filename
        )
        return self
