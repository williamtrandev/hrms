from django.urls import path
from . import views

app_name = 'salary'

urlpatterns = [
    path('', views.salary_list, name='salary_list'),
    path('/generate', views.generate_salary, name='generate'),
    path('/export', views.export_salary, name='export'),
    path('/me', views.staff_salary_list, name='staff_salary_list'),
]