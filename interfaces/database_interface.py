from abc import ABC, abstractmethod

import api.models as models


class DatabaseInterface(ABC):
    @abstractmethod
    async def add_products(self, products: list[models.Product]) -> int:
        pass

    @abstractmethod
    async def get_all_products(self) -> list[models.Product]:
        pass

    @abstractmethod
    async def clear_all_products(self) -> bool:
        pass
