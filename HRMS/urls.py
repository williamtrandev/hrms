from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('auth/login')),

    path('admin', admin.site.urls),

    # Authentication
    path('auth', include('authentication.urls')),

    # Home
    path('dashboard', include('home.urls')),

    # Staff
    path('staff', include('staff.urls')),

    # Attendance
    path('attendance', include('attendance.urls')),

    # Leave
    path('leave', include('leave.urls')),

    # Salary
    path('salaries', include('reviews.urls')),

]