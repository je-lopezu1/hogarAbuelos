# Generated by Django 5.1.6 on 2025-03-24 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='patients',
        ),
    ]
