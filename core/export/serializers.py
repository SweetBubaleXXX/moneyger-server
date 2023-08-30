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


class _RecursiveField(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class CategoryJsonSerializer(serializers.ModelSerializer):
    subcategories = _RecursiveField(many=True)
    transactions = TransactionJsonSerializer(many=True)

    class Meta:
        model = TransactionCategory
        fields = (
            "transaction_type",
            "name",
            "display_order",
            "icon",
            "color",
            "subcategories",
            "transactions",
        )
