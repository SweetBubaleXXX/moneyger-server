# Generated by Django 4.2.3 on 2023-08-01 14:44

from django.db import migrations


def remove_nulled_categories(apps, schema_editor):
    Transaction = apps.get_model("core", "Transaction")
    Transaction.objects.filter(category__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_historicaltransaction_account_transaction_account_and_more"),
    ]

    operations = [migrations.RunPython(remove_nulled_categories)]
