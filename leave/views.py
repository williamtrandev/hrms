from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from authentication.decorators import admin_required
from leave.forms import LeaveForm, LeaveFormAdmin
from leave.models import Leave
from staff.models import StaffProfile, Department

@admin_required
@require_http_methods(["GET"])
def leave_admin(request):
    # Xử lý tìm kiếm
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    date_filter = request.GET.get('date', '')
    try:
        date_filter_obj = datetime.strptime(date_filter, "%Y-%m-%d").date()
    except ValueError:
        date_filter_obj = None

    per_page = request.GET.get('per_page', 10)

    leaves = Leave.objects.all().select_related('staff').order_by('-created_at')

    if search_query:
        leaves = leaves.filter(
            Q(id__icontains=search_query) |
            Q(staff__full_name__icontains=search_query) |
            Q(staff__user__email__icontains=search_query) |
            Q(staff__phone_number__icontains=search_query) |
            Q(staff__department_id=search_query if search_query.isdigit() else None) |
            Q(staff__position__name__icontains=search_query)
        )

    if department_filter:
        leaves = leaves.filter(staff__department_id=department_filter)

    if date_filter_obj:
        leaves = leaves.filter(
            Q(start_date=date_filter_obj) |
            Q(end_date=date_filter_obj) |
            Q(created_at=date_filter_obj)
        )

    paginator = Paginator(leaves, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    context = {
        'page_obj': page_obj,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
    }

    return render(request, "leave_admin.html", context)

@require_http_methods(["GET"])
def leave_staff(request):
    per_page = request.GET.get('per_page', 10)
    date_filter = request.GET.get('date', '')
    try:
        date_filter_obj = datetime.strptime(date_filter, "%Y-%m-%d").date()
    except ValueError:
        date_filter_obj = None

    staff = get_object_or_404(StaffProfile, user=request.user)
    # staff = StaffProfile.objects.filter(user=request.user).first()
    staff_leaves = Leave.objects.filter(staff=staff).order_by('-created_at')

    if date_filter_obj:
        staff_leaves = staff_leaves.filter(
            Q(start_date=date_filter_obj) |
            Q(end_date=date_filter_obj) |
            Q(created_at=date_filter_obj)
        )

    paginator = Paginator(staff_leaves, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, "leave_staff.html", context)

@require_http_methods(["GET", "POST"])
def new(request):
    staff = StaffProfile.objects.filter(user=request.user).first()
    notification = None

    if request.method == 'POST':
        form = LeaveForm(request.POST, staff=staff)
        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            reason = form.cleaned_data["reason"]
            reason_detail = form.cleaned_data["reason_detail"]

            leave = Leave.objects.create(
                staff=staff,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                reason_detail=reason_detail
            )
            notification = {
                'type': 'success',
                'message': 'Yêu cầu nghỉ phép đã được tạo thành công.'
            }
        else:
            notification = {
                'type': 'error',
                'message': 'Dữ liệu không hợp lệ, vui lòng kiểm tra lại.'
            }
    else:
        form = LeaveForm(staff=staff)

    return render(request, "new.html", {
        'form': form,
        'notification': notification
    })

@admin_required
@require_http_methods(["GET", "POST"])
def details(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    notification = None

    if request.method == 'POST':
        form = LeaveFormAdmin(request.POST, instance=leave, staff=leave.staff)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.save()
            notification = {
                'type': 'success',
                'message': 'Yêu cầu nghỉ phép đã được cập nhật trạng thái thành công.'
            }
        else:
            notification = {
                'type': 'error',
                'message': 'Dữ liệu không hợp lệ, vui lòng kiểm tra lại.'
            }
    else:
        form = LeaveFormAdmin(instance=leave, staff=leave.staff)

    return render(request, "details.html", {
        'form': form,
        'notification': notification
    })

@require_http_methods(["GET", "POST"])
def edit(request, leave_id):
    staff = StaffProfile.objects.filter(user=request.user).first()
    leave = get_object_or_404(Leave, id=leave_id)
    notification = None

    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave, staff=staff)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.save()
            notification = {
                'type': 'success',
                'message': 'Yêu cầu nghỉ phép đã được chỉnh sửa thành công.'
            }
        else:
            notification = {
                'type': 'error',
                'message': 'Dữ liệu không hợp lệ, vui lòng kiểm tra lại.'
            }
    else:
        form = LeaveForm(instance=leave, staff=staff)

    return render(request, "edit.html", {
        'form': form,
        'notification': notification
    })
