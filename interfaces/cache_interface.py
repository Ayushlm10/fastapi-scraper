from abc import ABC, abstractmethod


class CacheInterface(ABC):
    @abstractmethod
    async def get(self, key: str):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int = 3600):
        pass

    @abstractmethod
    async def clear_cache(self) -> None:
        pass
