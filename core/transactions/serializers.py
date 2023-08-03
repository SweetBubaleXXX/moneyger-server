from rest_framework import serializers

from .models import TransactionCategory


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
