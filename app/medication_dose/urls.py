from django.contrib import admin
from django.urls import path
from . import views

app_name = 'medication_dose'

urlpatterns = [
    path('<int:resident_pk>/doses/', views.resident_doses_view, name='resident_doses_view'),
    path('<int:resident_pk>/doses/add_quantity/', views.add_resident_medication_quantity_view, name='add_resident_medication_quantity_view'), # New URL
    path('<int:resident_pk>/doses/<int:dose_pk>/delete/', views.delete_medication_dose_view, name='delete_medication_dose_view'),
    path('<int:resident_pk>/doses/<int:dose_pk>/update/', views.update_medication_dose_view, name='update_medication_dose_view'),
]