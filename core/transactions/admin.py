from django.contrib import admin


class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "name", "transaction_type")
    ordering = ("account", "transaction_type", "name")
    search_fields = ("name",)
    list_filter = ("transaction_type", "account")


class TransactionAdmin(admin.ModelAdmin):
    ordering = ("-transaction_time",)
    list_display = (
        "id",
        "account",
        "category",
        "currency",
        "amount_decimal",
        "transaction_time",
    )
    list_filter = ("transaction_time", "account")
