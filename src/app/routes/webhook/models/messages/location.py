from pydantic import BaseModel

from app.routes.webhook.models.messages.base import  BaseMessageModel

class LocationObject(BaseModel):
    latitude: str
    longitude: str
    name: str
    address: str


class LocationMessage(BaseMessageModel):
    location: LocationObject
