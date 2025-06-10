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

unasus_bp = ScriptBlueprint()


@unasus_bp.register()
class UnaSusMenu(ScriptBaseModel):
    """Menu for UnaSUS content also refered as PNSPIPN,
    here users can choose between chapeters and exercises on this 
    content."""
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Módulo"
        body = (
            "Política Nacional de Saúde Integral da População (PNSIPN) 📖\n\n"
            
            "Olá! Bem-vindo(a) ao módulo sobre a Política Nacional de Saúde " 
            "Integral da População (PNSIPN). 🌟\n\n" 
            
            "Aqui, vamos explorar o conteúdo detalhado referente a esta importante "
            "política, cuidadosamente elaborado pelo Professor Hilton P. Silva.\n\n"
            
            "Neste espaço, você poderá escolher como deseja interagir com o material:\n"
            
            "1. *Explorar os Capítulos* 📚:\n"
            "Navegue pelo conteúdo de forma progressiva, lendo cada seção para um aprendizado completo e sequencial.\n\n"
            
            "2. *Praticar com Exercícios* ✍️:\n"
            "Teste seus conhecimentos respondendo a perguntas sobre os temas abordados. " 
            "Você pode fazer os exercícios conforme avança nos capítulos ou quando se sentir pronto(a) para revisar.\n\n"
            
            "O que você gostaria de fazer primeiro? Acessar os Capítulos ou ir para os Exercícios? 😊"
        )
        options = {
            "title": "Menu",
            "rows": [
                {"title": "Capítulos", "id": UnaSusChapterMenu.__name__},
                {"title": "Exercícios", "id": IntroMenuExercises.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Opções", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()
        
# --- Chapters --- 
@unasus_bp.register()
class UnaSusChapterMenu(ScriptBaseModel):
    """Menu conteining all chapters for UnaSus content on 
    Política Nacional de Saúde Integral da População"""
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Módulo"
        body = (
            "Política Nacional de Saúde Integral da População (PNSIPN) 📖\n\n"
            
            "Olá! Bem-vindo(a) ao módulo sobre a Política Nacional de Saúde " 
            "Integral da População (PNSIPN). 🌟\n\n" 
            
            "Aqui, vamos explorar o conteúdo detalhado referente a esta importante "
            "política, cuidadosamente elaborado pelo Professor Hilton P. Silva.\n\n"
            
            "Neste espaço, você poderá escolher como deseja interagir com o material:\n"
            
            "1. *Explorar os Capítulos* 📚:\n"
            "Navegue pelo conteúdo de forma progressiva, lendo cada seção para um aprendizado completo e sequencial.\n\n"
            
            "2. *Praticar com Exercícios* ✍️:\n"
            "Teste seus conhecimentos respondendo a perguntas sobre os temas abordados. " 
            "Você pode fazer os exercícios conforme avança nos capítulos ou quando se sentir pronto(a) para revisar.\n\n"
            
            "O que você gostaria de fazer primeiro? Acessar os Capítulos ou ir para os Exercícios? 😊"
        )
        options = {
            "title": "Menu",
            "rows": [
                {"title": "Capítulos", "id": IntroMenuChapters.__name__},
                {"title": "Exercícios", "id": IntroMenuExercises.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Opções", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()