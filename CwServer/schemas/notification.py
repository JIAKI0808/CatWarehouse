from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    is_read: bool
    created_at: datetime
    related_id: int | None

    model_config = {"from_attributes": True}
