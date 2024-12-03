from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from .models import AttendanceCorrectionRequest


class AttendanceCorrectionForm(forms.ModelForm):
    class Meta:
        model = AttendanceCorrectionRequest
        fields = ['EmployeeID', 'EditType', 'RequestContent', 'Reason']
        widgets = {
            'EmployeeID': forms.TextInput(attrs={'readonly': 'readonly', 'value': 'NV001'}),
            #'FullName': forms.TextInput(attrs={'readonly': 'readonly', 'value': 'Nguyễn Văn A'}),
            #'DepartmentName': forms.TextInput(attrs={'readonly': 'readonly', 'value': 'Phòng Kinh Doanh'}),
            'EditType': forms.Select(choices=[
                ('CheckIn', 'Check In'),
                ('CheckOut', 'Check Out'),
                ('Correction', 'Correction')
            ]),
            'RequestContent': forms.Textarea(attrs={'rows': 3}),
            'Reason': forms.Textarea(attrs={'rows': 3}),
        }