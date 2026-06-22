from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from models import Base


class SpecificItem(Base):
    __tablename__ = "specific_items"

    id = Column(Integer, primary_key=True, index=True)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"), nullable=False)
    name = Column(String, nullable=False)
    entry_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    recorder = Column(String, default="")
    price = Column(Float, default=0.0)
    description = Column(String, default="")
    extra = Column(String, default="{}")

    sub_category = relationship("SubCategory", back_populates="specific_items")
