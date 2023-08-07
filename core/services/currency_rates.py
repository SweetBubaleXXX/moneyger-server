from abc import ABCMeta, abstractmethod
from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Generic, TypeVar

import requests
from django.conf import settings
from django.core.cache import cache

from ..constants import CurrencyCode

T = TypeVar("T")


class BaseRates(Generic[T], metaclass=ABCMeta):
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


class AlfaBankNationalRates(BaseRates[dict[str, Decimal]]):
    def fetch_data(self) -> dict[str, Decimal]:
        res = requests.get(settings.ALFA_BANK_NATIONAL_RATES_URL)
        return {
            currency["iso"]: Decimal(currency["rate"]) / Decimal(currency["quantity"])
            for currency in filter(
                lambda currency: currency["iso"] in CurrencyCode.values,
                res.json()["rates"],
            )
        }

    def get_rate(self, cur_from: CurrencyCode, cur_to: CurrencyCode) -> Decimal:
        if cur_from == cur_to:
            return Decimal(1)
        rates = self.get_data()
        if cur_to is CurrencyCode.BYN:
            return rates[cur_from.value]
        if cur_from is CurrencyCode.BYN:
            return Decimal(1) / rates[cur_to.value]
        rate_to_byn = rates[cur_from.value]
        return rate_to_byn / rates[cur_to.value]
