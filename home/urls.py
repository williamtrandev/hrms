from django.contrib import admin
from django.urls import path, include
from home import views

app_name = 'home'

urlpatterns = [
    path('/admin', views.dashboard, name='dashboard'),
    path('/staff', views.dashboard_staff, name='dashboard_staff'),
]