from sqlalchemy.ext.asyncio import AsyncSession

from dataManager.base import DataManagerFactory, DataProduct, Validator, Repository
from dataManager.inventory.item import Item
from dataManager.inventory.validator import ItemValidator
from dataManager.inventory.repository import ItemRepository


class InventoryManagerFactory(DataManagerFactory):
    def __init__(self, db: AsyncSession):
        self.db = db

    def create_product(self, **kwargs) -> DataProduct:
        return Item(**kwargs)

    def create_validator(self) -> Validator:
        return ItemValidator()

    def create_repository(self) -> Repository:
        return ItemRepository(self.db)
