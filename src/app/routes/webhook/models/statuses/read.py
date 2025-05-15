from typing import Literal

from app.routes.webhook.models.statuses.base import StatusesBaseModel

class StatusRead(StatusesBaseModel):
    status: Literal["read"]