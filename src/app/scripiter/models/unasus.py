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
from app.client_session.messages.models.cta_url_button import CTAUrlButtonMessage
from app.client_session.messages.models.document import DocumentMessage


log = getLogger(__name__)

unasus_bp = ScriptBlueprint()
unasus_doc = ScripterDocName()

# --- Menu ---
@unasus_doc.register()
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
            
            "Neste espaço, você poderá escolher como deseja interagir com o material:\n\n"
            
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
                {"title": "Exercícios", "id": UnaSusExerciseMenu.__name__},
                {"title": "Bibliografia", "id": UnaSusBib.__name__},
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
@unasus_doc.register()
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

        header = "Navegando pelos Capítulos - PNSIPN"
        body = (
            "Ótima escolha! Você está na seção de Capítulos do módulo sobre "
            "a Política Nacional de Saúde Integral da População (PNSIPN). 😊\n\n"
            
            "Aqui você tem algumas opções para sua leitura:\n\n"
            
            "1. *Escolher um capítulo específico*:\n"
            "Ideal se você quer ir direto para um tópico de interesse ou revisar algo em particular. 🔎\n\n"
            
            "2. *Continuar a leitura de onde parou*:\n"
            "Retome seus estudos exatamente do ponto em que você estava na última vez. ▶️"
        )
        options = {
            "title": "Menu",
            "rows": [
                {
                    "title": "Continuar",
                    "id": UnaSusContinueChapter.__name__,
                    "description": "Continuar de onde parou.",
                },
                {
                    "title": "Unidade 1",
                    "id": UnaSusChapterOne.__name__,
                    "description": "Estatuto da Igualdade Racial",
                },
                {
                    "title": "Unidade 2",
                    "id": UnaSusChapterTwo.__name__,
                    "description": "PNSIPN",
                },
                {
                    "title": "Unidade 3",
                    "id": UnaSusChapterThree.__name__,
                    "description": "Mas o que aconteceu com a PNSIPN?",
                },
                {
                    "title": "Unidade 4",
                    "id": UnaSusChapterFour.__name__,
                    "description": "Marca, Diretrizes e Objetivos da PNSIPN",
                },
                {
                    "title": "Unidade 5",
                    "id": UnaSusChapterFive.__name__,
                    "description": "O Quesito Raça/Cor...",
                }
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




# 0. Continue
@unasus_doc.register()
@unasus_bp.register()
class UnaSusContinueChapter(ScriptBaseModel):
    """Continues the user reading on the Una Sus PNSIPN
    topic."""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        self.next = user.current_chapter_una  # type: ignore
        self.jump = True


# 1. Chapter one
@unasus_doc.register()
@unasus_bp.register()
class UnaSusChapterOne(ScriptBaseModel):
    """Chapter one Una Sus PNSIPN topic
    PNSPIPN e Estatuto da Igualdade Racial; Importância da autodeclaração de Raça/cor"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_u1_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_chapter_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusChapterOneContent(ScriptBaseModel):
    """Redirects the user to the videos they choose,
    or to the exercise section"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        videos = response_json.get("Videos")
        assert isinstance(videos, list)
        if "Documentário_Luis_Gama" in videos:
            next_function = UnaSusVidLuisGamaDoc(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()
        if "Filme_Doutor_Gama" in videos:
            next_function = UnaSusVidLuisGamaFilm(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()

        user.chapter_grade_una["C1"] = 1  # type: ignore
        flag_modified(user, "chapter_grade_una")

        self.next = UnaSusExerciseOne.__name__
        user.current_chapter_una = UnaSusChapterTwo.__name__  # type: ignore
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusVidLuisGamaDoc(ScriptBaseModel):
    """Link for the video on the Documentary on Luis Gama"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Documentário Luis Gama"
        body_text = "O advogado da liberdade"
        display_text = "Assistir"
        url = "https://www.youtube.com/watch?v=WJ1aDH63QrE"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusVidLuisGamaFilm(ScriptBaseModel):
    """Link for the video on the Filme on Luis Gama"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Filme Doutor Gama"
        body_text = "O advogado da liberdade"
        display_text = "Assistir"
        url = "https://www.youtube.com/watch?v=fpQbv2W_ECQ"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


# 2. Chapeter two
@unasus_doc.register()
@unasus_bp.register()
class UnaSusChapterTwo(ScriptBaseModel):
    """Chapter two Una Sus PNSIPN topic
    A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_u2_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_chapter_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusChapterTwoContent(ScriptBaseModel):
    """Redirects the user to the videos they choose,
    or to the exercise section"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)

        if response_json.get("lei_cao"):
            next_function = UnaSusVidLeiCao(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()
        if response_json.get("video_politica"):
            next_function = UnaSusVidPNSIPN(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()
        if response_json.get("documento_historico"):
            next_function = UnaSusDocNorteador(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()

        user.chapter_grade_una["C2"] = 1  # type: ignore
        flag_modified(user, "chapter_grade_una")
        self.next = UnaSusExerciseTwo.__name__
        user.current_chapter_una = UnaSusChapterThree.__name__  # type: ignore
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusVidLeiCao(ScriptBaseModel):
    """Link for the video ide documentário Lei CAÓ 30 anos de Existência e Resistência - Lei 7.716/1989"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Documentário"
        body_text = "Lei CAÓ 30 anos de Existência e Resistência"
        display_text = "Assistir"
        url = "https://www.bing.com/videos/riverview/relatedvideo?q=lei%20ca%C3%B3&mid=E1BACEBB9FDE26B3E700E1BACEBB9FDE26B3E700&ajaxhist=0"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusDocNorteador(ScriptBaseModel):
    """Pdf for the Documento
    histórico norteador do I Seminário Nacional de Saúde da População Negra.
    Nele você encontrará algumas das primeiras análises específicas sobre a saúde da população negra produzidas no Brasil.
    Recorreremos a ele diversas vezes ao longo desta sub-unidade"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        file_name = " Seminário Nacional de Saúde da População Negra.pdf"
        url = "https://bvsms.saude.gov.br/bvs/publicacoes/seminario_nacional_saude_pop_negra.pdf"
        caption = "Nele você encontrará algumas das primeiras análises específicas sobre a saúde da população negra produzidas no Brasil."
        message = DocumentMessage(
            to=wa_id, filename=file_name, link=url, caption=caption
        )
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusVidPNSIPN(ScriptBaseModel):
    """Link for the video Vídeo Política Nacional de Saúde Integral da População Negra (PNSIPN)
    Histórico, diretrizes e objetivos"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Vídeo"
        body_text = "Política Nacional de Saúde Integral da População Negra (PNSIPN) - Histórico, diretrizes e objetivos."
        display_text = "Assistir"
        url = "https://www.youtube.com/watch?v=ANK698VQEVM"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


# 3. Chapter
@unasus_doc.register()
@unasus_bp.register()
class UnaSusChapterThree(ScriptBaseModel):
    """Chapter two Una Sus PNSIPN topic
    A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_u3_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_chapter_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_doc.register()
@unasus_bp.register()
class UnaSusChapterThreeContent(ScriptBaseModel):
    """Redirects the user to the videos they choose,
    or to the exercise section"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        user.chapter_grade_una["C3"] = 1  # type: ignore
        flag_modified(user, "chapter_grade_una")
        self.next = UnaSusExerciseThree.__name__
        user.current_chapter_una = UnaSusChapterFour.__name__  # type: ignore
        await self.db_session.commit()


# 4. Chapter
@unasus_doc.register()
@unasus_bp.register()
class UnaSusChapterFour(ScriptBaseModel):
    """Chapter two Una Sus PNSIPN topic
    A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_u4_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_chapter_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusChapterFourContent(ScriptBaseModel):
    """Redirects the user to the videos they choose,
    or to the exercise section"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        user.chapter_grade_una["C4"] = 1  # type: ignore
        flag_modified(user, "chapter_grade_una")

        self.next = UnaSusExerciseFour.__name__
        user.current_chapter_una = UnaSusChapterFive.__name__  # type: ignore
        await self.db_session.commit()


# 5. Chapter
@unasus_doc.register()
@unasus_bp.register()
class UnaSusChapterFive(ScriptBaseModel):
    """Chapter two Una Sus PNSIPN topic
    A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_u5_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_chapter_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusChapterFiveContent(ScriptBaseModel):
    """Redirects the user to the videos they choose,
    or to the exercise section"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)
        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)

        if response_json.get("guia"):
            next_function = UnaSusDocGuia(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()
        if response_json.get("abrasco"):
            next_function = UnaSusAbrasco(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()
        if response_json.get("Portaria"):
            next_function = UnaSusPortaria(
                self.db_session, self.client_session, self.registery, self.value
            )
            await next_function._fn()

        user.chapter_grade_una["C5"] = 1  # type: ignore
        flag_modified(user, "chapter_grade_una")

        self.next = UnaSusExerciseFive.__name__
        user.current_chapter_una = UnaSusChapterFive.__name__  # type: ignore
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusPortaria(ScriptBaseModel):
    """Link for the site Portaria 344/2017"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Documento"
        body_text = "Portaria 344/2017"
        display_text = "Ler"
        url = (
            "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2017/prt0344_01_02_2017.html"
        )
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusAbrasco(ScriptBaseModel):
    """Link for the video Agora da ABRASCO sobre a PNSIPN e o preenchimento do 	quesito raça-cor."""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Vídeo"
        body_text = (
            "Agora da ABRASCO sobre a PNSIPN e o preenchimento do 	quesito raça-cor. "
        )
        display_text = "Assistir"
        url = "https://www.youtube.com/watch?v=FxaMakGEOUI"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusDocGuia(ScriptBaseModel):
    """Pdf for the Documento
    Guia de Enfrentamento ao Racismo Institucional"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        file_name = "Guia de Enfrentamento ao Racismo Institucional.pdf"
        url = "https://www.onumulheres.org.br/wp-content/uploads/2013/12/Guia-de-enfrentamento-ao-racismo-institucional.pdf"
        message = DocumentMessage(to=wa_id, filename=file_name, link=url)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


# Exercises
@unasus_bp.register()
@unasus_doc.register()
class UnaSusExerciseMenu(ScriptBaseModel):
    """Menu conteining all Exercises for UnaSus content on
    Política Nacional de Saúde Integral da População"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Hora de Praticar! - Exercícios PNSIPN"
        body = (
            "Excelente! Você está pronto(a) para testar seus conhecimentos na "
            "seção de Exercícios do módulo sobre a Política Nacional de Saúde Integral da População (PNSIPN). 💪\n\n"
            "Aqui você tem algumas opções:\n\n"
            "1. *Escolher um conjunto de exercícios específico*:\n"
            "Ideal se você quer praticar sobre um capítulo ou tópico em particular. 🎯\n\n"
            "2. *Continuar os exercícios de onde parou*:\n"
            "Retome o último exercício ou conjunto que você estava resolvendo. ▶️"
        )
        options = {
            "title": "Menu",
            "rows": [
                {
                    "title": "Continuar",
                    "id": UnaSusContinueExercise.__name__,
                    "description": "Continuar de onde parou.",
                },
                {
                    "title": "Unidade 1",
                    "id": UnaSusExerciseOne.__name__,
                    "description": "Estatuto da Igualdade Racial",
                },
                {
                    "title": "Unidade 2",
                    "id": UnaSusExerciseTwo.__name__,
                    "description": "PNSIPN",
                },
                {
                    "title": "Unidade 3",
                    "id": UnaSusExerciseThree.__name__,
                    "description": "Mas o que aconteceu com a PNSIPN?",
                },
                {
                    "title": "Unidade 4",
                    "id": UnaSusExerciseFour.__name__,
                    "description": "Marca, Diretrizes e Objetivos da PNSIPN",
                },
                {
                    "title": "Unidade 5",
                    "id": UnaSusExerciseFive.__name__,
                    "description": "O Quesito Raça/Cor...",
                },
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


# 0. Continue
@unasus_doc.register()
@unasus_bp.register()
class UnaSusContinueExercise(ScriptBaseModel):
    """Continues the user reading on the Una Sus PNSIPN
    topic."""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        
        self.next = user.current_exercise_una  # type: ignore
        self.jump = True


@unasus_bp.register()
@unasus_doc.register()
class UnaSusRetryExercise(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = InteractiveButtonMessage(
            to=wa_id,
            body_text="Deseja Tentar Novamente?",
            buttons=[
                {"id": UnaSusContinueExercise.__name__, "title": "Sim"},
                {"id": UnaSusContinueChapter.__name__, "title": "Não"},
            ],
        )
        message.add_header("Sua Resposta Estava Incorreta!")

        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


# 1. Exercise
@unasus_doc.register()
@unasus_bp.register()
class UnaSusExerciseOne(ScriptBaseModel):
    """Exercise one Una Sus PNSIPN topic
    PNSPIPN e Estatuto da Igualdade Racial; Importância da autodeclaração de Raça/cor"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_e1_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_exercise_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseOneHandle(ScriptBaseModel):
    """Handles Exercise one answers"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        q1_handler = UnaSusExerciseOneQ1Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q1_handler._fn()

        q2_handler = UnaSusExerciseOneQ2Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q2_handler._fn()

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)

        q1_answer = response_json.get("q1")
        q2_answer = response_json.get("q2")

        self.next = UnaSusChapterTwo.__name__

        if (q1_answer != "b") or (q2_answer != "c"):
            self.next = UnaSusRetryExercise.__name__

        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseOneQ1Answer(ScriptBaseModel):
    """Handles Exercise one Question one"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q1_answer = response_json.get("q1")

        match q1_answer:
            case "a":
                handler = UnaSusE1Q1A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE1Q1B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E1"][0] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "c":
                handler = UnaSusE1Q1C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "d":
                handler = UnaSusE1Q1D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q1A(ScriptBaseModel):
    """Explains UnaSus Exercise one Question 1 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "A PNSIPN foca na integralidade da saúde e no combate às desigualdades para "
            "promover o acesso equitativo, não na instituição de cotas para acesso a serviços."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q1B(ScriptBaseModel):
    """Explains UnaSus Exercise one Question 1 Alternative B"""

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
            "*Alternativa Correta*:\n\n"
            "A apresentação da Unidade 1 afirma que a PNSIPN 'é a primeira  "
            "política pública a reconhecer oficialmente o racismo institucional e estrutural, "
            "bem como reconhecer os diversos impactos adversos do racismo na saúde'."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q1C(ScriptBaseModel):
    """Explains UnaSus Exercise one Question  1 Alternative C"""

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
            "*Alternativa Incorreta*:\n\n"
            "A PNSIPN incentiva a formação e educação permanente dos trabalhadores da "
            "saúde sobre o tema, mas não estabelece obrigatoriedade de contratação baseada "
            "em raça."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q1D(ScriptBaseModel):
    """Explains UnaSus Exercise one Question 1 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "A política visa a melhoria das condições de saúde da população negra dentro "
            "do SUS, promovendo equidade, e não criando um sistema de financiamento paralelo."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseOneQ2Answer(ScriptBaseModel):
    """Handles Exercise one Question two"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q2_answer = response_json.get("q2")

        match q2_answer:
            case "a":
                handler = UnaSusE1Q2A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE1Q2B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "c":
                handler = UnaSusE1Q2C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E1"][1] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "d":
                handler = UnaSusE1Q2D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q2A(ScriptBaseModel):
    """Explains UnaSus Exercise one Question 2 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "Embora a PNSIPN aborde a saúde da população negra de forma integral, a Portaria "
            "344 tem como foco específico a coleta do dado raça/cor."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q2B(ScriptBaseModel):
    """Explains UnaSus Exercise one Question 2 Alternative B"""

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
            "*Alternativa Incorreta*:\n\n"
            "A Portaria 344 é normativa sobre a coleta de dados e não trata diretamente "
            "de mecanismos de repasse de verbas, embora os dados coletados possam subsidiar "
            "planejamentos futuros. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q2C(ScriptBaseModel):
    """Explains UnaSus Exercise one Question 2 Alternative C"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 1 menciona que 'Em 2017, a Portaria 344 estabeleceu "
            "a obrigatoriedade do adequado e completo preenchimento quesito raça/cor nos "
            "documentos de registro do SUS a partir da auto-declaração dos pacientes'. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE1Q2D(ScriptBaseModel):
    """Explains UnaSus Exercise one Question 2 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "Campanhas de conscientização são importantes, mas a Portaria 344 estabelece "
            "uma norma procedimental para a coleta de informações. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


# 2. Exercise
@unasus_doc.register()
@unasus_bp.register()
class UnaSusExerciseTwo(ScriptBaseModel):
    """Exercise Two Una Sus PNSIPN
    topic A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_e2_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_exercise_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseTwoHandle(ScriptBaseModel):
    """Handles Exercise Two answers"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        q1_handler = UnaSusExerciseTwoQ1Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q1_handler._fn()

        q2_handler = UnaSusExerciseTwoQ2Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q2_handler._fn()

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)

        q1_answer = response_json.get("q1")
        q2_answer = response_json.get("q2")

        self.next = UnaSusChapterThree.__name__

        if (q1_answer != "b") or (q2_answer != "c"):
            self.next = UnaSusRetryExercise.__name__

        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseTwoQ1Answer(ScriptBaseModel):
    """Handles Exercise 2 Question one"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q1_answer = response_json.get("q1")

        match q1_answer:
            case "a":
                handler = UnaSusE2Q1A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE2Q1B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E2"][0] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "c":
                handler = UnaSusE2Q1C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "d":
                handler = UnaSusE2Q1D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q1A(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question 1 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "O texto destaca que a PNSIPN é 'mais uma conquista dos movimentos sociais' "
            "e 'fruto de intensas mobilizações do Movimento Negro'. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()
        
@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q1B(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question 1 Alternative B"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 2 afirma que a PNSIPN 'é a primeira legislação "
            "nacional a reconhecer a existência do racismo institucional e o impacto do racismo "
            "na saúde'. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q1C(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question  1 Alternative C"""

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
            "*Alternativa Incorreta*:\n\n"
            "Embora a atenção à anemia falciforme seja um componente importante, a PNSIPN "
            "é mais abrangente, incluindo 'ações de cuidado, atenção, promoção à saúde "
            "e prevenção de doenças... gestão participativa, participação popular e controle "
            "social, produção de conhecimento, formação e educação permanente'. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q1D(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question 1 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "A PNSIPN é uma política instituída, não um programa temporário, e visa a "
            "melhoria contínua das condições de saúde da população negra. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseTwoQ2Answer(ScriptBaseModel):
    """Handles Exercise 2 Question two"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q2_answer = response_json.get("q2")

        match q2_answer:
            case "a":
                handler = UnaSusE2Q2A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE2Q2B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "c":
                handler = UnaSusE2Q2C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E2"][1] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "d":
                handler = UnaSusE2Q2D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q2A(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question 2 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "A Lei Afonso Arinos é mencionada como uma das 'medidas legais que foram sendo "
            "produzidas visando reduzir as iniquidades étnico-raciais históricas'. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q2B(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question 2 Alternative B"""

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
            "*Alternativa Incorreta*:\n\n"
            "A Lei Caó também é citada no mesmo contexto da Lei Afonso Arinos."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q2C(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question 2 Alternative C"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 2 lista diversas leis e decretos importantes, "
            "como a Lei Afonso Arinos, a Lei Caó e a criação da SEPPIR. O Estatuto da Criança "
            "e do Adolescente, embora fundamental para os direitos infantojuvenis, não é "
            "especificamente mencionado no contexto da trajetória de criação da PNSIPN descrito "
            "nesta unidade. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE2Q2D(ScriptBaseModel):
    """Explains UnaSus Exercise 2 Question 2 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "A criação da SEPPIR é listada como um dos desenvolvimentos importantes no "
            "período que antecedeu a PNSIPN. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


# 3. Exercise
@unasus_doc.register()
@unasus_bp.register()
class UnaSusExerciseThree(ScriptBaseModel):
    """Exercise Two Una Sus PNSIPN
    topic A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_e3_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_exercise_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseThreeHandle(ScriptBaseModel):
    """Handles Exercise Three answers"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        q1_handler = UnaSusExerciseThreeQ1Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q1_handler._fn()

        q2_handler = UnaSusExerciseThreeQ2Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q2_handler._fn()

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)

        q1_answer = response_json.get("q1")
        q2_answer = response_json.get("q2")

        self.next = UnaSusChapterFour.__name__

        if (q1_answer != "c") or (q2_answer != "c"):
            self.next = UnaSusRetryExercise.__name__

        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseThreeQ1Answer(ScriptBaseModel):
    """Handles Exercise 3 Question one"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q1_answer = response_json.get("q1")

        match q1_answer:
            case "a":
                handler = UnaSusE3Q1A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE3Q1B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "c":
                handler = UnaSusE3Q1C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E3"][0] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "d":
                handler = UnaSusE3Q1D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q1A(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question 1 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "'O texto indica o oposto: menor acesso e menor taxa de internação para a "
            "população negra.' "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q1B(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question 1 Alternative B"""

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
            "*Alternativa Incorreta*:\n\n"
            "Não há menção no texto sobre desenvolvimento de tratamentos específicos mais "
            "eficazes para a população negra durante a pandemia; pelo contrário, as desigualdades "
            "no acesso foram ressaltadas. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q1C(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question  1 Alternative C"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 3 afirma que 'Durante a pandemia de COVID-19, "
            "evidenciou-se de forma aguda os impactos do racismo estrutural na saúde dessa "
            "população. Os negros tiveram menos acesso a serviços de saúde, menor taxa de "
            "internação, receberam menos vacinas e tiveram maior taxa de mortalidade pelo "
            "SARS-CoV-2 que a população branca'. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q1D(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question 1 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "O texto contradiz essa afirmação, explicitando que a pandemia evidenciou "
            "os impactos do racismo estrutural e as desigualdades raciais na saúde. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseThreeQ2Answer(ScriptBaseModel):
    """Handles Exercise 2 Question two"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q2_answer = response_json.get("q2")

        match q2_answer:
            case "a":
                handler = UnaSusE3Q2A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE3Q2B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "c":
                handler = UnaSusE3Q2C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E3"][1] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "d":
                handler = UnaSusE3Q2D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q2A(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question 2 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "O texto foca em barreiras estruturais e institucionais de acesso, e não em "
            "uma recusa generalizada por parte das comunidades. A PNSIPN, inclusive, prevê "
            "o reconhecimento de saberes populares. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q2B(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question 2 Alternative B"""

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
            "*Alternativa Incorreta*:\n\n"
            "O problema apontado é o acesso limitado a serviços e equipamentos de saúde, "
            "e não um excesso de equipes. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q2C(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question 2 Alternative C"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 3 aponta que 'a maioria dos seus territórios "
            "tradicionalmente ocupados continua sem reconhecimento/demarcação oficial, e "
            "muitos municípios sequer reconhecem a existência dessas comunidades em sua área "
            "de abrangência', o que impacta o acesso a políticas públicas, incluindo saúde. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE3Q2D(ScriptBaseModel):
    """Explains UnaSus Exercise 3 Question 2 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "O texto afirma o contrário: ''as populações quilombolas, apresentam os piores "
            "indicadores nacionais de saúde''.' "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


# 4. Exercise
@unasus_bp.register()
@unasus_doc.register()
class UnaSusExerciseFour(ScriptBaseModel):
    """Exercise Two Una Sus PNSIPN
    topic A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_e4_1",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_exercise_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseFourHandle(ScriptBaseModel):
    """Handles Exercise Four answers"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        q1_handler = UnaSusExerciseFourQ1Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q1_handler._fn()

        q2_handler = UnaSusExerciseFourQ2Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q2_handler._fn()

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)

        q1_answer = response_json.get("q1")
        q2_answer = response_json.get("q2")

        self.next = UnaSusChapterFive.__name__

        if (q1_answer != "b") or (q2_answer != "c"):
            self.next = UnaSusRetryExercise.__name__

        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseFourQ1Answer(ScriptBaseModel):
    """Handles Exercise 4 Question one"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q1_answer = response_json.get("q1")

        match q1_answer:
            case "a":
                handler = UnaSusE4Q1A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE4Q1B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E4"][0] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "c":
                handler = UnaSusE4Q1C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "d":
                handler = UnaSusE4Q1D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE4Q1A(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 1 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "Fomentar estudos e pesquisas é um objetivo específico (XII), mas o objetivo "
            "geral é mais amplo e focado na promoção da saúde integral e combate às desigualdades. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE4Q1B(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 1 Alternative B"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 4 define o Objetivo Geral da PNSIPN como: ''Promover "
            "a saúde integral da população negra, priorizando a redução das desigualdades "
            "étnico-raciais, o combate ao racismo e à discriminação nas instituições e serviços "
            "do SUS.''' "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE4Q1C(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question  1 Alternative C"""

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
            "*Alternativa Incorreta*:\n\n"
            "Embora a participação e o controle social sejam diretrizes, o objetivo geral "
            "não se restringe à representação em cargos de gestão, mas à promoção da saúde "
            "integral. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE4Q1D(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 1 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "A PNSIPN visa a equidade dentro do SUS, fortalecendo-o para atender adequadamente "
            "a população negra, e não criar um sistema paralelo. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseFourQ2Answer(ScriptBaseModel):
    """Handles Exercise 2 Question two"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q2_answer = response_json.get("q2")

        match q2_answer:
            case "a":
                handler = UnaSusE4Q2A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE4Q2B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "c":
                handler = UnaSusE4Q2C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E4"][1] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "d":
                handler = UnaSusE4Q2D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()


@unasus_bp.register()
class UnaSusE4Q2A(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 2 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "Esta é a Diretriz Geral I, focada na formação dos profissionais."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusE4Q2B(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 2 Alternative B"""

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
            "*Alternativa Incorreta*:\n\n"
            "Esta é a Diretriz Geral II, focada na participação social."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusE4Q2C(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 2 Alternative C"""

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
            "*Alternativa Correta*:\n\n"
            "'A Diretriz Geral IV da PNSIPN, conforme a Unidade 4, é: "
            "''Promoção do reconhecimento dos saberes e práticas populares de saúde, incluindo "
            "aqueles preservados pelas religiões de matrizes africanas'', o que se alinha "
            "com a valorização de conhecimentos não hegemônicos.' "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()

@unasus_doc.register()
@unasus_bp.register()
class UnaSusE4Q2D(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 2 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "Esta é a Diretriz Geral V, focada no monitoramento e avaliação."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


# 5. Exercise
@unasus_doc.register()
@unasus_bp.register()
class UnaSusExerciseFive(ScriptBaseModel):
    """Exercise Two Una Sus PNSIPN
    topic A Política Nacional de Saúde Integral da População Negra (PNSIPN)"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_e5_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_exercise_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseFiveHandle(ScriptBaseModel):
    """Handles Exercise Five answers"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        q1_handler = UnaSusExerciseFiveQ1Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q1_handler._fn()

        q2_handler = UnaSusExerciseFiveQ2Answer(
            self.db_session, self.client_session, self.registery, self.value
        )
        await q2_handler._fn()

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)

        q1_answer = response_json.get("q1")
        q2_answer = response_json.get("q2")

        self.next = UnaCheckCongratulations.__name__

        if (q1_answer != "b") or (q2_answer != "c"):
            self.next = UnaSusRetryExercise.__name__

        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseFiveQ1Answer(ScriptBaseModel):
    """Handles Exercise 5 Question one"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q1_answer = response_json.get("q1")

        match q1_answer:
            case "a":
                handler = UnaSusE5Q1A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE5Q1B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E5"][0] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "c":
                handler = UnaSusE5Q1C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "d":
                handler = UnaSusE5Q1D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q1A(ScriptBaseModel):
    """Explains UnaSus Exercise 5 Question 1 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "O texto explicitamente condena a heteroidentificação (quando o servidor atribui "
            "a raça/cor sem perguntar), indicando que é contrária à Portaria 344. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q1B(ScriptBaseModel):
    """Explains UnaSus Exercise 5 Question 1 Alternative B"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 5, ao discutir a Portaria 344/2017, enfatiza "
            "que a coleta 'respeitará o critério de autodeclaração do usuário de saúde'. "
            "O texto também critica a heteroidentificação, que seria a observação pelo profissional. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q1C(ScriptBaseModel):
    """Explains UnaSus Exercise 5 Question  1 Alternative C"""

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
            "*Alternativa Incorreta*:\n\n"
            "A portaria foca na autodeclaração no momento do atendimento no serviço de "
            "saúde, não primariamente em registros civis para essa finalidade. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q1D(ScriptBaseModel):
    """Explains UnaSus Exercise 5 Question 1 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "Embora a ascendência possa influenciar a autodeclaração, o critério estabelecido "
            "pela portaria é a autodeclaração do indivíduo sobre como ele se identifica "
            "no momento. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusExerciseFiveQ2Answer(ScriptBaseModel):
    """Handles Exercise 2 Question two"""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)

        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        q2_answer = response_json.get("q2")

        match q2_answer:
            case "a":
                handler = UnaSusE5Q2A(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "b":
                handler = UnaSusE5Q2B(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
            case "c":
                handler = UnaSusE5Q2C(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()
                user.exercise_grade_una["E5"][1] = 1  # type: ignore
                flag_modified(user, "exercise_grade_una")
                await self.db_session.commit()
            case "d":
                handler = UnaSusE5Q2D(
                    self.db_session, self.client_session, self.registery, self.value
                )
                await handler._fn()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q2A(ScriptBaseModel):
    """Explains UnaSus Exercise 5 Question 2 Alternative A"""

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
            "*Alternativa Incorreta*:\n\n"
            "A incompletude é um problema a ser sanado, não um critério para aumento de"
            "financiamento. O texto aponta a incompletude como uma lacuna."
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q2B(ScriptBaseModel):
    """Explains UnaSus Exercise 5 Question 2 Alternative B"""

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
            "*Alternativa Incorreta*:\n\n"
            "A incompletude, especialmente quando se marca 'ignorado', representa uma "
            "perda de informação e prejudica a qualidade e a representatividade dos dados. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q2C(ScriptBaseModel):
    """Explains UnaSus Exercise 5 Question 2 Alternative C"""

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
            "*Alternativa Correta*:\n\n"
            "A Unidade 5 conclui que 'Sem o adequado registro, é impossível "
            "planejar para adequada implementação da PNSIPN ou qualquer outra política pública "
            "que objetive reduzir as iniquidades étnico-raciais.' "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusE5Q2D(ScriptBaseModel):
    """Explains UnaSus Exercise 4 Question 2 Alternative D"""

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
            "*Alternativa Incorreta*:\n\n"
            "A ausência do dado raça/cor impede a análise de desigualdades e o direcionamento "
            "de políticas específicas, não simplificando a análise de forma positiva, mas "
            "sim a tornando menos completa e menos capaz de identificar disparidades. "
        )

        message = TextMessage(to=wa_id, body_text=message_content)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


# Check Exercises:
@unasus_bp.register()
@unasus_doc.register()
class UnaCheckCongratulations(ScriptBaseModel):
    """Checks if you have completed all exercises on unasus"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        chapters = user.chapter_grade_una
        chapter_map = {
            "C1": "Falta o capítulo 1.",
            "C2": "Falta o capítulo 2",
            "C3": "Falta o capítulo 3",
            "C4": "Falta o capítulo 4",
            "C5": "Falta o capítulo 5 ",
        }
        exercises = user.exercise_grade_una
        exercises_map = {
            "E1": (
                "Exercicio 1 Questão 1, faltante.",
                "Exercicio 1 Questão 2, faltante.",
            ),
            "E2": (
                "Exercicio 2 Questão 1, faltante.",
                "Exercicio 2 Questão 2, faltante.",
            ),
            "E3": (
                "Exercicio 3 Questão 1, faltante.",
                "Exercicio 3 Questão 2, faltante.",
            ),
            "E4": (
                "Exercicio 4 Questão 1, faltante.",
                "Exercicio 4 Questão 2, faltante.",
            ),
            "E5": (
                "Exercicio 5 Questão 1, faltante.",
                "Exercicio 5 Questão 2, faltante.",
            ),
        }

        give_congrats = True
        for key, value in chapters.items():
            if value == 0:
                give_congrats = False
                message_content = chapter_map.get(key)
                message = TextMessage(to=wa_id, body_text=message_content) # type: ignore
                await message.send(self.client_session)

        for ex_key, ex_grades_list in exercises.items():
            exercise_specific_messages = exercises_map.get(ex_key)
            for i, grade_value in enumerate(ex_grades_list):
                if grade_value == 0:
                    give_congrats = False
                    if i < len(exercise_specific_messages): # type: ignore
                        message_content = exercise_specific_messages[i] # type: ignore
                        message = TextMessage(to=wa_id, body_text=message_content)
                        await message.send(self.client_session)

        if give_congrats:
            message_content = "Parabens você completou toda essa seção com exito!"
            message = TextMessage(to=wa_id, body_text=message_content)
            await message.send(self.client_session)

        self.next = "Redirecter"
        user.current_step = self.next
        await self.db_session.commit()


# --- Bibiograph
@unasus_doc.register()
@unasus_bp.register()
class UnaSusBib(ScriptBaseModel):
    """Bibliograph of una sus content"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_unasus_bib_0",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        user.current_exercise_una = self.__class__.__name__
        await self.db_session.commit()


@unasus_bp.register()
class UnaSusBibHandle(ScriptBaseModel):
    """Bibliograph of una sus content"""

    async def _fn(self):
        self.jump = True
        messages = self.value.messages
        if not messages:
            return
        message = messages[0]
        assert isinstance(message, NfmReplyMessage)
        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]
        wa_id = contact.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        
        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        
        if response_json.get("denuncia_site"):
            handler = UnaSusDenunciaSite(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("desigualdades_pdf"):
            handler = UnaSusDesiqualPdf(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("destino_site"):
            handler = UnaSusDestinoSite(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("politica_nacional_video"):
            handler = UnaSusPoliticaVideo(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("diretos_humanos_pdf"):
            handler = UnaSusDireitosHumanosPdf(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("racismo_estrutural_pdf"):
            handler = UnaSusRaciPdf(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("guia_pdf"):
            handler = UnaSusGuiaPdf(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("boletim_v1_site"):
            handler = UnaSusBoletimV1Site(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("boletim_v2_site"):
            handler = UnaSusBoletimV2Site(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        if response_json.get("comunidades_pdf"):
            handler = UnaSusComunityPdf(self.db_session, self.client_session, self.registery, self.value)
            await handler._fn()
        
        
        user.current_step = "Redirecter"
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusRaciPdf(ScriptBaseModel):
    """Pdf for the Documento
    ALMEIDA, Silvio Luís. Racismo estrutural. Coleção Feminismos Plurais. São Paulo: Sueli Carneiro; Pólen. Brasil 2011
    """

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        file_name = "Racismo estrutural.pdf"
        url = "https://fpabramo.org.br/csbh/wp-content/uploads/sites/3/2020/11/DOC_0013-2.pdf"
        message = DocumentMessage(to=wa_id, filename=file_name, link=url)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusGuiaPdf(ScriptBaseModel):
    """Pdf for the Documento
    BRASIL. Guia de implementação do quesito Raça/Cor/Etnia. Brasília: Universidade de Brasília, Ministério da Saúde, 2018.
    """

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        file_name = "Guia de implementação.pdf"
        url = "http://bvsms.saude.gov.br/bvs/publicacoes/guia_implementacao_raca_cor_etnia.pdf"
        message = DocumentMessage(to=wa_id, filename=file_name, link=url)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusBoletimV1Site(ScriptBaseModel):
    """Link for the siteBoletim Epidemiológico Especial. Saúde da População Negra, Volume 1"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Boletim Epidemiológico Especial"
        body_text = " Saúde da População Negra, Volume 1"
        display_text = "Visitar"
        url = "https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/boletins/epidemiologicos/especiais/2023/boletim-epidemiologico-saude-da-populacao-negra-numero-especial-vol-1-out.2023"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusBoletimV2Site(ScriptBaseModel):
    """Link for the siteBoletim Epidemiológico Especial. Saúde da População Negra, Volume 2"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Boletim Epidemiológico Especial"
        body_text = "Saúde da População Negra, Volume 2."
        display_text = "Visitar"
        url = "https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/boletins/epidemiologicos/especiais/2023/boletim-epidemiologico-saude-da-populacao-negra-numero-especial-vol-2-out.2023"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusComunityPdf(ScriptBaseModel):
    """Pdf for the Documento
    Vulnerabilidade Histórica e Futura das Comunidades Quilombolas do Pará em Tempo de Pandemia.
    """

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        file_name = "Comunidades Quilombolas.pdf"
        url = "https://malungu.org/wp-content/uploads/2021/11/Vulnerabilidade...-digital.pdf"
        message = DocumentMessage(to=wa_id, filename=file_name, link=url)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusDenunciaSite(ScriptBaseModel):
    """Link for the site Denúncia do CNS e CNDH à ONU mostra que negros morreram cinco vezes mais de Covid-19 que brancos."""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Denúncia do CNS e CNDH à ONU"
        body_text = "mostra que negros morreram cinco vezes mais de Covid-19 que brancos. Portal do CNS. Publicado em 26 de novembro de 2021."
        display_text = "Visitar"
        url = "https://conselho.saude.gov.br/ultimas-noticias-cns/2211-denuncia-do-cns-e-cndh-a-onu-mostra-que-negros-morreram-cinco-vezes-mais-de-covid-19-que-brancos"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusDesiqualPdf(ScriptBaseModel):
    """Pdf for the Documento
    Desigualdades Raciais e Covid-19. O que a pandemia encontra no Brasil.
    """

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        file_name = " Desigualdades Raciais.pdf"
        url = "https://cebrap.org.br/wp-content/uploads/2020/11/Afro_Informativo-1_final_-2.pdf"
        message = DocumentMessage(to=wa_id, filename=file_name, link=url)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusDestinoSite(ScriptBaseModel):
    """Link for the site Denúncia do CNS e CNDH à ONU mostra que negros morreram cinco vezes mais de Covid-19 que brancos."""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "O Destino dos negros após a abolição"
        body_text = ". Instituto de Pesquisa Econômica Aplicada - IPEA. Ed. 70, 29/12/2011. Ano 8, 2011"
        display_text = "Visitar"
        url = "https://www.ipea.gov.br/desafios/index.php?option=com_content&id=2673%3Acatid%3D28"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()


@unasus_bp.register()
@unasus_doc.register()
class UnaSusPoliticaVideo(ScriptBaseModel):
    """Link for the video Como implementar a Política Nacional de Saúde Integral da População Negra no seu município?"""

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Como implementar "
        body_text = "a Política Nacional de Saúde Integral da População Negra no seu município? Sociedade Brasileira de Medicina de Família e Comunidade, 2023"
        display_text = "Assistir"
        url = "https://www.youtube.com/watch?v=VQrocnNtpHo"
        message = CTAUrlButtonMessage(
            to=wa_id, display_text=display_text, body_text=body_text, url=url
        )
        message.add_header(header)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()

@unasus_bp.register()
@unasus_doc.register()
class UnaSusDireitosHumanosPdf(ScriptBaseModel):
    """Pdf for the Documento
    Desigualdades Raciais e Covid-19. O que a pandemia encontra no Brasil.
    """

    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        file_name = "Direitos Humanos.pdf"
        url = "https://www.social.org.br/images/pdf/direitos_humanos_2021.pdf"
        message = DocumentMessage(to=wa_id, filename=file_name, link=url)
        await message.send(self.client_session)

        self.next = "Redirecter"
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        user.current_step = self.next
        await self.db_session.commit()