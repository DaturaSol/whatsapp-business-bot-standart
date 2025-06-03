"""Model for User Table Structure

**Important!**:
Avoid changing this Structure.
Implement other Tables as you wish, but this
will be used as defined here along the program.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
# from datetime import datetime

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
    last_name = Column(String)
    company = Column(String)
    department = Column(String)
    title = Column(String)
    email = Column(String)
    birthday = Column(String)
    summary = Column(String)
    current_step = Column(String, default="HelloUser")
    # Best would be to add these to a new class, but i am short on time
    current_chapter = Column(String, default="ChapterOne")
    current_exercise = Column(String, default="ExerciseOne")
    exercise_grade = Column(JSON, default={"E1": 0, "E2": 0, "E3": 0, "E4": 0})
    chapter_grade = Column(JSON, default={"C1": 0, "C2": 0, "C3": 0, "C4": 0})
    past_question = Column(String)

    user_convos = relationship(
        "Convo",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(Convo.timestamp)",
    )

    def __init__(
        self,
        wa_id: str,
        formatted_name: str | None = None,
        last_name: str | None = None,
        company: str | None = None,
        department: str | None = None,
        title: str | None = None,
        email: str | None = None,
        birthday: str | None = None,
        summary: str | None = None,
        current_step: str = "HelloUser",
        current_chapter: str = "ChapterOne",
        current_exercise: str = "ExerciseOne",
        exercise_grade: dict  = {"E1": "❎", "E2": "❎", "E3": "❎", "E4": "❎"},
        chapter_grade: dict  = {"C1": "❎", "C2": "❎", "C3": "❎", "C4": "❎"},
        past_question: str | None = None
    ):
        self.wa_id = wa_id
        self.formatted_name = formatted_name
        self.last_name = last_name
        self.company = company
        self.department = department
        self.title = title
        self.email = email
        self.birthday = birthday
        self.summary = summary
        self.current_step = current_step
        self.current_chapter = current_chapter
        self.current_exercise = current_exercise
        self.exercise_grade = exercise_grade
        self.chapter_grade = chapter_grade
        self.past_question = past_question
