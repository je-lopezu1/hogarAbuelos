from django.contrib import admin
from django.urls import path
from . import views

app_name = 'medications'

urlpatterns = [
    path('', views.medications_view, name='medications_view'),
    path('create/', views.create_medication_view, name='create_medication_view'),
    path('delete/<int:pk>/', views.delete_medication_view, name='delete_medication_view'),
]