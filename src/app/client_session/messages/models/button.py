"""Another rushed implementation"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Any

from app.client_session.messages.models.base import WhatsAppRequestTo


class IntButtonHeaderObject(BaseModel):
    type_: Literal["text"] = Field(default="text", alias="type")
    text: str


class IntButtonBodyObject(BaseModel):
    text: str


class IntButtonFooterObject(BaseModel):
    text: str


class ReplyObject(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None


class ButtonObject(BaseModel):
    type_: Literal["reply"] = Field(default="reply", alias="type")
    reply: ReplyObject


class IntButtonObject(BaseModel):
    buttons: List[ButtonObject]


class InteractiveButtonObject(BaseModel):
    type_: Literal["button"] = Field(default="button", alias="type")
    header: Optional[IntButtonHeaderObject] = None
    body: IntButtonBodyObject
    footer: Optional[IntButtonFooterObject] = None
    action: IntButtonObject


class InteractiveButtonMessage(WhatsAppRequestTo):
    type_: Literal["interactive"] = Field(default="interactive", alias="type")
    interactive: InteractiveButtonObject

    def __init__(
        self, *, to: str, body_text: str, buttons: List[dict[str, Any]], **kwargs
    ):
        """buttons should be:
        ```
        [
            {"id": id, "title": title},
            {"id": id, "title": title}
        ]
        ```"""
        buttons_payload = []
        for dic in buttons:
            id = dic.get("id")
            title = dic.get("title")
            reply_payload = ReplyObject(id=id, title=title)
            button_object_payload = ButtonObject(reply=reply_payload)
            buttons_payload.append(button_object_payload)

        action_payload = IntButtonObject(buttons=buttons_payload)
        body_payload = IntButtonBodyObject(text=body_text)
        interactive_payload = InteractiveButtonObject(
            body=body_payload, action=action_payload
        )

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["interactive"] = interactive_payload

        super().__init__(**init_data)

    def add_header(self, text: str):
        self.interactive.header = IntButtonHeaderObject(text=text)
        return self

    def add_footer(self, text: str):
        self.interactive.footer = IntButtonFooterObject(text=text)
        return self
