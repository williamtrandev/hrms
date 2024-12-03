from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('/add', views.add_staff, name='add_staff'),
    path('/detail/<int:staff_id>', views.detail_staff, name='detail_staff'),
    path('/edit/<int:staff_id>', views.edit_staff, name='edit_staff'),
    path('/delete/<int:staff_id>', views.delete_staff, name='delete_staff'),
]