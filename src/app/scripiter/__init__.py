"""Module contaning information on the scripter class.
Every script must inherit this class.
"""

from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger
from typing import Type

log = getLogger(__name__)


class ScriptBaseModel:
    """Abstract Class responsible for running
    scripts"""

    def __init__(
        self,
        db_session: AsyncSession,
        client_session: ClientSession,
        registery: dict[str, Type["ScriptBaseModel"]],
    ):

        self.db_session = db_session
        self.client_session = client_session
        self.registery = registery
        # Reference nodes
        self.next: str | None = None  # This points to the next class to be executed
        self.jump: bool = (
            False  # This tells if a webhook is necessary to excute the next script
        )
        self.expected_type: list[str | None] = (
            []
        )  # Name of the WebHookPayload Types that are expected 

    async def _fn(self, payload): # TODO
        """This function will do most of the script work, send messages,
        do data Base stuff etc etc"""
        raise NotImplementedError

    async def handle(self, payload): # TODO: No typehint, bad code. will Arise in circular imports.
        """Function resposible to check if subclass has atribute `_fn` and executing it"""
        try:
            await self._fn(payload)
        except NotImplementedError as e:
            raise e  # TODO: Implement a better handle for this.

        if self.jump and self.next:  # Should execute another class?
            handler_cls = self.registery.get(
                self.next
            )  # Fecthes the next class to be executed
            if handler_cls:
                next_cls = handler_cls(
                    db_session=self.db_session,
                    client_session=self.client_session,
                    registery=self.registery,
                )

                await next_cls.handle(payload)


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
