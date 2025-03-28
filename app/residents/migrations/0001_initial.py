# Generated by Django 5.1.6 on 2025-02-07 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('medications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('medical_condition', models.CharField(max_length=300)),
                ('medication', models.ManyToManyField(related_name='residents', to='medications.medication')),
            ],
        ),
    ]
