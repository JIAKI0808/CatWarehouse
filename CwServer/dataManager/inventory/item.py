from dataManager.base import DataProduct


class Item(DataProduct):
    def __init__(
        self,
        name: str,
        sub_category_id: int,
        price: float = 0.0,
        recorder: str = "",
        description: str = "",
        id: int | None = None,
    ):
        self.id = id
        self.name = name
        self.sub_category_id = sub_category_id
        self.price = price
        self.recorder = recorder
        self.description = description

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "sub_category_id": self.sub_category_id,
            "price": self.price,
            "recorder": self.recorder,
            "description": self.description,
        }
