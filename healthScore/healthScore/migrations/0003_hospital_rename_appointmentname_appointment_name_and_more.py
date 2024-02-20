# Generated by Django 4.2 on 2024-02-20 22:13

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthScore', '0002_appointment_user_alter_hospitals_contactinfo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='hospital',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(default='')),
                ('address', models.TextField(default='')),
                ('email', models.EmailField(max_length=254)),
                ('password', models.TextField()),
                ('contactInfo', models.TextField(default='', max_length=10)),
                ('website', models.TextField(default='')),
                ('status', models.TextField(choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending')], default='pending')),
            ],
        ),
        migrations.RenameField(
            model_name='appointment',
            old_name='appointmentName',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='appointment',
            old_name='appointmentProperties',
            new_name='properties',
        ),
        migrations.RemoveField(
            model_name='communityinteraction',
            name='userName',
        ),
        migrations.RemoveField(
            model_name='healthrecord',
            name='dateTime',
        ),
        migrations.AddField(
            model_name='healthrecord',
            name='createdAt',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 22, 12, 47, 11431)),
        ),
        migrations.AddField(
            model_name='healthrecord',
            name='updatedAt',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 22, 12, 47, 11453)),
        ),
        migrations.AlterField(
            model_name='communityinteraction',
            name='postTimeStamp',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 20, 22, 12, 47, 12121)),
        ),
        migrations.AlterField(
            model_name='healthrecord',
            name='status',
            field=models.TextField(choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending')], default='pending'),
        ),
        migrations.AlterField(
            model_name='hospitalstaff',
            name='hospitalID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='healthScore.hospital'),
        ),
        migrations.DeleteModel(
            name='hospitals',
        ),
    ]
