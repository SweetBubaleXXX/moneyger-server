from typing import NamedTuple

from rest_framework import serializers

from ..transactions.models import Transaction, TransactionCategory


class TransacationCsvSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    amount = serializers.DecimalField(
        source="amount_decimal", max_digits=15, decimal_places=None
    )
    transaction_type = serializers.CharField(source="category.transaction_type")

    class Meta:
        model = Transaction
        fields = (
            "category",
            "transaction_type",
            "currency",
            "amount",
            "transaction_time",
            "comment",
        )


class TransactionJsonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "currency",
            "amount",
            "transaction_time",
            "comment",
        )


class _ParsedCategory(NamedTuple):
    instance: TransactionCategory
    transactions: list[dict]


def _create_transactions(parsed_category: _ParsedCategory):
    return Transaction.objects.bulk_create(
        Transaction(
            account=parsed_category.instance.account,
            category=parsed_category.instance,
            **transaction_data,
        )
        for transaction_data in parsed_category.transactions
    )


class CategoryListJsonSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        account = self.context["account"]
        parsed_categories: list[_ParsedCategory] = []
        for category_data in validated_data:
            transactions = category_data.pop("transactions")
            category_instance = TransactionCategory(
                account=account,
                **category_data,
            )
            parsed_categories.append(_ParsedCategory(category_instance, transactions))
        TransactionCategory.objects.bulk_create(
            category.instance for category in parsed_categories
        )
        for category in parsed_categories:
            _create_transactions(category)
        return parsed_categories


class _RecursiveField(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class CategoryJsonSerializer(serializers.ModelSerializer):
    subcategories = _RecursiveField(many=True, read_only=True)
    transactions = TransactionJsonSerializer(many=True)

    class Meta:
        model = TransactionCategory
        list_serializer_class = CategoryListJsonSerializer
        fields = (
            "transaction_type",
            "name",
            "display_order",
            "icon",
            "color",
            "subcategories",
            "transactions",
        )

    def create(self, validated_data):
        account = self.context["account"]
        transactions = validated_data.pop("transactions")
        category = TransactionCategory.objects.create(account=account, **validated_data)
        _create_transactions(_ParsedCategory(category, transactions))
        return category
