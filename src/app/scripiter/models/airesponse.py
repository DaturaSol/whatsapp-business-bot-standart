import json
from logging import getLogger
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.data_base.db_helper.crud import get_user
from app.scripiter import ScriptBlueprint, ScriptBaseModel
from app.client_session.services.genai import get_ai_response

# --- WebHook ---
from app.routes.webhook.models.contacts import Contact
from app.routes.webhook.models.messages.list import ListMessageMessage
from app.routes.webhook.models.messages.nfm_reply import NfmReplyMessage
from app.routes.webhook.models.messages.button import ButtonMessageMessage
from app.routes.webhook.models.messages.text import TextMessage as TextMessageWeb

# -- Client Session ---
from app.client_session.messages.models.text import TextMessage
from app.client_session.messages.models.template import TemplateMessage
from app.client_session.messages.models.interactive_list import InteractiveListMessage
from app.client_session.messages.models.button import InteractiveButtonMessage


log = getLogger(__name__)

airesponse_bp = ScriptBlueprint()

@airesponse_bp.register()
class AIResponse(ScriptBaseModel):
    async def _fn(self):
        return await super()._fn()