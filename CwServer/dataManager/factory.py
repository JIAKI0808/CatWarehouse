from sqlalchemy.ext.asyncio import AsyncSession

from dataManager.base import DataManagerFactory
from dataManager.inventory.factory import InventoryManagerFactory

_factories: dict[str, type[DataManagerFactory]] = {
    "inventory": InventoryManagerFactory,
}


def register_factory(name: str, factory_cls: type[DataManagerFactory]):
    _factories[name] = factory_cls


def get_factory(name: str, db: AsyncSession) -> DataManagerFactory:
    factory_cls = _factories.get(name)
    if factory_cls is None:
        raise ValueError(f"Unknown factory: {name}")
    return factory_cls(db)
