from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.dialects.sqlite import JSON

from models import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    ai_config = Column(JSON, default=dict)
    plugin_config = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
