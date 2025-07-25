# Generated by Django 4.1.1 on 2025-03-03 23:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Lead",
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
                ("name", models.CharField(max_length=40)),
                ("preferred_contact", models.CharField(max_length=100)),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                ("date_of_inquiry", models.DateTimeField(auto_now_add=True)),
                ("converted", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="ContactAttempt",
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
                ("date_attempted", models.DateTimeField()),
                ("successful", models.BooleanField(default=False)),
                (
                    "lead",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contact_attempts",
                        to="core.lead",
                    ),
                ),
            ],
        ),
    ]
