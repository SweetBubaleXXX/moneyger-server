from rest_framework import serializers

from .models import Transaction, TransactionCategory


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


class TransactionSerializer(serializers.ModelSerializer):
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
        read_only_fields = ("category",)
