# Generated by Django 5.1.7 on 2025-03-08 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_task"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="due_date",
            field=models.DateField(
                blank=True,
                help_text="Date when the task should be completed",
                null=True,
            ),
        ),
    ]
