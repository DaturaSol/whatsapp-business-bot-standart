"""Model for User Table Structure

**Important!**:
Avoid changing this Structure.
Implement other Tables as you wish, but this
will be used as defined here along the program.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.data_base.models.base import Base

class User(Base):
    """This class is thought on top of WhatsApp Business API
    Contact info.

    Args:
    ---
    ```
        'wa_id' (str): 'Unique identifier from WhatsApp'
        'formatted_name' (str, optional): 'Complete user name.' None
        'company' (str, optional): 'Place where user uses the bot.' None
        'department' (str, optional): 'Maybe user course.' None
        'title' (str, optional): 'The role.' None
        'email' (str, optional): 'User email.' None
        'birthday' (datetime, optional): 'User birthday.' None
        'summary' (str, optional): 'A quick resume from past conversations.'  None
    ```

    Contact Info Structure:
    ---
    ```
    {
        'name': {
            'formated_name': (str),
            'first_name': (str),
            'last_name': (str)
        },
        'phone': [{
            'phone': (str),
            'wa_id': (str)
        }],
        'org': {
            'company': (str),
            'department': (str),
            'title': (str),
        },
        'birthday': (datetime),
        'emails': [{
            'email': (str)
            'type': (str)
        }]
    }
    ```
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wa_id = Column(String, nullable=False, unique=True, index=True)
    formatted_name = Column(String)
    company = Column(String)
    department = Column(String)
    title = Column(String)
    email = Column(String)
    birthday = Column(DateTime)
    summary = Column(String)

    user_convos = relationship(
        "Convo",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(Convo.timestamp)",
    )

    def __init__(
        self,
        wa_id: str,
        formatted_name: str = None,
        company: str = None,
        department: str = None,
        title: str = None,
        email: str = None,
        birthday: datetime = None,
        summary: str = None,
    ):
        self.wa_id = wa_id
        self.formatted_name = formatted_name
        self.company = company
        self.department = department
        self.title = title
        self.email = email
        self.birthday = birthday
        self.summary = summary
