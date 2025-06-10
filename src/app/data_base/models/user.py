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
    gender = Column(String)
    company = Column(String)
    department = Column(String)
    title = Column(String)
    email = Column(String)
    birthday = Column(String)
    summary = Column(String)
    current_step = Column(String, default="HelloUser")
    past_question = Column(String)
    # Best would be to add these to a new class, but i am short on time
    # Una Sus
    current_chapter_una = Column(String, default="ChapterOne")
    current_exercise_una = Column(String, default="ExerciseOne")
    exercise_grade_una = Column(JSON, default={"E1": 0, "E2": 0, "E3": 0, "E4": 0})
    chapter_grade_una = Column(JSON, default={"C1": 0, "C2": 0, "C3": 0, "C4": 0})
    # Conto Ngerinha
    current_chapter_other = Column(String, default="ChapterOne")
    current_exercise_other = Column(String, default="ExerciseOne")
    exercise_grade_other = Column(JSON, default={"E1": 0, "E2": 0, "E3": 0, "E4": 0})
    chapter_grade_other = Column(JSON, default={"C1": 0, "C2": 0, "C3": 0, "C4": 0})

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
        gender: str | None = None,
        email: str | None = None,
        birthday: str | None = None,
        summary: str | None = None,
        current_step: str = "HelloUser",
        past_question: str | None = None,
        current_chapter_una: str ="ChapterOne",
        current_exercise_una: str ="ExerciseOne",
        exercise_grade_una: dict ={"E1": 0, "E2": 0, "E3": 0, "E4": 0},
        chapter_grade_una: dict = {"C1": 0, "C2": 0, "C3": 0, "C4": 0},
        current_chapter_other: str = "ChapterOne",
        current_exercise_other: str = "ExerciseOne",
        exercise_grade_other: dict = {"E1": 0, "E2": 0, "E3": 0, "E4": 0},
        chapter_grade_other: dict = {"C1": 0, "C2": 0, "C3": 0, "C4": 0},
    ):
        self.wa_id = wa_id
        self.formatted_name = formatted_name
        self.last_name = last_name
        self.company = company
        self.department = department
        self.title = title
        self.gender = gender
        self.email = email
        self.birthday = birthday
        self.summary = summary
        self.current_step = current_step
        self.past_question = past_question
        self.current_chapter_una = current_chapter_una
        self.current_exercise_una = current_exercise_una
        self.exercise_grade_una = exercise_grade_una
        self.chapter_grade_una = chapter_grade_una
        self.current_chapter_other = current_chapter_other
        self.current_exercise_other = current_exercise_other
        self.exercise_grade_other = exercise_grade_other
        self.chapter_grade_other = chapter_grade_other
        
