from django.contrib import admin

from .transactions.admin import TransactionAdmin, TransactionCategoryAdmin
from .transactions.models import Transaction, TransactionCategory

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionCategory, TransactionCategoryAdmin)
