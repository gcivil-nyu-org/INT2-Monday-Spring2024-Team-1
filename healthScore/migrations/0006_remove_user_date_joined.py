# Generated by Django 4.2 on 2024-03-08 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("healthScore", "0005_user_date_joined_user_is_active_user_is_staff_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="date_joined",
        ),
    ]
