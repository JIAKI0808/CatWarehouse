from abc import ABC, abstractmethod
from typing import Any, Sequence


class DataProduct(ABC):
    """Abstract data product created by the factory."""

    @abstractmethod
    def to_dict(self) -> dict:
        ...


class Validator(ABC):
    """Abstract validator for data validation."""

    @abstractmethod
    def validate(self, data: dict) -> bool:
        ...

    @abstractmethod
    def errors(self) -> list[str]:
        ...


class Repository(ABC):
    """Abstract repository for data persistence."""

    @abstractmethod
    async def get(self, id: int) -> Any | None:
        """按主键取一条；不存在返回 None。"""
        ...

    @abstractmethod
    async def get_all(self) -> Sequence[Any]:
        """取全部。"""
        ...

    @abstractmethod
    async def create(self, data: dict) -> Any:
        """新建并返回持久化后的对象。"""
        ...

    @abstractmethod
    async def update(self, id: int, data: dict) -> Any | None:
        """按主键部分更新；不存在返回 None。"""
        ...

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """按主键删除；返回是否真的删掉了。"""
        ...


class DataManagerFactory(ABC):
    """Abstract factory for creating data management components."""

    @abstractmethod
    def create_product(self, **kwargs) -> DataProduct:
        ...

    @abstractmethod
    def create_validator(self) -> Validator:
        ...

    @abstractmethod
    def create_repository(self) -> Repository:
        ...
