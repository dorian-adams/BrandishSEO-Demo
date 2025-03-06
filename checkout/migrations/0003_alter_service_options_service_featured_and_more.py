# Generated by Django 4.1.1 on 2025-02-09 04:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="service",
            options={"ordering": ["package_type"]},
        ),
        migrations.AddField(
            model_name="service",
            name="featured",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="service",
            name="package_type",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Keyword"), (2, "SEO Strategy")], unique=True
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=7,
                validators=[django.core.validators.MinValueValidator(0.0)],
                verbose_name="Price (USD)",
            ),
        ),
        migrations.CreateModel(
            name="ServiceFeature",
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
                ("description", models.CharField(max_length=100)),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="features",
                        to="checkout.service",
                    ),
                ),
            ],
        ),
    ]
