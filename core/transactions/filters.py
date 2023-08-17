from django_filters import rest_framework as filters

from .models import Transaction, TransactionCategory


class TransactionCategoryFilter(filters.FilterSet):
    not_subcategory = filters.BooleanFilter(
        field_name="parent_category", lookup_expr="isnull"
    )

    class Meta:
        model = TransactionCategory
        fields = ("transaction_type", "icon", "color")


def get_user_categories(request):
    if request is None:
        return TransactionCategory.objects.none()
    return request.user.transactioncategory_set.all()


class TransactionFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(queryset=get_user_categories)
    amount = filters.RangeFilter("amount")
    transaction_time = filters.DateTimeFromToRangeFilter("transaction_time")

    class Meta:
        model = Transaction
        fields = (
            "category__transaction_type",
            "currency",
        )
