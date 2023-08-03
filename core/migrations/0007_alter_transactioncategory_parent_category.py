# Generated by Django 4.2.3 on 2023-08-03 07:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_alter_transaction_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transactioncategory",
            name="parent_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subcategories",
                to="core.transactioncategory",
            ),
        ),
    ]
