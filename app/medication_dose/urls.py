from django.contrib import admin
from django.urls import path
from . import views

app_name = 'medication_dose'

urlpatterns = [
    path('<int:resident_pk>/doses/', views.resident_doses_view, name='resident_doses_view'),
]