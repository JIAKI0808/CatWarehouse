from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime

from models import Base


class RecurringBill(Base):
    __tablename__ = "recurring_bill"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, default="")
    platform = Column(String, default="")
    person = Column(String, default="")
    type = Column(String, nullable=False, default="expense")
    frequency = Column(String, nullable=False, default="monthly")
    next_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
