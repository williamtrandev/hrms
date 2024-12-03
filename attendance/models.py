from django.db import models
from django.contrib.auth.models import User

from staff.models import StaffProfile


class AttendanceTracking(models.Model):
    id = models.AutoField(primary_key=True)
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    date_work = models.DateField(auto_now_add=True)
    checkin = models.TimeField(null=True, blank=True)
    checkout = models.TimeField(null=True, blank=True)
    overtime = models.FloatField(null=True, blank=True)
    total_working = models.FloatField(null=True, blank=True)
    is_late = models.BooleanField()


class AttendanceCorrectionRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('checkin', 'Check In'),
        ('checkout', 'Check Out'),
        ('overtime', 'Overtime'),
    ]

    RESPONSE_TYPE_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.AutoField(primary_key=True)
    attendance_tracking = models.ForeignKey(AttendanceTracking, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    reason = models.CharField(max_length=255)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES, default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_reason = models.CharField(max_length=255, null=True, blank=True)

