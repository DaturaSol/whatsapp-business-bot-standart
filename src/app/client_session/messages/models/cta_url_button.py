"""Module Containing Call to Action Url Interactive Button Message Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.models.base import WhatsAppRequestTo


class CTAParameters(BaseModel):
    display_text: str
    url: str


class CTAction(BaseModel):
    name: Literal["cta_url"] = "cta_url"
    parameters: CTAParameters


class CTAFooter(BaseModel):
    text: str


class CTABody(BaseModel):
    text: str


class CTAHeader(BaseModel):
    type_: Literal["text"] = Field(default="text", alias="type")
    text: str


class ICTAUrlObject(BaseModel):
    type_: Literal["cta_url"] = Field(default="cta_url", alias="type")
    header: Optional[CTAHeader] = None
    body: CTABody
    footer: Optional[CTAFooter] = None
    action: CTAction


class CTAUrlButtonMessage(WhatsAppRequestTo):
    type_: Literal["interactive"] = Field(default="interactive", alias="type")
    interactive: ICTAUrlObject

    def __init__(
        self, *, to: str, display_text: str, url: str, body_text: str, **kwargs
    ):
        body_payload = CTABody(text=body_text)
        parameters_payload = CTAParameters(display_text=display_text, url=url)
        action_payload = CTAction(parameters=parameters_payload)
        interactive_paylaod = ICTAUrlObject(body=body_payload, action=action_payload)

        init_data = kwargs.copy()
        init_data["to"] = to
        init_data["interactive"] = interactive_paylaod

        super().__init__(**init_data)

    def add_header(self, text: str):
        self.interactive.header = CTAHeader(text=text)
        return self

    def add_footer(self, text: str):
        self.interactive.footer = CTAFooter(text=text)
        return self
