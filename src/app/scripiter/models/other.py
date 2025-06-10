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

user_bp = ScriptBlueprint()


# --- Redirecter ---
@user_bp.register()
class Redirecter(ScriptBaseModel):
    """This class is responsible for redirecting unkown text payloads
    to the AI model to answer and also: list, button, flow payloads to redrect them."""

    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return

        message = messages[0]

        contatcs = self.value.contacts
        if not contatcs:
            return
        contact = contatcs[0]

        self.jump = True

        if isinstance(message, ButtonMessageMessage):
            self.next = message.interactive.button_reply.id

        if isinstance(message, ListMessageMessage):
            self.next = message.interactive.list_reply.id

        if isinstance(message, NfmReplyMessage):
            await self.handle_nfm_reply(message, contact)

        if isinstance(message, TextMessageWeb):
            message_body = message.text.body
            match message_body:
                case "/Capitulos":
                    self.next = MenuChapters.__name__
                case "/Exercicios":
                    self.next = MenuExercises.__name__
                case "/Menu":
                    self.next = Menu.__name__
                case "/Info":
                    self.next = PersonalInfoMenu.__name__
                case _:
                    self.next = AIResponse.__name__

    async def handle_nfm_reply(self, message: NfmReplyMessage, contact: Contact):
        """A loot of the logic behind the chapters is here"""
        response_json: dict = json.loads(message.interactive.nfm_reply.response_json)
        wa_id = contact.wa_id
        flow_token = response_json.get("flow_token")
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        match flow_token:
            case IntroPersonalInfo.__name__:
                self.next = IntroMenu.__name__
                    
                # --- Updates user info ---
                user.formatted_name = response_json.get("Nome")
                user.last_name = response_json.get("Sobrenome")
                user.email = response_json.get("Email")
                user.birthday = response_json.get("Aniversrio")
                user.summary = response_json.get("Sobre_Voce")
                await self.db_session.commit()  # Commits to be used in the next call

            case PersonalInfoMenu.__name__:
                self.next = Menu.__name__
                user.formatted_name = response_json.get("Nome")
                user.last_name = response_json.get("Sobrenome")
                user.email = response_json.get("Email")
                user.birthday = response_json.get("Aniversrio")
                user.summary = response_json.get("Sobre_Voce")
                await self.db_session.commit()  # Commits to be used in the next call

            case ChapterOne.__name__:
                self.next = ExerciseOne.__name__
                user.chapter_grade["C1"] = "✅"  # type: ignore
                flag_modified(
                    user, "chapter_grade"
                )  # SQL Alchemy has problems with JSON
                await self.db_session.commit()

            case ExerciseOne.__name__:
                answer = response_json.get("choice")
                controler = ExerciseOneChoice(
                    self.client_session, self.db_session, wa_id
                )
                self.next = await controler.handle_choice(answer)  # type: ignore

            case ChapterTwo.__name__:
                self.next = ExerciseTwo.__name__
                user.chapter_grade["C2"] = "✅"  # type: ignore
                flag_modified(
                    user, "chapter_grade"
                )  # SQL Alchemy has problems with JSON
                await self.db_session.commit()

            case ExerciseTwo.__name__:
                answer = response_json.get("choice")
                controler = ExerciseTwoChoice(
                    self.client_session, self.db_session, wa_id
                )
                self.next = await controler.handle_choice(answer)  # type: ignore

            case ChapterThree.__name__:
                self.next = ExerciseThree.__name__
                user.chapter_grade["C3"] = "✅"  # type: ignore
                flag_modified(
                    user, "chapter_grade"
                )  # SQL Alchemy has problems with JSON
                await self.db_session.commit()

            case ExerciseThree.__name__:
                answer = response_json.get("choice")
                controler = ExerciseThreeChoice(
                    self.client_session, self.db_session, wa_id
                )
                self.next = await controler.handle_choice(answer)  # type: ignore

            case ChapterFour.__name__:
                self.next = ExerciseFour.__name__
                user.chapter_grade["C4"] = "✅"  # type: ignore
                flag_modified(
                    user, "chapter_grade"
                )  # SQL Alchemy has problems with JSON
                await self.db_session.commit()
            case ExerciseFour.__name__:
                answer = response_json.get("choice")
                controler = ExerciseFourChoice(
                    self.client_session, self.db_session, wa_id
                )
                self.next = await controler.handle_choice(answer)  # type: ignore

            case _:
                pass


@user_bp.register()
class Retry(ScriptBaseModel):
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
                {"id": ContinueExercise.__name__, "title": "Sim"},
                {"id": Menu.__name__, "title": "Não"},
            ],
        )
        message.add_header("Sua Resposta Estava Incorreta!")

        await message.send(self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


# --- Intros ---
@user_bp.register()
class HelloUser(ScriptBaseModel):
    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return

        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        intro_message = (
            "Prazer em te conhecer! 👋 Sou um bot do WhatsApp, ainda em fase de desenvolvimento. 🛠️\n"
            "\nMeu propósito hoje é demonstrar minhas capacidades no ensino à distância. "
            "🎓 Vamos simular um ambiente de aprendizado onde poderemos vivenciar este processo! 🧑‍🏫\n"
            "\nPara o nosso assunto de hoje, vamos analisar o conto *'Negrinha'* 📖, de *Monteiro Lobato*.\n"
            "\nMas, antes de continuarmos, gostaria de te conhecer um pouco melhor! 😊 Me conta um pouco sobre você?\n"
        )

        message = TextMessage(to=wa_id, body_text=intro_message)
        await message.send(client_session=self.client_session)

        self.next = IntroPersonalInfo.__name__
        self.jump = True


@user_bp.register()
class IntroPersonalInfo(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        flow_action_data = {
            "Nome": contatc.profile.name,
            "Sobrenome": "",
            "Email": "",
            "Data_de_Aniversrio": "",
            "Me_fale_sobre_voce": "",
        }

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_sobre_voce",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_action_data_payload=flow_action_data,
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


@user_bp.register()
class IntroMenu(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Menu Inicial"
        body = (
            "Este é o menu (ou painel de controle) ⚙️, "
            "onde você, o usuário, pode conferir suas informações "
            "pessoais 👤 ou navegar para outros menus.\n Temos, por exemplo:\n"
            "* A seção de Capítulos 📚: para você escolher de onde continuar sua leitura.\n"
            "* E a seção de Exercícios 🧠: onde você pode praticar o conhecimento adquirido."
        )
        options = {
            "title": "Menu",
            "rows": [
                {"title": "Informações Pessoais", "id": PersonalInfoMenu.__name__},
                {"title": "Capítulos", "id": IntroMenuChapters.__name__},
                {"title": "Exercícios", "id": IntroMenuExercises.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Ver", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


@user_bp.register()
class IntroMenuChapters(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Painel Capítulos"
        body = (
            "Este é o painel dos Capítulos 📚.\n Aqui, você poderá fazer a leitura do conto "
            "*Negrinha*, de *Monteiro Lobato*, de maneira gradual, conforme seu tempo permitir (ou no seu próprio ritmo ⏳).\n"
            "O conto foi dividido em 4 partes, organizadas de acordo com os blocos de conteúdo da história, para facilitar sua leitura. 📖➡️"
        )
        options = {
            "title": "Menu",
            "rows": [
                {
                    "title": "Continuar",
                    "id": ContinueChapter.__name__,
                    "description": "Continuar sua Leitura de onde parou.",
                },
                {"title": "Capítulo 1", "id": ChapterOne.__name__},
                {"title": "Capítulo 2", "id": ChapterTwo.__name__},
                {"title": "Capítulo 3", "id": ChapterThree.__name__},
                {"title": "Capítulo 4", "id": ChapterFour.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Ver", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


@user_bp.register()
class IntroMenuExercises(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Painel de Exercícios"
        body = (
            "Este é o painel de Exercícios 🧠.\n"
            "Cada capítulo possui um exercício para que você possa testar seu conhecimento sobre o conteúdo apresentado."
        )
        options = {
            "title": "Menu",
            "rows": [
                {
                    "title": "Continuar",
                    "id": ContinueExercise.__name__,
                    "description": "Continuar a partir do seu ultimo exercício.",
                },
                {"title": "Exercício 1", "id": ExerciseOne.__name__},
                {"title": "Exercício 2", "id": ExerciseTwo.__name__},
                {"title": "Exercício 3", "id": ExerciseThree.__name__},
                {"title": "Exercício 4", "id": ExerciseFour.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Ver", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


# --- Menu ---
@user_bp.register()
class Menu(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Menu Inicial"
        body = (
            "Este é o menu (ou painel de controle) ⚙️, "
            "onde você, o usuário, pode conferir suas informações "
            "pessoais 👤 ou navegar para outros menus.\n Temos, por exemplo:\n"
            "* A seção de Capítulos 📚: para você escolher de onde continuar sua leitura.\n"
            "* E a seção de Exercícios 🧠: onde você pode praticar o conhecimento adquirido."
        )
        options = {
            "title": "Menu",
            "rows": [
                {"title": "Informações Pessoais", "id": PersonalInfoMenu.__name__},
                {"title": "Capítulos", "id": MenuChapters.__name__},
                {"title": "Exercícios", "id": MenuExercises.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Ver", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


# --- Personal Info ---
@user_bp.register()
class PersonalInfoMenu(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        chapter = user.chapter_grade
        exercise = user.exercise_grade

        flow_action_data = {
            "Nome": user.formatted_name,
            "Sobrenome": user.last_name,
            "Email": user.email,
            "Aniversrio": user.birthday,
            "Sobre_Voce": user.summary,
            "Chapter_One": chapter.get("C1"),
            "Chapter_Two": chapter.get("C2"),
            "Chapter_Three": chapter.get("C3"),
            "Chapter_Four": chapter.get("C4"),
            "Exercise_One": exercise.get("E1"),
            "Exercise_Two": exercise.get("E2"),
            "Exercise_Three": exercise.get("E3"),
            "Exercise_Four": exercise.get("E4"),
        }

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_personal_info",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_action_data_payload=flow_action_data,
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user.current_step = self.next
        await self.db_session.commit()


# --- Chapters ---
@user_bp.register()
class MenuChapters(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Painel Capítulos"
        body = (
            "Aqui, você poderá fazer a leitura do conto "
            "*Negrinha*, de *Monteiro Lobato*."
        )
        options = {
            "title": "Menu",
            "rows": [
                {
                    "title": "Continuar",
                    "id": ContinueChapter.__name__,
                    "description": "Continuar sua Leitura de onde parou.",
                },
                {"title": "Capítulo 1", "id": ChapterOne.__name__},
                {"title": "Capítulo 2", "id": ChapterTwo.__name__},
                {"title": "Capítulo 3", "id": ChapterThree.__name__},
                {"title": "Capítulo 4", "id": ChapterFour.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Ver", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


@user_bp.register()
class ContinueChapter(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        self.next = user.current_chapter  # type: ignore
        self.jump = True


@user_bp.register()
class ChapterOne(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_parte_1",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_chapter = self.__class__.__name__
        await self.db_session.commit()


@user_bp.register()
class ChapterTwo(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_mininisterio_parte_2",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_chapter = self.__class__.__name__
        await self.db_session.commit()


@user_bp.register()
class ChapterThree(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_parte_3",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_chapter = self.__class__.__name__
        await self.db_session.commit()


@user_bp.register()
class ChapterFour(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_parte_4",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_chapter = self.__class__.__name__
        await self.db_session.commit()


# --- Exercises ---
@user_bp.register()
class MenuExercises(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        header = "Painel de Exercícios"
        body = "Cada capítulo possui um exercício para que você possa testar seu conhecimento."
        options = {
            "title": "Menu",
            "rows": [
                {
                    "title": "Continuar",
                    "id": ContinueExercise.__name__,
                    "description": "Continuar a partir do seu ultimo exercício.",
                },
                {"title": "Exercício 1", "id": ExerciseOne.__name__},
                {"title": "Exercício 2", "id": ExerciseTwo.__name__},
                {"title": "Exercício 3", "id": ExerciseThree.__name__},
                {"title": "Exercício 4", "id": ExerciseFour.__name__},
            ],
        }

        message = InteractiveListMessage(to=wa_id, button_name="Ver", body_text=body)
        message.add_header(header)
        message.add_section(options)

        await message.send(self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        await self.db_session.commit()


@user_bp.register()
class ContinueExercise(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        self.next = user.current_exercise  # type: ignore
        self.jump = True


@user_bp.register()
class ExerciseOne(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_exercicios_parte_1",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_exercise = self.__class__.__name__
        await self.db_session.commit()


class ExerciseOneChoice:
    def __init__(
        self, client_session: ClientSession, async_session: AsyncSession, wa_id: str
    ) -> None:
        self.client_session = client_session
        self.async_session = async_session
        self.wa_id = wa_id

    async def handle_choice(self, answer: str):
        next_call = Retry.__name__
        user = await get_user(self.async_session, self.wa_id)
        if not user:
            return
        user.exercise_grade["E1"] = "❎"  # type: ignore
        flag_modified(user, "exercise_grade")  # SQL Alchemy has problems with JSON
        await self.async_session.commit()
        match answer:
            case "a":
                message_content = self.choice_a()
            case "b":
                message_content = self.choice_b()
            case "c":
                message_content = self.choice_c()
                next_call = ChapterTwo.__name__
                user.current_exercise = ExerciseTwo.__name__
                user.exercise_grade["E1"] = "✅"  # type: ignore
            case "d":
                message_content = self.choice_d()
            case _:
                message_content = "Não aparenta ser uma resposta valida"
        flag_modified(user, "exercise_grade")  # SQL Alchemy has problems with JSON
        await self.async_session.commit()
        message = TextMessage(to=self.wa_id, body_text=message_content)
        await message.send(self.client_session)

        return next_call

    def choice_a(self):
        return (
            "*Por que está errada*: Esta alternativa é o oposto do que o texto descreve. D. Inácia "
            '"não gostava de crianças", Negrinha vivia "sempre escondida", era constantemente maltratada '
            '("Batiam nele os da casa, todos os dias") e a patroa sentia prazer em seus castigos '
            '("Ai! Como alivia a gente uma boa roda de cocres bem fincados!..."). '
            "Não há qualquer indício de empatia ou busca pelo bem-estar de Negrinha."
        )

    def choice_b(self):
        return (
            "*Por que está errada*: Embora D. Inácia seja descrita como "
            '"amimada pelos padres, com lugar certo na igreja e camarote de luxo no céu" '
            'e o padre a chame de "dama de grandes virtudes apostólicas", '
            "suas ações contradizem frontalmente qualquer noção de igualdade ou compaixão. "
            "Ela destrata Negrinha, sente prazer na crueldade e tem preconceito "
            '("essa indecência de negro igual a branco"). Sua religiosidade é uma fachada para sua hipocrisia.'
        )

    def choice_c(self):
        return (
            "*Por que está correta*: O texto é repleto de exemplos que sustentam esta afirmação. "
            "A crueldade é evidente nos castigos infligidos a Negrinha (apelidos, agressões físicas, "
            "o episódio do ovo quente). O sadismo é perceptível no prazer que D. Inácia sente ao torturar "
            '("gozando-se na prelibação da tortura", "Como alivia a gente uma boa roda de cocres"). '
            'A hipocrisia se manifesta na sua imagem pública de "excelente senhora", "virtuosa", "esteio da religião", '
            "contrastando com seu comportamento privado. "
            "A fachada de virtude é mantida pela sua posição social e pela conivência do vigário."
        )

    def choice_d(self):
        return (
            'Por que está errada: A primeira parte da afirmação ("impaciência com o choro") '
            'é verdadeira ("Mas não admitia choro de criança. Ai! Punha-lhe os nervos em carne viva"). '
            'No entanto, a segunda parte ("cuidado geral para que Negrinha não sofresse abusos físicos graves") '
            "é completamente falsa. O texto descreve detalhadamente os abusos físicos: "
            '"O corpo de Negrinha era tatuado de sinais roxos, cicatrizes, vergões. Batiam nele os da casa, todos os dias...", '
            "além do sádico episódio do ovo quente."
        )


@user_bp.register()
class ExerciseTwo(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mpv_ministerio_exercicios_parte_2",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_exercise = self.__class__.__name__
        await self.db_session.commit()


class ExerciseTwoChoice:
    def __init__(
        self, client_session: ClientSession, async_session: AsyncSession, wa_id: str
    ) -> None:
        self.client_session = client_session
        self.async_session = async_session
        self.wa_id = wa_id

    async def handle_choice(self, answer: str):
        next_call = Retry.__name__
        user = await get_user(self.async_session, self.wa_id)
        if not user:
            return
        user.exercise_grade["E2"] = "❎"  # type: ignore
        # SQL Alchemy has problems with JSON
        match answer:
            case "a":
                message_content = self.choice_a()
            case "b":
                message_content = self.choice_b()
            case "c":
                message_content = self.choice_c()
                next_call = ChapterThree.__name__
                user.current_exercise = ExerciseThree.__name__
                user.exercise_grade["E2"] = "✅"  # type: ignore
            case "d":
                message_content = self.choice_d()
            case _:
                message_content = "Não aparenta ser uma resposta valida"
        flag_modified(user, "exercise_grade")
        await self.async_session.commit()
        message = TextMessage(to=self.wa_id, body_text=message_content)
        await message.send(self.client_session)

        return next_call

    def choice_a(self):
        return (
            "*Por que está errada*: O medo é uma emoção constante na vida de Negrinha, "
            "e ela de fato sente medo da reação de D. Inácia ao ser flagrada com a boneca "
            '("Ao percebê-la na sala, Negrinha tremera..."). Contudo, sua primeira reação ao ver a boneca '
            "em si não é de medo do objeto, mas de fascínio. O texto diz: "
            '"Que maravilha! (...) Negrinha arregalava os olhos. Nunca imaginara coisa assim, tão galante."'
        )

    def choice_b(self):
        return (
            "Por que está errada: A reação de Negrinha é o oposto da indiferença. "
            'O texto usa termos como "maravilha", "arregalava os olhos", "êxtase", "extasiada". '
            'Embora ela não soubesse o nome "boneca" inicialmente '
            '("Nunca vira uma boneca e nem sequer sabia o nome desse brinquedo"), '
            'ela "compreendeu que era uma criança artificial", o que demonstra uma '
            "compreensão intuitiva e encantada, não indiferença."
        )

    def choice_c(self):
        return (
            "Por que está correta: O texto descreve explicitamente essa reação: "
            '"Que maravilha! (...) Negrinha arregalava os olhos." "Era de êxtase, o olhar de Negrinha." '
            '"Nunca vira uma boneca (...). Mas compreendeu que era uma criança artificial. - É feita??... perguntou extasiada." '
            "Essas passagens mostram o deslumbramento e a surpresa maravilhada de Negrinha diante do brinquedo."
        )

    def choice_d(self):
        return (
            "Por que está errada: O texto não aponta para sentimentos de raiva ou inveja em relação à "
            "boneca naquele momento. A dor da desigualdade é mencionada antes "
            '("Mas logo a dura lição da desigualdade humana chicoteou sua alma"), quando '
            "vê as meninas brincando livremente. Mas a reação específica à boneca é de puro "
            "fascínio e encantamento, não de emoções negativas direcionadas ao objeto ou às meninas por possuí-lo."
        )


@user_bp.register()
class ExerciseThree(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_exercicios_parte_3",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_exercise = self.__class__.__name__
        await self.db_session.commit()


class ExerciseThreeChoice:
    def __init__(
        self, client_session: ClientSession, async_session: AsyncSession, wa_id: str
    ) -> None:
        self.client_session = client_session
        self.async_session = async_session
        self.wa_id = wa_id

    async def handle_choice(self, answer: str):
        next_call = Retry.__name__
        user = await get_user(self.async_session, self.wa_id)
        if not user:
            return
        user.exercise_grade["E3"] = "❎"  # type: ignore
        match answer:
            case "a":
                message_content = self.choice_a()
            case "b":
                message_content = self.choice_b()
                next_call = ChapterFour.__name__
                user.current_exercise = ExerciseFour.__name__
                user.exercise_grade["E3"] = "✅"  # type: ignore
            case "c":
                message_content = self.choice_c()
            case "d":
                message_content = self.choice_d()
            case _:
                message_content = "Não aparenta ser uma resposta valida"
        flag_modified(user, "exercise_grade")  # SQL Alchemy has problems with JSON
        await self.async_session.commit()
        message = TextMessage(to=self.wa_id, body_text=message_content)
        await message.send(self.client_session)

        return next_call

    def choice_a(self):
        return (
            "Por que está errada: Não há nenhuma indicação no texto de que Negrinha tenha "
            "passado a fazer exigências. Sua transformação é interna e leva a uma melancolia posterior, "
            "não a um confronto ou reivindicação por melhores condições ou mais brinquedos."
        )

    def choice_b(self):
        return (
            "Por que está correta: O narrador afirma isso de forma direta e enfática: "
            '"Negrinha, coisa humana, percebeu nesse dia da boneca que tinha alma." '
            'E continua: "Divina eclosão! Surpresa maravilhosa do mundo que ela trazia em si, '
            "e que desabrochava, afinal, como fulgurante flor de luz. Sentiu-se elevada à altura "
            "de ser humano. Cessara de ser coisa e de ora avante lhe seria impossível viver a "
            'vida de coisa." Essa é a transformação central descrita.'
        )

    def choice_c(self):
        return (
            "Por que está errada: A transformação de Negrinha não se manifesta como "
            "rebeldia ativa. Pelo contrário, após a partida das meninas, ela "
            '"caíra numa tristeza infinita", tornando-se "nostálgica, cismarenta". '
            "A mudança é uma introspecção dolorosa, não um desafio externo."
        )

    def choice_d(self):
        return (
            "Por que está errada: O texto menciona um momento de gratidão "
            '("Se a gratidão sorriu na vida, alguma vez, foi naquela surrada carinha..."). '
            "No entanto, não há indicação de que ela esqueceu os maus-tratos, nem que sua visão sobre "
            "D. Inácia mudou permanentemente para uma de pura gratidão. A consequência mais profunda "
            'e duradoura, como explicitado pelo narrador, foi a "descoberta da alma" e a subsequente '
            'impossibilidade de retornar ao seu estado anterior de existência como "coisa".'
        )


@user_bp.register()
class ExerciseFour(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return

        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = TemplateMessage(
            to=wa_id,
            template_name="mvp_ministerio_exercicios_parte_4",
            has_static_header=True,
            has_flow_button=True,
            flow_button_index="0",
            flow_token=self.__class__.__name__,
        )
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_exercise = self.__class__.__name__
        await self.db_session.commit()


class ExerciseFourChoice:
    def __init__(
        self, client_session: ClientSession, async_session: AsyncSession, wa_id: str
    ) -> None:
        self.client_session = client_session
        self.async_session = async_session
        self.wa_id = wa_id

    async def handle_choice(self, answer: str):
        next_call = Retry.__name__
        user = await get_user(self.async_session, self.wa_id)
        if not user:
            return
        user.exercise_grade["E4"] = "❎"  # type: ignore
        match answer:
            case "a":
                message_content = self.choice_a()
            case "b":
                message_content = self.choice_b()
            case "c":
                message_content = self.choice_c()
                next_call = VerifyCongratulations.__name__
                user.current_exercise = ExerciseFour.__name__
                user.exercise_grade["E4"] = "✅"  # type: ignore
            case "d":
                message_content = self.choice_d()
            case _:
                message_content = "Não aparenta ser uma resposta valida"
        flag_modified(user, "exercise_grade")  # SQL Alchemy has problems with JSON
        await self.async_session.commit()
        message = TextMessage(to=self.wa_id, body_text=message_content)
        await message.send(self.client_session)

        return next_call

    def choice_a(self):
        return (
            "Por que está errada: O texto sugere o contrário: "
            '"D. Inácia, pensativa, já a não atenazava tanto...". Isso indica uma diminuição, '
            "e não uma intensificação, da crueldade direta da patroa, embora isso não "
            "fosse suficiente para salvar Negrinha."
        )

    def choice_b(self):
        return (
            'Por que está errada: Embora o texto mencione que "uma febre veio e a levou" '
            'e que ela definhou "como roída de invisível doença consuntora", a causa fundamental '
            "de seu definhamento não é primariamente uma doença física externa, mas a consequência de "
            'sua transformação interna. A "doença" física é apresentada como resultado do seu estado '
            "de profunda tristeza e da perda da alegria que experimentara."
        )

    def choice_c(self):
        return (
            "Por que está correta: Esta alternativa capta a essência da tragédia de Negrinha. "
            'O texto afirma: "Só não voltou a si Negrinha. Sentia-se outra, inteiramente transformada." '
            'E crucialmente: "Aquele dezembro de férias, luminosa rajada de céu trevas adentro de '
            'seu doloroso inferno, envenenara-a." E antes, na Parte 3, o narrador já havia antecipado: '
            '"Assim foi, e essa consciência a matou." A experiência da alegria e da humanidade, seguida '
            'pela sua perda abrupta, tornou a vida anterior insuportável para sua "alma, com um mês de vida apenas".'
        )

    def choice_d(self):
        return (
            "Por que está errada: Fome e frio sempre foram constantes na vida de Negrinha. "
            'O texto diz que ela "Mal comia", mas isso é apresentado como uma consequência de '
            'sua "tristeza infinita", não como a causa primária de seu definhamento. Além disso, '
            'menciona-se que "na cozinha uma criada nova, boa de coração, amenizava-lhe a vida", '
            "o que sugere que, em alguns aspectos, suas condições físicas imediatas poderiam até ter "
            "melhorado levemente, mas seu sofrimento era de outra ordem, mais profunda."
        )


# --- Extra ---
@user_bp.register()
class VerifyCongratulations(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        user = await get_user(self.db_session, wa_id)
        if not user:
            return

        chapter = user.chapter_grade
        exercise = user.exercise_grade
        chapter_ok = True
        exercise_ok = True
        for value_1, value_2 in zip(chapter.values(), exercise.values()):
            if value_1 == "❎":
                chapter_ok = False
            if value_2 == "❎":
                exercise_ok = False

        self.jump = True
        self.next = NotCongratulations.__name__

        if chapter_ok and exercise_ok:
            self.next = Congratulations.__name__


@user_bp.register()
class Congratulations(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = "Parabens!"

        message = TextMessage(to=wa_id, body_text=message)
        await message.send(client_session=self.client_session)

        self.next = Redirecter.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_exercise = self.__class__.__name__
        await self.db_session.commit()


@user_bp.register()
class NotCongratulations(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        contatc = contatcs[0]
        wa_id = contatc.wa_id

        message = "Alguns parametros ou exercicios não foram completados"

        message = TextMessage(to=wa_id, body_text=message)
        await message.send(client_session=self.client_session)

        self.next = Menu.__name__
        user = await get_user(self.db_session, wa_id)
        if not user:
            return
        user.current_step = self.next
        user.current_exercise = self.__class__.__name__
        await self.db_session.commit()


@user_bp.register()
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

        prompt = {
            "Instructions": (
                "Você é um bot do WhatsApp Business para a empresa Estum. "
                "Seu proposito hoje é servir como uma demonstração viavel, de como o ensino a "
                "distancia pode ser beneficiado por um metodo gameficado, onde conteudos são servidos "
                "gradualmente com 'check points'. Você recebera o prompt do user e algumas informações "
                "de usuario. Nesta demonstração estamos fazendo uma analise do conto de Monteiro Lobato 'Negrinha'. "
                "matenha as responsas curtas, você não precisa se introduzir toda hora. Fale apenas o necessário. "
                "cuidado com o termo 'negrinha', é um termo pejurativo, o objetivo aqui é educar. "
                "Dividimos o conto em 4 capitulos, ❎ signifca que não leu ou não respondeu certo, ✅ significa que leu "
                "ou respondeu certo."
            ),
            "User_prompt": message_content,
            "User_info": {
                "Name": user.formatted_name,
                "Last_name": user.last_name,
                "Birthday": user.birthday,
                "email": user.email,
                "About_user": user.summary,
                "Chapter user has read": user.chapter_grade,
                "Correct exercises user has answered": user.exercise_grade,
                "Past User prompt and answer": user.past_question,
            },
        }

        prompt_redirect = {
            "Intruction": (
                "Seu objetio é redirecionar o usuario de acordo com o que ele desejar, "
                "vem aqui uma lista dos redirecionadores, voce deve analizar o que o usuario deseja. "
                "Retorne em formato de dicionario (Json) a opção desejada, não esqueça do jump."
            ),
            "User_input": message_content,
            "Redirect_Names_and_description": [
                {
                    "redirecter": Redirecter.__name__,
                    "description": (
                        "Se o user não pedir nada sempre retorne este por default. "
                        "Se não souber retorne este. Se o usuario não pediu nada, retorna este. "
                        "Uma resposta como 'oi', ou conversa basica."
                    ),
                    "jump": False,
                },
                {
                    "redirecter": Menu.__name__,
                    "description": "Menu com informações principais",
                    "jump": True,
                },
                {
                    "redirecter": MenuChapters.__name__,
                    "description": "Menu com o conteudo dos capitulos",
                    "jump": True,
                },
                {
                    "redirecter": ChapterOne.__name__,
                    "description": "Capitulo 1",
                    "jump": True,
                },
                {
                    "redirecter": ChapterTwo.__name__,
                    "description": "Capitulo 2",
                    "jump": True,
                },
                {
                    "redirecter": ChapterThree.__name__,
                    "description": "Capitulo 3",
                    "jump": True,
                },
                {
                    "redirecter": ChapterFour.__name__,
                    "description": "Capitulo 4",
                    "jump": True,
                },
                {
                    "redirecter": MenuExercises.__name__,
                    "description": "Menu com o conteudo dos exercicios.",
                    "jump": True,
                },
                {
                    "redirecter": ExerciseOne.__name__,
                    "description": "Exercicio 1",
                    "jump": True,
                },
                {
                    "redirecter": ExerciseTwo.__name__,
                    "description": "exercicio 2",
                    "jump": True,
                },
                {
                    "redirecter": ExerciseThree.__name__,
                    "description": "Exercicio 3",
                    "jump": True,
                },
                {
                    "redirecter": ExerciseFour.__name__,
                    "description": "Exercicio 4",
                    "jump": True,
                },
                {
                    "redirecter": PersonalInfoMenu.__name__,
                    "Description": (
                        "Menu com a nota do individuo e informações "
                        "como email, nome, o usuario pode alterar"
                    ),
                    "jump": True,
                },
            ],
        }

        prompt = str(
            prompt
        )  # HACK: Json will fuck all the unicode and the stupid ai wont be able to understand.
        prompt_redirect = json.dumps(prompt_redirect)

        ai_content = await get_ai_response(
            client_session=self.client_session, prompt=prompt, timeout_seconds=10
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
            redirect_function_name = ai_redirect_dic.get(
                "redirecter", Redirecter.__name__
            )
            jumps = ai_redirect_dic.get("jump", False)
        else:
            redirect_function_name = Redirecter.__name__
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
        user.current_exercise = self.__class__.__name__
        await self.db_session.commit()
