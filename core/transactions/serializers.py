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
    category = serializers.IntegerField(source="category_id", read_only=True)
    amount = serializers.DecimalField(
        source="amount_decimal", min_value=0, max_digits=15, decimal_places=None
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
