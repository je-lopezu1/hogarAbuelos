from django.contrib import admin
from django.urls import path
from . import views

app_name = 'medication_dose'

urlpatterns = [
    # The resident_doses_view now handles both display and creation
    path('<int:resident_pk>/doses/', views.resident_doses_view, name='resident_doses_view'),
    # Removed the separate create URL:
    # path('<int:resident_pk>/doses/create/', views.create_medication_dose_view, name='create_medication_dose_view'),
    path('<int:resident_pk>/doses/<int:dose_pk>/delete/', views.delete_medication_dose_view, name='delete_medication_dose_view'),
    path('<int:resident_pk>/doses/<int:dose_pk>/update/', views.update_medication_dose_view, name='update_medication_dose_view'),
]