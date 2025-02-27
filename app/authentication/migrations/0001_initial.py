# Generated by Django 5.1.6 on 2025-02-27 00:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('residents', '0002_rename_medication_resident_medications'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('doctor', 'Doctor'), ('patient', 'Paciente'), ('family', 'Familiar')], max_length=10)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('specialty', models.CharField(blank=True, max_length=100)),
                ('relationship', models.CharField(blank=True, max_length=50)),
                ('patients', models.ManyToManyField(blank=True, related_name='doctors', to='residents.resident')),
                ('related_residents', models.ManyToManyField(blank=True, related_name='family_members', to='residents.resident')),
                ('resident', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patient_profile', to='residents.resident')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
