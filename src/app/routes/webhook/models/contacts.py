from pydantic import BaseModel


class Profile(BaseModel):
    name: str

class Contact(BaseModel):
    profile: Profile
    wa_id: str