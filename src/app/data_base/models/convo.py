"""Model for Convo Table Structure

**Important!**:
Avoid changing this Structure.
Implement other Tables as you wish, but this
will be used as defined here along the program.
"""

from app.data_base.models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Index
from datetime import datetime
from sqlalchemy.orm import relationship


class Convo(Base):
    """This class contains message informations between user
    and bot

    Args:
    ---
    ```
        'whatsapp_message_id' (str): 'Unique identifier from meta for each message'
        'wa_id' (str): 'Unique identifier from meta for each person'
        'timestamp' (datetime): 'timestamp of the message'
        'messages' (str): 'A dict containing the type of content given'
        'past_message' (str, optional): 'Past message sent by the bot.'None
    ```
    """

    __tablename__ = "convo"

    whatsapp_message_id = Column(Integer, primary_key=True)
    wa_id = Column(
        String, ForeignKey("users.wa_id"), unique=True, nullable=False, index=True
    )
    timestamp = Column(DateTime, nullable=False, index=True)
    messages = Column(JSON, nullable=False)
    past_message = Column(String)

    user = relationship("User", back_populates="user_convos")

    __table_args__ = (Index("ix_convos_user_wa_id_timestamp", "wa_id", "timestamp"),)

    def __init__(
        self,
        whatsapp_message_id: str,
        wa_id: str,
        timestamp: datetime,
        messages: dict,
        past_message: str = None,
    ):
        self.whatsapp_message_id = whatsapp_message_id
        self.wa_id = wa_id
        self.timestamp = timestamp
        self.messages = messages
        self.past_message = past_message
