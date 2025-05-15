from pydantic import BaseModel
from typing import Optional, List, Literal

from app.routes.webhook.models.statuses.base import StatusesBaseModel

class ErrorData(BaseModel):
    details: str


class StatusErrorObject(
    BaseModel
):  # Renamed from ErrosObject to avoid clash and fix typo
    code: int  # Changed to int based on example
    title: str
    message: Optional[str] = None
    error_data: Optional[ErrorData] = None
    href: Optional[str] = None


class StatusFailed(StatusesBaseModel):
    status: Literal["failed"]
    errors: List[StatusErrorObject]