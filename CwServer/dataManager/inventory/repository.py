from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dataManager.base import Repository
from dataManager.inventory.item import Item
from models.specific_item import SpecificItem


class ItemRepository(Repository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Item | None:
        result = await self.db.execute(
            select(SpecificItem).where(SpecificItem.id == id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return Item(
            id=model.id,
            name=model.name,
            sub_category_id=model.sub_category_id,
            price=model.price,
            recorder=model.recorder,
            description=model.description,
        )

    async def get_all(self) -> list[Item]:
        result = await self.db.execute(select(SpecificItem))
        return [
            Item(
                id=m.id,
                name=m.name,
                sub_category_id=m.sub_category_id,
                price=m.price,
                recorder=m.recorder,
                description=m.description,
            )
            for m in result.scalars().all()
        ]

    async def create(self, data: dict) -> Item:
        model = SpecificItem(**data)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return Item(
            id=model.id,
            name=model.name,
            sub_category_id=model.sub_category_id,
            price=model.price,
            recorder=model.recorder,
            description=model.description,
        )

    async def update(self, id: int, data: dict) -> Item | None:
        model = await self.db.get(SpecificItem, id)
        if model is None:
            return None
        for key, value in data.items():
            setattr(model, key, value)
        await self.db.commit()
        await self.db.refresh(model)
        return Item(
            id=model.id,
            name=model.name,
            sub_category_id=model.sub_category_id,
            price=model.price,
            recorder=model.recorder,
            description=model.description,
        )

    async def delete(self, id: int) -> bool:
        model = await self.db.get(SpecificItem, id)
        if model is None:
            return False
        await self.db.delete(model)
        await self.db.commit()
        return True
