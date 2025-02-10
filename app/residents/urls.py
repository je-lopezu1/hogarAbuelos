from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.residents_view, name='residents'),
]