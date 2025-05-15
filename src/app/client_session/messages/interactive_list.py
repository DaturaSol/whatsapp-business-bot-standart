"""Module Containing Call to Action Url Interactive Button Message Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Any

from app.client_session.messages.base import WhatsAppRequestTo


class IntListHeaderObject(BaseModel):
    type_: Literal["text"] = Field(default="text", alias="type")
    text: str


class IntListBodyObject(BaseModel):
    text: str


class IntListFooterObject(BaseModel):
    text: str


class IntListRowObject(BaseModel):
    id_: str = Field(..., alias="id")
    title: str
    description: Optional[str] = None


class IntListSectionObject(BaseModel):
    title: str
    rows: List[IntListRowObject]


class IntListSectionsObject(BaseModel):
    sections: List[IntListSectionObject] = []
    button: str


class InteractiveListObject(BaseModel):
    type_: Literal["list"] = Field(default="list", alias="type")
    header: Optional[IntListHeaderObject] = None
    body: IntListBodyObject
    footer: Optional[IntListFooterObject] = None
    actions: IntListSectionsObject


class InteractiveListMessage(WhatsAppRequestTo):
    type_: Literal["interactive"] = Field(default="interactive", alias="type")
    interactive: InteractiveListObject

    def __init__(self, *, to: str, button_name: str, body_text: str, **kwargs):

        action_payload = IntListSectionsObject(button=button_name)
        body_payload = IntListBodyObject(text=body_text)

        interactive_payload = InteractiveListObject(
            actions=action_payload, body=body_payload
        )

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["interactive"] = interactive_payload

        super().__init__(**init_data)

    def add_header(self, text: str):
        self.interactive.header = IntListHeaderObject(text=text)
        return self

    def add_footer(self, text: str):
        self.interactive.footer = IntListFooterObject(text=text)
        return self

    def add_section(self, section_data: dict[str, Any]):
        """Adds another row to the list, pay attention, we can only
        have 7 items, and each id must be unique.

        Example:
        ```
        {
            "title": "_",
            "rows": [
                {"id": "_", "title": "_", "description": "_"},
                {"id": "_", "title": "_", "description": "_"}
            ]
        }
        ```
        """
        section = IntListSectionObject.model_validate(section_data)
        self.interactive.actions.sections.append(section)

        return self
