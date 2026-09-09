from sqlalchemy import Column, Integer, String, ForeignKey

from models import Base


class PricingSubCategory(Base):
    __tablename__ = "pricing_sub_category"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("pricing_category.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
