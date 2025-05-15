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
    first_name: str
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

    def add_address_to(self, idx: int):
        pass

    def add_email_to(self, idx: int):
        pass

    def add_birthday_to(self, idx: int):
        pass

    def add_phone_to(self, idx: int):
        pass

    def add_org_to(self, idx: int):
        pass

    def add_url_to(self, idx: int):
        pass


class ContactsMessage(WhatsAppRequestTo):
    type_: Literal["contacts"] = Field("contacts", alias="type")
    contacts: List[ContactObject] = []

    def __init__(
        self,
        *,
        to: str,
        formatted_name: str,
        first_name: str,
        last_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        suffix: Optional[str] = None,
        prefix: Optional[str] = None,
        **kwagrs,
    ):
        name_paylaod = NameObject(
            formatted_name=formatted_name,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            suffix=suffix,
            prefix=prefix,
        )

        contact_paylaod = ContactObject(name=name_paylaod)

        init_data = kwagrs.copy()
        init_data["to"] = to
        init_data["contacts"] = [contact_paylaod]

        super().__init__(**init_data)

    def append_contact(self):
        pass
