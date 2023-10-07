from decimal import Decimal

from rest_framework import serializers

from .models import Transaction, TransactionCategory
from ..constants import CurrencyCode


class TransactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCategory
        fields = (
            "id",
            "parent_category",
            "transaction_type",
            "name",
            "display_order",
            "icon",
            "color",
        )
        read_only_fields = ("parent_category",)


class TransactionCategoryUpdateSerializer(TransactionCategorySerializer):
    class Meta(TransactionCategorySerializer.Meta):
        read_only_fields = TransactionCategorySerializer.Meta.read_only_fields + (
            "transaction_type",
        )


class PositiveDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        if Decimal(data) <= 0:
            raise serializers.ValidationError("Ensure this value is greater than 0.")
        return super().to_internal_value(data)


class TransactionSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(source="category_id", read_only=True)
    amount = PositiveDecimalField(
        source="amount_decimal", max_digits=15, decimal_places=None
    )
    transaction_type = serializers.ReadOnlyField(source="category.transaction_type")

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category",
            "transaction_type",
            "amount",
            "currency",
            "comment",
            "transaction_time",
        )


class TransactionUpdateSerializer(TransactionSerializer):
    category = serializers.IntegerField(
        source="category_id", read_only=False, required=False
    )

    def validate_category(self, value):
        if self.instance is None:
            raise serializers.ValidationError()
        try:
            category = TransactionCategory.objects.get(pk=value)
            assert category.account == self.instance.account
        except (TransactionCategory.DoesNotExist, AssertionError):
            raise serializers.ValidationError("Invalid category id.")
        return value


class SummarySerializer(serializers.Serializer):
    total = serializers.FloatField()
    currency = serializers.ChoiceField(choices=CurrencyCode.choices)


class CategorySummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    total = serializers.FloatField()


class StatsSerializer(SummarySerializer):
    categories = serializers.ListField(child=CategorySummarySerializer())
