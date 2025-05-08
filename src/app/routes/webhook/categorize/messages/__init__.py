"""Module containing all Possible Messages Types and
there respective functions."""

from typing import Union

from app.routes.webhook.categorize.messages.text import TextMessage
from app.routes.webhook.categorize.messages.button import ButtonMessageMessage
from app.routes.webhook.categorize.messages.list import ListMessageMessage
from app.routes.webhook.categorize.messages.callback import CallBackButtonMessage
from app.routes.webhook.categorize.messages.image import ImageMessage
from app.routes.webhook.categorize.messages.video import VideoMessage
from app.routes.webhook.categorize.messages.audio import AudioMessage
from app.routes.webhook.categorize.messages.contact import ContactMessage
from app.routes.webhook.categorize.messages.sticker import StickerMessage
from app.routes.webhook.categorize.messages.reaction import ReactionMessage
from app.routes.webhook.categorize.messages.location import LocationMessage
from app.routes.webhook.categorize.messages.adds import AidsMessage
from app.routes.webhook.categorize.messages.unsuported import UnsupportedMessage
from app.routes.webhook.categorize.messages.unknown import UnknownMessage


Message = Union[
    TextMessage,
    ButtonMessageMessage,
    ListMessageMessage,
    CallBackButtonMessage,
    ImageMessage,
    VideoMessage,
    AudioMessage,
    ContactMessage,
    StickerMessage,
    ReactionMessage,
    LocationMessage,
    AidsMessage,
    UnsupportedMessage,
    UnknownMessage,
]
