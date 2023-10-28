from django_filters import rest_framework as filters

from ..constants import TransactionType
from .models import Transaction, TransactionCategory


def get_user_categories(request):
    if request is None:
        return TransactionCategory.objects.none()
    return request.user.transactioncategory_set.all()


class TransactionFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(queryset=get_user_categories)
    transaction_type = filters.ChoiceFilter(
        "category__transaction_type", choices=TransactionType.choices
    )
    transaction_time = filters.DateTimeFromToRangeFilter("transaction_time")

    class Meta:
        model = Transaction
        fields = ("currency",)


class TransactionCategoryFilter(filters.FilterSet):
    parent_category = filters.ModelChoiceFilter(queryset=get_user_categories)
    not_subcategory = filters.BooleanFilter(
        field_name="parent_category", lookup_expr="isnull"
    )

    class Meta:
        model = TransactionCategory
        fields = ("transaction_type", "icon", "color")
