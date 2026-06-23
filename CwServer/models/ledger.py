from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from models import Base


class Ledger(Base):
    __tablename__ = "ledger"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)
    platform = Column(String, default="")
    description = Column(String, default="")
    notes = Column(String, default="")
    person = Column(String, default="")
    type = Column(String, nullable=False, default="expense")  # income / expense
