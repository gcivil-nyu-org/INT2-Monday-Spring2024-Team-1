# Generated by Django 4.2 on 2024-04-13 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("healthScore", "0025_alter_user_profilepic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="profilePic",
            field=models.TextField(null=True),
        ),
    ]
