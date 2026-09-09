from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from models import Base


class Pricing(Base):
    __tablename__ = "pricing"

    id = Column(Integer, primary_key=True, index=True)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"), nullable=False)
    name = Column(String, nullable=False)
    cost = Column(Float, default=0.0)
    suggested_price = Column(Float, default=0.0)
    discount = Column(Float, default=1.0)
    description = Column(String, default="")
    notes = Column(String, default="")
    record_date = Column(DateTime, server_default=func.now())

    sub_category = relationship("SubCategory", backref="pricing_items")
