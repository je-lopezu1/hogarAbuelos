# Generated by Django 5.1.6 on 2025-02-07 02:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('medications', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medication',
            name='description',
        ),
        migrations.RemoveField(
            model_name='medication',
            name='dosage',
        ),
    ]
