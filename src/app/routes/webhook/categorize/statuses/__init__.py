from typing import Union

from app.routes.webhook.categorize.statuses.sent import StatusSent
from app.routes.webhook.categorize.statuses.read import StatusRead
from app.routes.webhook.categorize.statuses.delivered import StatusDelivered
from app.routes.webhook.categorize.statuses.failed import StatusFailed





Status = Union[StatusSent, StatusDelivered, StatusRead, StatusFailed]