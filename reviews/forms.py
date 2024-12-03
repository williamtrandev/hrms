# from django import forms
# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Luong
#
#
# class SalaryForm(forms.ModelForm):
#     class Meta:
#         model = Luong
#         fields = [
#             'MaLuong', 'MaDNP', 'MaNV', 'MaChamCong', 'LuongCoBan',
#             'Thuong', 'TongLuong', 'NgayTraLuong'
#         ]
#
#
#
# def edit_salary(request, salary_id):
#     salary = get_object_or_404(Luong, id=salary_id)
#
#     if request.method == 'POST':
#         form = SalaryForm(request.POST, instance=salary)
#         if form.is_valid():
#             form.save()
#             return redirect('salary_list')  # Hoặc trang bạn muốn chuyển hướng sau khi lưu
#     else:
#         form = SalaryForm(instance=salary)
#
#     return render(request, 'edit_salary.html', {'form': form, 'salary': salary})
#
