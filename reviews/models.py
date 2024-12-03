from django.db import models

from staff.models import StaffProfile

class Salary(models.Model):
    staff = models.ForeignKey(
        StaffProfile, 
        on_delete=models.CASCADE,
        related_name='salaries'
    )
    num_days_work = models.PositiveIntegerField(default=0)
    bonus = models.PositiveIntegerField(default=0)
    pay_date = models.DateTimeField()
    total_salary = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)