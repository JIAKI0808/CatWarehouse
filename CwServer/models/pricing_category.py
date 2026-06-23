from sqlalchemy import Column, Integer, String

from models import Base


class PricingCategory(Base):
    __tablename__ = "pricing_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, default="")
