"""File responsible for carrying important functions related to the data base.

An example would be adding users
"""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.data_base.models.user import User
from app.data_base.models.convo import Convo

log = logging.getLogger(__name__)


async def create_user(
    async_session: AsyncSession,
    wa_id: str,
    formatted_name: str = None,
    company: str = None,
    department: str = None,
    title: str = None,
    email: str = None,
    birthday: datetime = None,
    summary: str = None,
) -> User:
    """Adds an user to the data Base"""
    try:
        log.info("New user added")
        new_user = User(
            wa_id=wa_id,
            formatted_name=formatted_name,
            company=company,
            department=department,
            title=title,
            email=email,
            birthday=birthday,
            summary=summary,
        )

        async_session.add(new_user)
        return new_user
    
    except Exception as e:
        log.exception(f"{e}")
        raise e


async def add_convo(
    async_session: AsyncSession,
    whatsapp_message_id: str,
    wa_id: str,
    timestamp: datetime,
    messages: dict,
    past_message: str = None,
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
