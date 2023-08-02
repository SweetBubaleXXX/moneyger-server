from django_filters import BooleanFilter
from django_filters import rest_framework as filters

from .models import TransactionCategory


class TransactionCategoryFilter(filters.FilterSet):
    not_subcategory = BooleanFilter(field_name="parent_category", lookup_expr="isnull")

    class Meta:
        model = TransactionCategory
        fields = ["transaction_type", "icon", "color"]
