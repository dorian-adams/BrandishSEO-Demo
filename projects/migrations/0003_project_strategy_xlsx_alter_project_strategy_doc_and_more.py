# Generated by Django 4.1.1 on 2025-05-31 01:04

import django.core.validators
from django.db import migrations, models

import projects.models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0002_alter_task_assigned_to_alter_task_task_goal"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="strategy_xlsx",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=projects.models.directory_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["xlsx"]
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="strategy_doc",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=projects.models.directory_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["docx"]
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="strategy_pdf",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=projects.models.directory_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf"]
                    )
                ],
            ),
        ),
    ]
