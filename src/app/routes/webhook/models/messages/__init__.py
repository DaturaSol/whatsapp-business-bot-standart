"""Module containing all Possible Messages Types and
there respective functions."""

from typing import Union

from app.routes.webhook.models.messages.text import TextMessage
from app.routes.webhook.models.messages.button import ButtonMessageMessage
from app.routes.webhook.models.messages.list import ListMessageMessage
from app.routes.webhook.models.messages.callback import CallBackButtonMessage
from app.routes.webhook.models.messages.image import ImageMessage
from app.routes.webhook.models.messages.video import VideoMessage
from app.routes.webhook.models.messages.audio import AudioMessage
from app.routes.webhook.models.messages.contact import ContactMessage
from app.routes.webhook.models.messages.sticker import StickerMessage
from app.routes.webhook.models.messages.reaction import ReactionMessage
from app.routes.webhook.models.messages.location import LocationMessage
from app.routes.webhook.models.messages.adds import AidsMessage
from app.routes.webhook.models.messages.unsuported import UnsupportedMessage
from app.routes.webhook.models.messages.unknown import UnknownMessage
from app.routes.webhook.models.messages.nfm_reply import NfmReplyMessage

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
    NfmReplyMessage,
]
