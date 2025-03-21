# Generated by Django 5.1.4 on 2025-01-10 19:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("searchapp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginCredentials",
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
                ("username", models.CharField(max_length=100, unique=True)),
                ("password", models.CharField(max_length=255)),
                ("role", models.CharField(max_length=50)),
            ],
        ),
    ]
