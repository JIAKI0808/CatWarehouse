from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, default="")
    extra = Column(String, default="{}")

    sub_categories = relationship("SubCategory", back_populates="category")
