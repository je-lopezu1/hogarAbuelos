from django.contrib import admin
from django.urls import path
from . import views

app_name = 'supplies'

urlpatterns = [
    path('', views.supplies_view, name='supplies_view'),
    path('create/', views.create_supply_view, name='create_supply_view'),
    path('delete/<int:pk>/', views.delete_supply_view, name='delete_supply_view'),
    path('update/<int:pk>/', views.update_supply_view, name='update_supply_view'),
    path('add_resident_supply_quantity/<int:resident_pk>/', views.add_resident_supply_quantity_view, name='add_resident_supply_quantity_view'),
]