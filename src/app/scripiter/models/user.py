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

# --- Client Session ---
from app.client_session.messages.models.text import TextMessage
from app.client_session.messages.models.template import TemplateMessage
from app.client_session.messages.models.interactive_list import InteractiveListMessage
from app.client_session.messages.models.button import InteractiveButtonMessage

log = getLogger(__name__)

user_bp = ScriptBlueprint()

@user_bp.register()
class UserMenu(ScriptBaseModel):
    """User Main menu also Known as Painel de Controle, here they can choose
    the subject they want to study."""
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Painel de Controle"
        body = (
            "Bem-vindo(a) ao seu Painel de Controle! 🚀\n\n"
            
            "Este é o seu centro de comando." 
            "A partir daqui, você pode navegar pelas diferentes "
            "funcionalidades e configurações que tenho disponíveis no momento.\n\n"
            
            "Explore as opções para personalizar sua experiência, "
            "acessar módulos de estudo ou gerenciar suas preferências.\n" 
            "Estou aqui para ajudar! 😊"
        )
        options = {
            "title": "Menu",
            "rows": [
                {"title": "Informações Pessoais", "id": InfoMenu.__name__},
                {"title": "PNSPIPN", "id": "UnaSusMenu", "description": "Autor: Hilton P. Silva"},
                # {"title": "Conto Negrinha", "id": , "description": "Autor: Monteiro Lobato"},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Ver", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


@user_bp.register()
class InfoMenu(ScriptBaseModel):
    """Also known as Informações Pessoais, here the user can alter
    what i known about them, change there name, gender and other 
    user personal specific relations"""
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        
        flow_action_data = {
            "Nome": user.formatted_name,
            "Sobrenome": user.last_name,
            "Genero": user.gender,
            "Email": user.email,
            "Aniversario": user.birthday,
            "SobreVoce": user.summary,
        }
        
        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_info_menu",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_action_data_payload=flow_action_data,
            flow_token=self.__class__.__name__
        )
        
        await message.send(self.client_session)
        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()
        
        
@user_bp.register()
class AllDone(ScriptBaseModel):
    """Tells User that there message was properly recieved."""
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        
        message_content = "Maravilha! ✨ Recebi seus dados atualizados e parece que está tudo certinho por aqui. 👍"
        
        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)
        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()