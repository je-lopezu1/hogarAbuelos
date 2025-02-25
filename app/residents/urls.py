from django.contrib import admin
from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    path('', views.residents_view, name='residents_view'),
    path('create/', views.create_resident_view, name='create_resident_view'),
    path('delete/<int:pk>/', views.delete_resident_view, name='delete_resident_view'),
    path('update/<int:pk>/', views.update_resident_view, name='update_resident_view'),
]