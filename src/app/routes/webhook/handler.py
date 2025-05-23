"""Module responsible for running on background everytime a payload is called"""

from logging import getLogger
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.scripiter import ScriptBaseModel
from app.scripiter.models import registery
from app.data_base.db_helper.crud import get_or_create_user
from app.routes.webhook.models.payload import WebHookPayload

log = getLogger(__name__)


async def handle_payload(
    payload: WebHookPayload,
    db_session: AsyncSession,
    client_session: ClientSession,
):
    """Function resposible for assigning an activity
    for each type of payload
    """

    value = (
        payload.entry[0].changes[0].value
    )  # We are only checking the first of each, i dont think we will recieve more complex payloads.

    if (
        not hasattr(value, "contacts") or not value.contacts
    ):  # This means our payload has nobody to send back to...
        # There are interesting cases here, but i cant care for that now
        return  # We just return, nothing interesting to do.

    if not hasattr(
        value, "messages"
    ):  # For now i am only interested if i get a message from an user
        return  # Returns, nothing interesting to do.

    contact = value.contacts[
        0
    ]  # Again only interested on the first, havent seen different types.

    wa_id = contact.wa_id  # User unique WhatsApp ID
    name = (
        contact.profile.name
    )  # User name registered on WhatsApp, WARNING: non UTF-8 character will break things

    user = await get_or_create_user(
        async_session=db_session, wa_id=wa_id, formatted_name=name
    )  # NOTE: I did not test this function;

    current_step = user.current_step  # Points to the user action.

    handler_cls = registery.get(
        current_step
    )  # Looks on the resgitery for the next action.

    if handler_cls:
        handler: ScriptBaseModel = handler_cls(
            db_session=db_session,
            client_session=client_session,
            registery=registery,
            payload_value=value,
        )

        await handler.handle()
