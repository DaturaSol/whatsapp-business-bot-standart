"""Module contaning information on the scripter class.
Every script must inherit this class.
"""

from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger
from typing import Type

from app.routes.webhook.models.payload import Value
from app.routes.webhook.models.messages import Message

log = getLogger(__name__)


class ScriptBaseModel:
    """Abstract Class responsible for running
    scripts
    ---
    Atr:
    ---
        self.db_session (AsyncSession):
            Asynchronous Session to work with the Data Base
        self.client_session (ClientSession):
            Asynchronous Session to work with Requests
        self.value (Value):
            Payload Infomation
        self.next (ScriptBaseModel):
            Next class that the script should point to
        self.jump (bool):
            If the script should jump to the next entrance, without waiting for
            a payload.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        client_session: ClientSession,
        registery: dict[str, Type["ScriptBaseModel"]],
        payload_value: Value,
    ):
        self.db_session = db_session
        self.client_session = client_session
        self.registery = registery
        self.value = payload_value

        # Reference nodes
        self.next: str | None = None  # This points to the next class to be executed
        self.jump: bool = (
            False  # This tells if a webhook is necessary to excute the next script
        )

    async def _fn(self):
        """This function will do most of the script work, send messages,
        do data Base stuff etc etc"""
        raise NotImplementedError

    async def handle(self):
        """Function resposible to check if subclass has atribute `_fn` and executing it"""
        try:
            await self._fn()
        except NotImplementedError as e:
            raise e  # TODO: Implement a better handle for this.

        if self.jump and self.next:  # Should execute another class?
            handler_cls = self.registery.get(
                self.next  # Next step we defined inside the class
            )  # Fecthes the next class to be executed
            if handler_cls:
                next_cls = handler_cls(
                    db_session=self.db_session,
                    client_session=self.client_session,
                    registery=self.registery,
                    payload_value=self.value,
                )  # Pass the same information for the next action

                await next_cls.handle()


class ScriptBlueprint:
    """Class responsible for storing different scripts"""

    def __init__(self) -> None:
        self._register_classes = {}

    def register(self):
        """Register a function inside a dictionary"""

        def wrapper(cls):
            name = cls.__name__
            if name in self._register_classes:
                raise ValueError(
                    f"Class with name '{name}' already registered in blueprint."
                )
            self._register_classes[name] = cls
            return cls

        return wrapper

    def get_registery(self):
        return self._register_classes
