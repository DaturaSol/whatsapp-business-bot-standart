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

# --- Redirecters ---
from app.scripiter.models.user import user_docs
from app.scripiter.models.redirecter import redirecter_doc
from app.scripiter.models.unasus import unasus_doc


log = getLogger(__name__)

airesponse_bp = ScriptBlueprint()

redirecters = redirecter_doc.get_registery() + user_docs.get_registery() + unasus_doc.get_registery()

@airesponse_bp.register()
class AIResponse(ScriptBaseModel):
    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]

        if not isinstance(message, TextMessageWeb):
            return

        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id

        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        contact = contatcs[0]

        message_content = message.text.body

        prompt_response = {
            "Instructions": (
                "Você é um bot do WhatsApp para a empresa Estum. "
                "Seu proposito, hoje é servir como demonstração viavel, de como "
                "o ensino a distancia pode ser facil pelo whatsApp."
                "Por hora você não tem muito acesso ao conteudo, disponibilizado "
                "mas isto não é um problema, ja que o conteudo foi feito por professores "
                "e todas as respostas estão presentes aqui, seu papel é apenas "
                "responder o usuario caso veja necessário, existe outra ia "
                "responsavel por redirecionar os alunos aos conteudos proprios. "
                "Seja breve e gentil. "
                "Caso o usuario pergunte sobre alguma questão, a outra ia tentara redirecionar, para sanar a duvida."
                "Capitulos e exercicios marcados com 1 significam que foram feitos, com zero signfica que não."
            ),
            "User_message": message_content,
            "User_info": {
                "Name": user.formatted_name,
                "last_name": user.last_name,
                "gender": user.gender,
                "birthday": user.birthday,
                "about_section": user.summary,
                "Chapters user has read on Política Nacional de Saúde Integral da População Negra (PNSIPN)": user.chapter_grade_una,
                "Exercises user has done on Política Nacional de Saúde Integral da População Negra (PNSIPN)": user.exercise_grade_una,
                "past user prompt that required ai": user.past_question,
            },
        }

        prompt_redirect = {
            "Instructions": (
                "Seu objetivo é redicionar o usuario de acordo com o pedido e contexto "
                "Sera disponibilizado a mensagem artual do usuario, a ultima mensagem dele com ia "
                "Um dicionario em formato json, que possui o nome do redirecionador sua descrição e outras opções "
                "voce deve retornar também em formato json. Retorne sempre redirecter e jump."
            ),
            "user_input": message_content,
            "past user prompt that required ai": user.past_question,
            "redirecters": redirecters,
        }

        prompt_response = str(prompt_response)
        prompt_redirect = json.dumps(prompt_redirect)

        ai_content = await get_ai_response(
            client_session=self.client_session,
            prompt=prompt_response,
            timeout_seconds=10,
        )

        ai_redirect = await get_ai_response(
            client_session=self.client_session,
            prompt=prompt_redirect,
            timeout_seconds=10,
        )

        if not ai_content or not ai_redirect:
            return

        ai_redirect = ai_redirect.replace("json", "").replace("`", "")

        try:
            ai_redirect_dic = json.loads(ai_redirect)
        except Exception as e:
            log.exception(f"Couldnt get ai_redirect {e}")

        if isinstance(ai_redirect_dic, dict):
            redirect_function_name = ai_redirect_dic.get("redirecter", "Redirecter")
            jumps = ai_redirect_dic.get("jump", False)
        else:
            redirect_function_name = "Redirecter"
            jumps = False

        log.warning(f"Ai redirecter user to [{redirect_function_name}]")

        user.past_question = (
            f"[User_prompt: {message_content}], [Bot_response: {ai_content}]"
        )

        message_to_send = TextMessage(to=wa_id, body_text=ai_content)
        await message_to_send.send(self.client_session)

        self.next = redirect_function_name
        self.jump = jumps
        user.current_step = self.next
        await self.db_session.commit()
