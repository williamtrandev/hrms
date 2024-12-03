from django import forms
from .models import StaffProfile, Department, Position

class StaffForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = StaffProfile
        fields = ['full_name', 'email', 'department', 'position', 'gender', 
                 'birthdate', 'join_date', 'phone_number', 'address', 'base_salary']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '500000',
                'value': '5000000'
            }),
        }
