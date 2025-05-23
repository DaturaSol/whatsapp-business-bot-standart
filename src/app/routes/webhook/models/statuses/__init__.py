from typing import Union

from app.routes.webhook.models.statuses.sent import StatusSent
from app.routes.webhook.models.statuses.read import StatusRead
from app.routes.webhook.models.statuses.delivered import StatusDelivered
from app.routes.webhook.models.statuses.failed import StatusFailed


Status = Union[StatusSent, StatusDelivered, StatusRead, StatusFailed]
