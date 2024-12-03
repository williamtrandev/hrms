from django.urls import path
from . import views

app_name = 'leave'

urlpatterns = [
    path('', views.leave_admin, name='leave_admin'),
    path('/me', views.leave_staff, name='leave_staff'),
    path('/new', views.new, name='new'),
    path('/detail/<int:leave_id>', views.details, name='detail'),
    path('/edit/<int:leave_id>', views.edit, name='edit'),
]