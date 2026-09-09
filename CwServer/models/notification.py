from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from models import Base


class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # expiry, budget
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    related_id = Column(Integer, nullable=True)
