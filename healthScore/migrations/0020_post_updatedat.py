# Generated by Django 4.2 on 2024-03-30 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("healthScore", "0019_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="updatedAt",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
