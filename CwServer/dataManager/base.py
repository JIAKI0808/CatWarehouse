from abc import ABC, abstractmethod


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
    async def get(self, id: int):
        ...

    @abstractmethod
    async def get_all(self):
        ...

    @abstractmethod
    async def create(self, data: dict):
        ...

    @abstractmethod
    async def update(self, id: int, data: dict):
        ...

    @abstractmethod
    async def delete(self, id: int):
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
