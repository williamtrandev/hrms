from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('/history', views.attendance_history, name='attendance_history'),
    path('/correction-request/<int:attendance_id>', views.correction_request, name='correction_request'),
    path('/correction-response', views.correction_response, name='correction_response'),
    path('/correction-request/<int:request_id>/approve', views.approve_correction_request, name='approve_correction_request'),
    path('/correction-request/<int:request_id>/attendance-details', views.get_attendance_details_from_correction_request, name='get_attendance_details_from_correction_request'),
    path('/correction-request/history', views.attendant_request_history, name='attendant_request_history'),
    path('/correction-request/<int:request_id>/reject', views.reject_correction_request, name='reject_correction_request'),
    path('/correction-history', views.attendance_correction_history, name='attendance_correction_history'),
    path('/status', views.get_attendance_status, name='get_attendance_status'),
    path('/check', views.check_attendance, name='check_attendance'),
]