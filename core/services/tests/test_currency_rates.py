from django.core.cache import cache
from django.test import TestCase


class CacheClearTestCase(TestCase):
    def tearDown(self):
        cache.clear()


class AlfaBankNationRatesTestCase(CacheClearTestCase):
    pass
