"""Module Containing DocumentMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class DocumentBody(BaseModel):
    id_: Optional[str] = Field(None, alias="id")
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: str


class DocumentMessage(WhatsAppRequestTo):
    type_: Literal["document"] = Field("document", alias="type")
    document: DocumentBody

    def __init__(
        self,
        *,
        to: str,
        filename: str,
        id_: Optional[str] = None,
        link: Optional[str] = None,
        caption: Optional[str] = None,
        **kwargs,
    ):
        document_payload = DocumentBody(
            id=id_, link=link, caption=caption, filename=filename
        )

        super().__init__(to=to, image=document_payload, **kwargs)
