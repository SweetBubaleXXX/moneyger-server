from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta, time
from decimal import Decimal
from typing import TypeVar

from django.core.cache import cache

from ..constants import CurrencyCode

T = TypeVar("T")


class BaseRates(metaclass=ABCMeta):
    def _seconds_to_midnight(self) -> int:
        now = datetime.utcnow()
        midnight = datetime.combine(now + timedelta(days=1), time())
        return (midnight - now).seconds

    def get_data(self) -> T:
        return cache.get_or_set(
            f"{self.__class__.__name__}_data",
            self.fetch_data,
            self._seconds_to_midnight(),
        )

    @abstractmethod
    def fetch_data(self) -> T:
        pass

    @abstractmethod
    def get_rate(self, cur_from: CurrencyCode, cur_to: CurrencyCode) -> Decimal:
        pass
