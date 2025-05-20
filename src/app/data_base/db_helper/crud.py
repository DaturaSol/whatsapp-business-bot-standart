"""File responsible for carrying important functions related to the data base.

An example would be adding users
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.data_base.models.user import User
from app.data_base.models.convo import Convo

log = logging.getLogger(__name__)


async def create_user(
    async_session: AsyncSession, wa_id: str, formatted_name: str | None = None
) -> User:
    """Adds an user to the data Base"""
    try:
        log.info("New user added")
        new_user = User(wa_id=wa_id, formatted_name=formatted_name)

        async_session.add(new_user)
        return new_user

    except Exception as e:
        log.exception(f"{e}")
        raise e


async def get_user(
    async_session: AsyncSession,
    wa_id: str,
) -> User | None:
    try:
        result = await async_session.execute(select(User).where(User.wa_id == wa_id))  # type: ignore
        # Pylance will throw some stupid erro about the type of wa_id, i dont have patieince for this now
        return result.scalar_one_or_none()
    except Exception as e:
        logging.exception(f"Error \n{e}")
        raise


async def get_or_create_user(
    async_session: AsyncSession, wa_id: str, formatted_name: str | None = None
) -> User:
    try:
        p_user = await get_user(async_session=async_session, wa_id=wa_id)
        if not p_user:
            p_user = await create_user(
                async_session=async_session, wa_id=wa_id, formatted_name=formatted_name
            )
        return p_user
    except Exception as e:
        raise


async def add_convo(
    async_session: AsyncSession,
    whatsapp_message_id: str,
    wa_id: str,
    timestamp: datetime,
    messages: dict,
    past_message: str | None = None,
) -> Convo:
    """Adds a converssation to an already logged used"""
    try:
        log.info("New convo Added")
        new_convo = Convo(
            whatsapp_message_id=whatsapp_message_id,
            wa_id=wa_id,
            timestamp=timestamp,
            messages=messages,
            past_message=past_message,
        )

        async_session.add(new_convo)
        return new_convo
    except Exception as e:
        log.exception(f"{e}")
        raise e
