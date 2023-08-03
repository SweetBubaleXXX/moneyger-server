from django_filters import BooleanFilter, DateTimeFromToRangeFilter, RangeFilter
from django_filters import rest_framework as filters

from .models import Transaction, TransactionCategory


class TransactionCategoryFilter(filters.FilterSet):
    not_subcategory = BooleanFilter(field_name="parent_category", lookup_expr="isnull")

    class Meta:
        model = TransactionCategory
        fields = ("transaction_type", "icon", "color")


class TransactionFilter(filters.FilterSet):
    amount = RangeFilter("amount")
    transaction_time = DateTimeFromToRangeFilter("transaction_time")

    class Meta:
        model = Transaction
        fields = (
            "category__transaction_type",
            "currency",
        )
