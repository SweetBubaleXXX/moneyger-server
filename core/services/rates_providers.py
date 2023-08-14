from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Generic, TypeVar

import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework import status

from ..constants import CurrencyCode

T = TypeVar("T")


class FetchRatesException(BaseException):
    def __init__(self, url: str | None = None) -> None:
        if url:
            message = "Failed to fetch rates"
        else:
            message = f"Failed to fetch rates from {url}"
        super().__init__(message)


class BaseRates(Generic[T], metaclass=ABCMeta):
    supported_currencies: Iterable[str] = CurrencyCode.values

    @classmethod
    def validate_currencies(cls, *args: str) -> None:
        for currency in args:
            if currency not in cls.supported_currencies:
                raise ValueError(f"No rates for {currency}")

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

    def _seconds_to_midnight(self) -> int:
        now = datetime.utcnow()
        midnight = datetime.combine(now + timedelta(days=1), time())
        return (midnight - now).seconds


class AlfaBankNationalRates(BaseRates[dict[str, Decimal]]):
    def fetch_data(self) -> dict[str, Decimal]:
        try:
            res = requests.get(settings.ALFA_BANK_NATIONAL_RATES_URL)
            assert res.status_code == status.HTTP_200_OK
            rates = res.json().get("rates")
            assert rates, "Rates list is empty"
        except (requests.RequestException, AssertionError) as e:
            raise FetchRatesException(settings.ALFA_BANK_NATIONAL_RATES_URL) from e
        return self._parse_rates(rates)

    def get_rate(self, cur_from: CurrencyCode, cur_to: CurrencyCode) -> Decimal:
        self.validate_currencies(cur_from, cur_to)
        if cur_from == cur_to:
            return Decimal(1)
        rates = self.get_data()
        if cur_to is CurrencyCode.BYN:
            return rates[cur_from.value]
        if cur_from is CurrencyCode.BYN:
            return Decimal(1) / rates[cur_to.value]
        rate_to_byn = rates[cur_from.value]
        return rate_to_byn / rates[cur_to.value]

    def _parse_rates(self, rates):
        essential_rates = filter(
            lambda currency: currency["iso"] in CurrencyCode.values,
            rates,
        )
        return {
            currency["iso"]: (
                Decimal(str(currency["rate"])) / Decimal(currency["quantity"])
            )
            for currency in essential_rates
        }
