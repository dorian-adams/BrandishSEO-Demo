# Generated by Django 4.1.1 on 2023-04-30 22:21

import customerportal.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("checkout", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
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
                ("project_name", models.CharField(max_length=40, unique=True)),
                ("slug", models.SlugField()),
                ("website", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("keywords", models.CharField(max_length=200)),
                ("competitor", models.CharField(max_length=200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Researching", "Researching"),
                            ("In Progress", "In Progress"),
                            ("Final Touches", "Final Touches"),
                            ("Review", "Review"),
                            ("Complete", "Complete"),
                        ],
                        default="Payment Pending",
                        max_length=20,
                    ),
                ),
                (
                    "strategy_doc",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=customerportal.models.directory_path,
                    ),
                ),
                (
                    "strategy_pdf",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=customerportal.models.directory_path,
                    ),
                ),
                (
                    "admin",
                    models.ManyToManyField(
                        related_name="admins", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "members",
                    models.ManyToManyField(
                        related_name="members", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="checkout.service",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Task",
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
                ("task_title", models.CharField(max_length=100)),
                ("task_description", models.TextField()),
                ("task_goal", models.CharField(max_length=100)),
                (
                    "progress",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("Low", "Low"),
                            ("Medium", "Medium"),
                            ("High", "High"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("To-do", "To-do"),
                            ("In progress", "In progress"),
                            ("Completed", "Completed"),
                        ],
                        default="To-do",
                        max_length=15,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("slug", models.SlugField()),
                ("feedback", models.BooleanField(default=False)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="customerportal.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskComment",
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
                ("text", models.CharField(max_length=1000)),
                ("posted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="customerportal.task",
                    ),
                ),
            ],
            options={
                "ordering": ("posted_at",),
            },
        ),
        migrations.CreateModel(
            name="DirectMessage",
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
                (
                    "text",
                    models.TextField(
                        max_length=300,
                        validators=[
                            django.core.validators.MinLengthValidator(
                                3, "Comment must be greater than 3 characters."
                            )
                        ],
                    ),
                ),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sent_to",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sent_from",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("sent_at",),
            },
        ),
        migrations.CreateModel(
            name="AccountInvite",
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
                ("email", models.EmailField(max_length=300)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customerportal.project",
                    ),
                ),
            ],
        ),
    ]
