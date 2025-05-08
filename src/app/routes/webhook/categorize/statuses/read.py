from typing import Literal

from app.routes.webhook.categorize.statuses.base import StatusesBaseModel

class StatusRead(StatusesBaseModel):
    status: Literal["read"]