from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Base.metadata knows about them
from models.category import Category  # noqa: E402, F401
from models.sub_category import SubCategory  # noqa: E402, F401
from models.specific_item import SpecificItem  # noqa: E402, F401
from models.settings import Settings  # noqa: E402, F401
from models.ledger import Ledger  # noqa: E402, F401
from models.budget import Budget  # noqa: E402, F401
from models.notification import Notification  # noqa: E402, F401
from models.tag import Tag  # noqa: E402, F401
from models.item_tag import ItemTag  # noqa: E402, F401
from models.recurring import RecurringBill  # noqa: E402, F401
from models.pricing import Pricing  # noqa: E402, F401
from models.pricing_category import PricingCategory  # noqa: E402, F401
from models.pricing_sub_category import PricingSubCategory  # noqa: E402, F401
