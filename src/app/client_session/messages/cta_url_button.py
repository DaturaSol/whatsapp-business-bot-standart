"""Module Containing Call to Action Url Interactive Button Message Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.client_session.messages.base import WhatsAppRequestTo


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
    type_: Literal["text"] = Field("text", alias="type")
    text: str


class ICTAUrlObject(BaseModel):
    type_: Literal["cta_url"] = Field("cta_url", alias="type")
    header: Optional[CTAHeader] = None
    body: Optional[CTABody] = None
    footer: Optional[CTAFooter] = None
    action: CTAction


class CTAUrlButtonMessage(WhatsAppRequestTo):
    type_: Literal["interactive"] = Field("interactive", alias="type")
    interactive: Optional[ICTAUrlObject] = None

    def complete(
        self,
        display_text: str,
        url: str,
        header: str = None,
        body: str = None,
        footer: str = None,
    ):
        header_object = CTAHeader(text=header) if header else None
        body_object = CTABody(text=body) if body else None
        footer_object = CTAFooter(text=footer) if footer else None
        cta_parameters = CTAParameters(display_text=display_text, url=url)
        cta_action_object = CTAction(parameters=cta_parameters)

        self.interactive = ICTAUrlObject(
            header=header_object,
            body=body_object,
            footer=footer_object,
            action=cta_action_object,
        )
        return self
