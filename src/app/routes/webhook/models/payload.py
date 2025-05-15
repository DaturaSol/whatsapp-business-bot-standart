"""Module containing the basic format every WebHook Payload should have
# [**Oficial Documentation**](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks)
## Example of basic payload structure?
```json
{
   "object": "whatsapp_business_account",
   "entry": [
       {
           "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
           "changes": [
               {
                   "value": {
                       "messaging_product": "whatsapp",
                       "metadata": {
                           "display_phone_number": "PHONE_NUMBER",
                           "phone_number_id": "PHONE_NUMBER_ID"
                       },
               # specific Webhooks payload
                   },
                   "field": "messages"
               }
           ]
       }
   ]
}
```
"""

from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.routes.webhook.models.messages import Message
from app.routes.webhook.models.statuses import Status
from app.routes.webhook.models.contacts import Contact


class MetaData(BaseModel):
    display_phone_number: str
    phone_number_id: str


class Value(BaseModel):
    messaging_product: Literal["whatsapp"]
    metadata: MetaData
    contacts: Optional[List[Contact]] | None = None
    messages: Optional[List[Message]] | None = None
    statuses: Optional[List[Status]] | None = None

    async def handle(self, db_session: AsyncSession, client_session: ClientSession):
        """Depending on the value Type
        proceeds to the correct task"""
        if self.messages:
            await self.messages[0].handle(
                contacts=self.contacts,
                db_session=db_session,
                client_session=client_session,
            )
        elif self.statuses:
            await self.statuses[0].handle()
        else:
            raise ValueError("Unknown payload type")


class Change(BaseModel):
    value: Value
    field: Literal["messages"]


class Entry(BaseModel):
    id: str
    changes: List[Change]


class WebHookPayload(BaseModel):
    object_: Literal["whatsapp_business_account"] = Field(..., alias="object")
    entry: List[Entry]

    async def handle(self, db_session: AsyncSession, client_session: ClientSession):
        """Assigns which taks should be done depending
        on what the payload is composed of."""
        await self.entry[0].changes[0].value.handle(
            db_session=db_session, client_session=client_session
        )
