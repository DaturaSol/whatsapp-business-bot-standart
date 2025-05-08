from pydantic import BaseModel
from typing import List, Optional

from app.routes.webhook.categorize.messages.base import  BaseMessageModel

class NameContactObject(BaseModel):
    formatted_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    prefix: Optional[str] = None


class AddressContactObject(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    state: Optional[str] = None
    street: Optional[str] = None
    type: Optional[str] = None
    zip: Optional[str] = None


class EmailContactObject(BaseModel):
    email: str
    type: Optional[str] = None


class OrgContactObject(BaseModel):
    company: str
    department: Optional[str] = None
    title: Optional[str] = None


class PhoneContactObject(BaseModel):
    phone: str
    wa_id: Optional[str] = None
    type: Optional[str] = None


class UrlsContactObject(BaseModel):
    url: str
    type: Optional[str] = None


class ContactObject(BaseModel):
    name: NameContactObject
    addresses: Optional[List[AddressContactObject]] = None
    emails: Optional[List[EmailContactObject]] = None
    org: Optional[OrgContactObject] = None
    phones: Optional[List[PhoneContactObject]] = None
    urls: Optional[List[UrlsContactObject]] = None
    birthday: Optional[str] = None


class ContactMessage(BaseMessageModel):
    contacts: List[ContactObject]