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

welcome_bp = ScriptBlueprint()

@welcome_bp.register()
class WellComeUser(ScriptBaseModel):
    """First Message the User sees when speaking with the bot, 
    the user should not be redirect to this."""
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        
        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_hello",
            has_static_header=True,
            has_flow_button=False,
        )
        
        await message.send(self.client_session)
        self.next = FirstInfo.__name__
        user.current_step = self.next
        await self.db_session.commit()


@welcome_bp.register()
class FirstInfo(ScriptBaseModel):
    """Next messasge after, wellcome user, user should not be redirected here"""
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
            "Nome": contatc.profile.name,
            "Sobrenome": "",
            "Genero": "",
            "Email": "",
            "Aniversario": "",
            "SobreVoce": "",
        }
        
        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_first_info",
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


@welcome_bp.register()
class IntroCompled(ScriptBaseModel):
    """Checkpoint that the intro was completed"""
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        
        message_content = (
            f"Perfeito, {user.formatted_name}! 🎉 Completamos nossa introdução inicial com sucesso!\n\n"
            
            "Agora, vou te apresentar melhor como funciona a minha interface, " 
            "para que você possa navegar com facilidade. Olha só como é simples:\n\n"
            
            "- *Comando Mágico* /:\n" 
            "Você pode explorar minhas opções de forma rápida digitando / (barra). " 
            "Ao fazer isso, um menu aparecerá com atalhos para diferentes seções e configurações. " 
            "Assim, você pode acessar o que precisa de maneira bem prática! 🛠️\n\n"
            
            "- *Conversa Inteligente*:\n" 
            "Além dos comandos, sinta-se à vontade para me pedir para ir a um "
            "capítulo específico, buscar uma referência ou tópico. " 
            "Farei o meu melhor para entender e te levar aonde você precisa! 🧠🔎\n\n"
            
            "Pronto(a) para começar a explorar o conteúdo?\n" 
            "Vou te redirecionar agora para o Menu Principal. Lá, você poderá escolher o que deseja estudar."
        )
        
        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)
        self.jump = True
        self.next = "UserMenu"
        