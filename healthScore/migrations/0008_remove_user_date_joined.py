# Generated by Django 4.2 on 2024-03-08 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("healthScore", "0007_alter_user_options_user_date_joined"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="date_joined",
        ),
    ]
