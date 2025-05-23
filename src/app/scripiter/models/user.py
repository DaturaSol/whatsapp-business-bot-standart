from logging import getLogger

from app.scripiter import ScriptBlueprint, ScriptBaseModel
from app.client_session.messages.models.text import TextMessage

log = getLogger(__name__)

user_bp = ScriptBlueprint()


@user_bp.register()
class HelloUser(ScriptBaseModel):
    async def _fn(self):
        messages = self.value.messages
        if not messages:
            return

        message = messages[0]
        log.info(message)

        self.next = TestAfterHelloUser.__name__
        self.jump = True

@user_bp.register()
class TestAfterHelloUser(ScriptBaseModel):
    async def _fn(self):
        contatcs = self.value.contacts
        if not contatcs:
            return
        
        contatc = contatcs[0]
        wa_id = contatc.wa_id
        
        message  = TextMessage(to=wa_id, body_text="Ola funcina")
        await message.send(client_session=self.client_session)
        