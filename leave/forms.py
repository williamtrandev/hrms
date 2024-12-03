from django import forms
from django.core.exceptions import ValidationError
from .models import Leave

class LeaveForm(forms.ModelForm):
    # Thêm các trường không có trong mô hình Leave
    staff_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )
    staff_fullname = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )
    staff_position = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )

    class Meta:
        model = Leave
        fields = ['start_date', 'end_date', 'reason', 'reason_detail']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Select(
                choices=[
                    ('Lý do cá nhân', 'Lý do cá nhân'),
                    ('Nghỉ phép', 'Nghỉ phép'),
                    ('Nghỉ bệnh', 'Nghỉ bệnh'),
                    ('Khác', 'Khác')
                ],
                attrs={'class': 'form-select'}
            ),
            'reason_detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'cols': 50}),
        }

    def __init__(self, *args, **kwargs):
        # Lấy dữ liệu staff khi khởi tạo form
        staff = kwargs.pop('staff', None)  # Truyền staff từ view
        super().__init__(*args, **kwargs)
        if staff:
            # Đặt giá trị ban đầu cho các trường
            self.fields['staff_id'].initial = staff.id
            self.fields['staff_fullname'].initial = staff.full_name
            self.fields['staff_position'].initial = staff.position

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise ValidationError('Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.')

        return cleaned_data

class LeaveFormAdmin(forms.ModelForm):
    # Thêm các trường không có trong mô hình Leave
    staff_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )
    staff_fullname = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )
    staff_position = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        required=False
    )

    class Meta:
        model = Leave
        fields = ['start_date', 'end_date', 'reason', 'reason_detail', 'status']
        widgets = {
            'start_date': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'end_date': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'reason_detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'cols': 50, 'readonly': True}),
            'status': forms.Select(
                choices=[
                    ('Đang chờ', 'Đang chờ'),
                    ('Duyệt', 'Duyệt'),
                    ('Không duyệt', 'Không duyệt')
                ],
                attrs={'class': 'form-select'}
            ),
        }

    def __init__(self, *args, **kwargs):
        # Lấy dữ liệu staff khi khởi tạo form
        staff = kwargs.pop('staff', None)  # Truyền staff từ view
        super().__init__(*args, **kwargs)
        if staff:
            # Đặt giá trị ban đầu cho các trường
            self.fields['staff_id'].initial = staff.id
            self.fields['staff_fullname'].initial = staff.full_name
            self.fields['staff_position'].initial = staff.position

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise ValidationError('Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.')

        return cleaned_data
