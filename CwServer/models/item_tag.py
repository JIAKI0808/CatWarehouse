from sqlalchemy import Column, Integer, ForeignKey

from models import Base


class ItemTag(Base):
    __tablename__ = "item_tag"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("specific_items.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False)
