from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import StaffForm
from .models import StaffProfile, Department
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from authentication.decorators import admin_required

def get_layout_by_user(user):
    """Helper function để xác định layout dựa trên user"""
    if user.is_superuser or user.is_staff:  # Nếu là admin
        return 'layouts/admin.html'
    return 'layouts/staff.html'  # Nếu là staff thường

@admin_required
@require_http_methods(["GET"])
def staff_list(request):
    # Xử lý tìm kiếm
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    per_page = request.GET.get('per_page', 10)
    
    # Query cơ sở
    employees = StaffProfile.objects.all()
    
    # Áp dụng bộ lọc tìm kiếm
    if search_query:
        employees = employees.filter(
            Q(id__icontains=search_query) |  # Tìm theo mã nhân viên
            Q(full_name__icontains=search_query) |  # Tìm theo tên
            Q(user__email__icontains=search_query) |  # Tìm theo email
            Q(phone_number__icontains=search_query) |  # Tìm theo số điện thoại
            Q(department_id=search_query if search_query.isdigit() else None) |  # Tìm theo ID phòng ban
            Q(position__name__icontains=search_query)  # Tìm theo tên chức vụ
        )
    
    # Lọc theo phòng ban từ dropdown
    if department_filter:
        employees = employees.filter(department_id=department_filter)
    
    # Phân trang
    paginator = Paginator(employees, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách phòng ban cho dropdown
    departments = Department.objects.all()
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
    }
    
    return render(request, 'staff_list.html', context)


@admin_required
@require_http_methods(["GET", "POST"])
def add_staff(request):
    notification = None
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            # Lấy thông tin từ form
            full_name = form.cleaned_data['full_name']
            department = form.cleaned_data['department']
            position = form.cleaned_data['position']
            gender = form.cleaned_data['gender']
            join_date = form.cleaned_data['join_date']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            birthdate = form.cleaned_data['birthdate']
            email = form.cleaned_data['email']
            base_salary = form.cleaned_data['base_salary']

            if User.objects.filter(email=email).exists():
                notification = {
                    'type': 'error',
                    'message': 'Email này đã tồn tại. Vui lòng chọn email khác.'
                }
                return render(request, 'add_staff.html', {
                    'form': form,
                    'notification': notification
                })

            user = User.objects.create_user(username=email, email=email, password='12345678', is_staff=True)

            staff = StaffProfile.objects.create(
                user=user,
                full_name=full_name,
                department=department,
                position=position,
                gender=gender,
                join_date=join_date,
                phone_number=phone_number,
                address=address,
                birthdate=birthdate,
                base_salary=base_salary
            )

            notification = {
                'type': 'success',
                'message': 'Nhân viên đã được thêm thành công!'
            }
    else:
        form = StaffForm()

    return render(request, 'add_staff.html', {
        'form': form,
        'notification': notification
    })


@require_http_methods(["GET"])
def detail_staff(request, staff_id):
    staff = get_object_or_404(StaffProfile, id=staff_id)
    return render(request, 'staff_detail.html', {
        'staff': staff,
        'base_layout': get_layout_by_user(request.user)
    })


@require_http_methods(["GET", "POST"])
def edit_staff(request, staff_id):
    staff = get_object_or_404(StaffProfile, id=staff_id)
    notification = None

    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        email = request.POST.get('email')

        if form.is_valid():
            if staff.user.email != email and User.objects.filter(email=email).exists():
                notification = {
                    'type': 'error',
                    'message': 'Email đã tồn tại. Vui lòng chọn email khác.'
                }
            else:
                staff = form.save(commit=False)
                staff.user.email = email
                staff.user.save()
                staff.save()
                notification = {
                    'type': 'success',
                    'message': 'Cập nhật thông tin nhân viên thành công.'
                }
        else:
            notification = {
                'type': 'error',
                'message': 'Có lỗi xảy ra khi cập nhật.'
            }
    else:
        form = StaffForm(instance=staff)
        email = staff.user.email

    return render(request, 'edit_staff.html', {
        'form': form,
        'staff': staff,
        'email': email,
        'notification': notification
    })

@require_http_methods(["DELETE"])
def delete_staff(request, staff_id):
    try:
        staff = StaffProfile.objects.get(id=staff_id)
        user = staff.user
        staff.delete()
        user.delete()
        return JsonResponse({
            'status': 'success',
            'notification': {
                'type': 'success',
                'message': 'Xóa nhân viên thành công'
            }
        })
    except StaffProfile.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'notification': {
                'type': 'error',
                'message': 'Nhân viên không tồn tại'
            }
        })