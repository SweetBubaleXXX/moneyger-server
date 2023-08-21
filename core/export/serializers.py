from rest_framework import serializers

from ..transactions.models import Transaction


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
