from abc import ABC, abstractmethod
from typing import Any

from src.utils.cache.cache import Cache


class EtagService(ABC):
    def __init__(self) -> None:
        self.cacheService = Cache()
        pass

    @abstractmethod
    def generate_etag_key(self, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def generate_etag(self, *args, **kwargs) -> str:
        pass

    # @abstractmethod
    # def validate_etag_from_cache(self, *args, **kwargs):
    #     pass

    def _get_etag_from_cache(self, etag_key: str) -> str | None:
        result = self.cacheService.get(key=etag_key)
        return result if result else None

    def _set_etag_to_cache(self, etag_key: str, etag: str) -> Any:
        # set time to 10 mins, 3600s
        set = self.cacheService.set(key=etag_key, time=3600, data=etag)
        return set
