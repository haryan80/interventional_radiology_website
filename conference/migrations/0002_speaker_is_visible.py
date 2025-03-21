# Generated by Django 5.0.2 on 2025-03-17 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conference", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="speaker",
            name="is_visible",
            field=models.BooleanField(
                default=True, help_text="Whether to display this speaker on the website"
            ),
        ),
    ]
