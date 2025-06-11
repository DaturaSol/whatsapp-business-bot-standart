import json
from logging import getLogger
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.data_base.db_helper.crud import get_user
from app.scripiter import ScriptBlueprint, ScriptBaseModel, ScripterDocName
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

redirecter_bp = ScriptBlueprint()
redirecter_doc = ScripterDocName()

@redirecter_doc.register()
@redirecter_bp.register()
class Redirecter(ScriptBaseModel):
    """Depending on the payload type, the redirecter will send the user
    to there proper destination, text messages, which are not accounted, will
    be redirected to the ai from this point too."""
    async def _fn(self):
        self.jump = True
        
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        # --- Logic -- 
        if isinstance(message, ButtonMessageMessage):
            self.next = message.interactive.button_reply.id

        if isinstance(message, ListMessageMessage):
            self.next = message.interactive.list_reply.id
            
        if isinstance(message, NfmReplyMessage):
            await self.handle_nfm_reply(message, contact)
            
        if isinstance(message, TextMessageWeb):
            message_body = message.text.body
            match message_body:
                case "/Painel":
                    self.next = "UserMenu"
                case "/PNSPIPN":
                    self.next = "UnaSusMenu"
                case "/Info":
                    self.next = "InfoMenu"
                case _:
                    self.next = "AIResponse"
            
    async def handle_nfm_reply(self, message: NfmReplyMessage, contact: Contact):
        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        wa_id = contact.wa_id
        flow_token = response_json.get("flow_token")
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        
        match flow_token:
            case "FirstInfo":
                self.next = "IntroCompled"
                log.info(f"Introduction completed for [User: {wa_id}]")
                user.formatted_name = response_json.get("Nome")
                user.gender = response_json.get("Genero")
                user.last_name = response_json.get("Sobrenome")
                user.email = response_json.get("Email")
                user.birthday = response_json.get("Aniversario")
                user.summary = response_json.get("SobreVoce")
                await self.db_session.commit()  # Commits to be used in the next call
                
            case "InfoMenu":
                self.next = "AllDone"
                log.info(f"Introduction completed for [User: {wa_id}]")
                user.formatted_name = response_json.get("Nome")
                user.gender = response_json.get("Genero")
                user.last_name = response_json.get("Sobrenome")
                user.email = response_json.get("Email")
                user.birthday = response_json.get("Aniversario")
                user.summary = response_json.get("SobreVoce")
                await self.db_session.commit()  # Commits to be used in the next call
                
            case "UnaSusChapterOne":
                self.next = "UnaSusChapterOneContent"
            
            case "UnaSusChapterTwo":
                self.next = "UnaSusChapterTwoContent"
                
            case "UnaSusChapterThree":
                self.next = "UnaSusChapterThreeContent"
            
            case "UnaSusChapterFour":
                self.next = "UnaSusChapterFourContent"
            
            case "UnaSusChapterFive":
                self.next = "UnaSusChapterFiveContent"
                
            case "UnaSusExerciseOne":
                self.next = "UnaSusExerciseOneHandle"
            
            case "UnaSusExerciseTwo":
                self.next = "UnaSusExerciseTwoHandle"
                
            case "UnaSusExerciseThree":
                self.next = "UnaSusExerciseThreeHandle"
                
            case "UnaSusExerciseFour":
                self.next = "UnaSusExerciseFourHandle"
                
            case "UnaSusExerciseFive":
                self.next = "UnaSusExerciseFiveHandle"
            
            case "UnaSusBib":
                self.next = "UnaSusBibHandle"