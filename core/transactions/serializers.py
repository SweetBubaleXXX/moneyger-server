from rest_framework import serializers

from .models import TransactionCategory


class TransactionCategorySerializer(serializers.ModelSerializer):
    child_categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

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
            "child_categories",
        )
        read_only_fields = ("parent_category",)


class TransactionCategoryUpdateSerializer(TransactionCategorySerializer):
    class Meta(TransactionCategorySerializer.Meta):
        read_only_fields = TransactionCategorySerializer.Meta.read_only_fields + (
            "transaction_type",
        )
