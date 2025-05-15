"""Module Containing DocumentMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


class DocumentBody(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: str


class DocumentMessage(WhatsAppRequestTo):
    type_: Literal["document"] = Field(default="document", alias="type")
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

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["document"] = document_payload

        super().__init__(**init_data)
