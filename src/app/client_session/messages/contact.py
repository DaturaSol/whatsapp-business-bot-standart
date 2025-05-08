"""Module Containing ContactMessage Structure and Functions"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, List

from app.client_session.messages.base import WhatsAppRequestTo


class UrlObject(BaseModel):
    url: str
    type_: Optional[str] = Field(..., alias="type")


class PhoneObject(BaseModel):
    phone: str
    type_: Optional[str] = Field(None, alias="type")
    wa_id: Optional[str] = None


class OrgObject(BaseModel):
    company: Optional[str] = None
    departament: Optional[str] = None
    title: Optional[str] = None


class NameObject(BaseModel):
    formatted_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    prefix: Optional[str] = None


class EmailObject(BaseModel):
    email: str
    type_: Optional[str] = Field(None, alias="type")


class AddressObject(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_: Optional[str] = Field(None, alias="zip")
    country: Optional[str] = None
    country_code: Optional[str] = None
    type_: Optional[str] = Field(None, alias="type")


class ContactObject(BaseModel):
    addresses: Optional[List[AddressObject]] = None
    birthday: Optional[str] = None
    emails: Optional[List[EmailObject]] = None
    name: NameObject
    org: Optional[OrgObject] = None
    phones: Optional[List[PhoneObject]] = None
    urls: Optional[List[UrlObject]] = None


class ContactsMessage(WhatsAppRequestTo):
    type_: Literal["contacts"] = Field("contacts", alias="type")
    contatcs: List[ContactObject]
