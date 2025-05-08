"""Base model for sending Requests to the WhatsApp Bussines API"""

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict
from aiohttp import ClientSession, ClientError, ContentTypeError
from asyncio import TimeoutError
import logging

from app.settings import Settings

log = logging.getLogger(__name__)

settings = Settings()

ACCESS_TOKEN = settings.access_token
API_VERSION = settings.api_version
PHONE_NUMBER_ID = settings.phone_number_id


class WhatsAppRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    messaging_product: Literal["whatsapp"] = "whatsapp"

    async def send(
        self,
        client_session: ClientSession,
        timeout: float = 10.0,
    ) -> None:
        """
        Serializes the model into JSON (with the right field names),
        POSTs it to Graph.
        """
        url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }

        # Build the exact dict shape the API expects
        payload = self.model_dump(exclude_none=True, by_alias=True)

        try:
            async with client_session.post(
                url, json=payload, headers=headers, timeout=timeout
            ) as resp:
                data = await resp.json()
                if resp.status >= 400 or "error" in data:
                    err = data.get("error", {}).get("message", data)
                    log.error(f"[WhatsApp] Error sending message: {err}")

        except ContentTypeError:
            log.exception(f"Invalid JSON received")
        except ClientError as e:
            log.exception(f"ClientError: {e}")
            raise
        except TimeoutError:
            log.exception("Timeout")
            raise
        except Exception as e:
            log.exception(e)
            raise


class Context(BaseModel):
    message_id: str


class WhatsAppRequestTo(WhatsAppRequest):
    recipient_type: Literal["individual"] = "individual"
    to: str
    context: Optional[Context] = None
