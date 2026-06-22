from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Base.metadata knows about them
from models.category import Category  # noqa: E402, F401
from models.sub_category import SubCategory  # noqa: E402, F401
from models.specific_item import SpecificItem  # noqa: E402, F401
