from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models import Base


class SubCategory(Base):
    __tablename__ = "sub_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    unit = Column(String, default="个")
    description = Column(String, default="")
    notes = Column(String, default="")
    extra = Column(String, default="{}")

    category = relationship("Category", back_populates="sub_categories")
    specific_items = relationship("SpecificItem", back_populates="sub_category")
