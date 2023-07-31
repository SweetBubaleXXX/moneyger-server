# Generated by Django 4.2.3 on 2023-07-28 14:26

import colorfield.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TransactionCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_modified", models.DateTimeField(auto_now=True)),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("IN", "Income"), ("OUT", "Outcome")], max_length=3
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("display_order", models.IntegerField(default=0)),
                ("icon", models.CharField(blank=True, max_length=64, null=True)),
                (
                    "color",
                    colorfield.fields.ColorField(
                        default="#FFFFFF",
                        image_field=None,
                        max_length=18,
                        samples=[
                            ("#ffffff", "white"),
                            ("#ff6b22", "orange"),
                            ("#cddc39", "lime"),
                            ("#b9b9b9", "grey"),
                            ("#af2422", "red"),
                            ("#673ab7", "purple"),
                            ("#4cd964", "green"),
                            ("#2196f3", "blue"),
                            ("#009688", "dark teal"),
                        ],
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent_category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="child_categories",
                        to="core.transactioncategory",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("amount", models.BigIntegerField()),
                (
                    "currency",
                    models.CharField(
                        choices=[
                            ("USD", "Usd"),
                            ("EUR", "Eur"),
                            ("BYN", "Byn"),
                            ("RUB", "Rub"),
                        ],
                        max_length=3,
                    ),
                ),
                ("comment", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "transaction_time",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="core.transactioncategory",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]