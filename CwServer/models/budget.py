from sqlalchemy import Column, Integer, String, Float

from models import Base


class Budget(Base):
    __tablename__ = "budget"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM
    amount = Column(Float, nullable=False)
