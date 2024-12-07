from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from staff.models import Department
from .models import AttendanceTracking, AttendanceCorrectionRequest
from datetime import datetime, time, timedelta
from authentication.decorators import admin_required
from django.contrib import messages
from django.utils import timezone
import json
from calendar import monthrange
from staff.models import StaffProfile


@login_required
@require_http_methods(["GET"])
def attendance_list(request):
    # Xử lý tìm kiếm
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    date_filter = request.GET.get('date', '')
    per_page = request.GET.get('per_page', 10)
    
    attendances = AttendanceTracking.objects.select_related('staff').all().order_by('-date_work')
    
    # Áp dụng bộ lọc tìm kiếm
    if search_query:
        attendances = attendances.filter(
            Q(staff__id__icontains=search_query) |  # Tìm theo mã nhân viên
            Q(staff__full_name__icontains=search_query) |  # Tìm theo tên
            Q(staff__department__name__icontains=search_query)  # Tìm theo phòng ban
        )
    
    # Lọc theo phòng ban
    if department_filter:
        attendances = attendances.filter(staff__department_id=department_filter)
    
    # Lọc theo ngày
    if date_filter:
        attendances = attendances.filter(date_work=date_filter)
    
    # Phân trang
    paginator = Paginator(attendances, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'departments': Department.objects.all(),
        'search_query': search_query,
        'department_filter': department_filter,
        'date_filter': date_filter,
    }
    return render(request, 'attendance_list.html', context)

@login_required
@require_http_methods(["GET"])
def attendance_history(request):
    year_filter = request.GET.get('year', datetime.now().year)
    month_filter = request.GET.get('month', datetime.now().month)
    status_filter = request.GET.get('status', '')
    per_page = request.GET.get('per_page', 10)

    # Query cơ sở - Chỉ lấy attendance của user hiện tại
    attendances = AttendanceTracking.objects.select_related('staff').filter(
        staff__user=request.user,
        checkin__isnull=False,
    ).order_by('-date_work')
    
    # Lọc theo năm và tháng
    if year_filter and month_filter:
        attendances = attendances.filter(
            date_work__year=year_filter,
            date_work__month=month_filter
        )
    
    # Lọc theo trạng thái
    if status_filter == 'late':
        attendances = attendances.filter(is_late=True)
    elif status_filter == 'on_time':
        attendances = attendances.filter(is_late=False)
    
    # Tạo danh sách năm (từ năm đầu tiên đến năm hiện tại)
    current_year = datetime.now().year
    years = range(current_year - 5, current_year + 1)
    
    # Danh sách tháng
    months = range(1, 13)
    
    # Phân trang
    paginator = Paginator(attendances, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'year_filter': int(year_filter) if year_filter else None,
        'month_filter': int(month_filter) if month_filter else None,
        'status_filter': status_filter,
        'years': years,
        'months': months,
    }
    
    return render(request, 'attendance_history.html', context)


@require_http_methods(["POST"])
def correction_request(request, attendance_id):
    try:
        data = json.loads(request.body)
        attendance = AttendanceTracking.objects.get(id=attendance_id)
        
        # Kiểm tra người yêu cầu có phải là người chấm công không
        if attendance.staff.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'Bạn không có quyền chỉnh sửa bản ghi này'
            })

        correction_request = AttendanceCorrectionRequest.objects.create(
            attendance_tracking=attendance,
            request_type=data.get('request_type'),
            content=data.get('content'),
            reason=data.get('reason'),
            response_type='pending'
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@admin_required
@require_http_methods(["GET"])
def correction_response(request):
    department_filter = request.GET.get('department', '')
    month_filter = request.GET.get('month', '')
    per_page = request.GET.get('per_page', 10)
    
    # Query cơ sở
    requests = AttendanceCorrectionRequest.objects.select_related(
        'attendance_tracking__staff__department'
    ).filter(response_type='pending').order_by('-created_at')
    
    # Lọc theo phòng ban
    if department_filter:
        requests = requests.filter(attendance_tracking__staff__department_id=department_filter)
    
    # Lọc theo tháng
    if month_filter:
        requests = requests.filter(created_at__month=month_filter)
    
    # Phân trang
    paginator = Paginator(requests, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Danh sách tháng (1-12)
    months = range(1, 13)
    
    context = {
        'page_obj': page_obj,
        'departments': Department.objects.all(),
        'months': months,
        'department_filter': department_filter,
        'month_filter': int(month_filter) if month_filter else None,
    }
    
    return render(request, 'attendance_correction_response.html', context)


@admin_required
@require_http_methods(["GET"])
def get_attendance_details_from_correction_request(request, request_id):
    try:
        # Lấy thông tin từ correction request
        correction_request = get_object_or_404(
            AttendanceCorrectionRequest.objects.select_related(
                'attendance_tracking__staff__department'
            ), 
            id=request_id
        )
        attendance = correction_request.attendance_tracking

        return JsonResponse({
            # Thông tin nhân viên
            'staff_name': attendance.staff.full_name,
            'staff_id': attendance.staff.id,
            'department': attendance.staff.department.name,
            
            # Thông tin chấm công
            'date': attendance.date_work.strftime('%Y-%m-%d'),
            'checkin': attendance.checkin.strftime('%H:%M') if attendance.checkin else None,
            'checkout': attendance.checkout.strftime('%H:%M') if attendance.checkout else None,
            'is_late': attendance.is_late,
            'total_working': attendance.total_working,
            
            # Thông tin yêu cầu chỉnh sửa
            'correction_type': correction_request.get_request_type_display(),
            'correction_content': correction_request.content,
            'correction_reason': correction_request.reason,
            'created_at': correction_request.created_at.strftime('%Y-%m-%d %H:%M')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
        
@admin_required
@require_http_methods(["POST"])
def approve_correction_request(request, request_id):
    try:
        data = json.loads(request.body)
        checkin_time = data.get('checkin')
        checkout_time = data.get('checkout')
        note = data.get('note')

        correction_request = get_object_or_404(
            AttendanceCorrectionRequest.objects.select_related('attendance_tracking'),
            id=request_id
        )
        attendance = correction_request.attendance_tracking
        STANDARD_CHECKIN = time(8, 0)  # 8:00 AM
        LUNCH_START = time(12, 0)  # 12:00 PM
        LUNCH_END = time(13, 30)  # 1:30 PM
        STANDARD_CHECKOUT = time(17, 30)  # 5:30 PM
        LUNCH_DURATION = timedelta(hours=1.5)  # 1.5 giờ nghỉ trưa
        if checkin_time:
            checkin_time_obj = datetime.strptime(checkin_time, '%H:%M').time()
            attendance.checkin = checkin_time_obj
            attendance.is_late = checkin_time_obj > STANDARD_CHECKIN

        # Cập nhật checkout
        if checkout_time:
            checkout_time_obj = datetime.strptime(checkout_time, '%H:%M').time()
            attendance.checkout = checkout_time_obj

        if attendance.checkin and attendance.checkout:
            # Chuyển đổi sang datetime để tính toán
            date = attendance.date_work
            checkin_dt = datetime.combine(date, attendance.checkin)
            checkout_dt = datetime.combine(date, attendance.checkout)
            standard_checkout_dt = datetime.combine(date, STANDARD_CHECKOUT)
            lunch_start_dt = datetime.combine(date, LUNCH_START)
            lunch_end_dt = datetime.combine(date, LUNCH_END)

            # Tính tổng thời gian
            total_duration = checkout_dt - checkin_dt

            # Trừ thời gian nghỉ trưa nếu thời gian làm việc bao gồm giờ nghỉ trưa
            if checkin_dt <= lunch_start_dt and checkout_dt >= lunch_end_dt:
                # Trừ toàn bộ thời gian nghỉ trưa
                total_duration -= LUNCH_DURATION
            elif checkin_dt < lunch_end_dt and checkout_dt > lunch_start_dt:
                # Trừ một phần thời gian nghỉ trưa
                overlap_start = max(checkin_dt, lunch_start_dt)
                overlap_end = min(checkout_dt, lunch_end_dt)
                total_duration -= (overlap_end - overlap_start)

            # Chuyển đổi sang giờ và làm tròn
            total_hours = total_duration.total_seconds() / 3600
            attendance.total_working = round(total_hours, 2)
            if checkout_dt > standard_checkout_dt and total_hours > 8:
                attendance.overtime = total_hours - 8
        if note:
            correction_request.response_reason = note
        
        correction_request.response_type = 'approved'
        correction_request.processed_by = request.user
        correction_request.processed_at = timezone.now()
        attendance.save()
        correction_request.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)   

@admin_required
@require_http_methods(["POST"])
def reject_correction_request(request, request_id):
    try:
        # Lấy dữ liệu từ request body
        data = json.loads(request.body)
        reason = data.get('reason')

        if not reason:
            return JsonResponse({
                'status': 'error',
                'message': 'Vui lòng nhập lý do từ chối'
            }, status=400)

        # Lấy correction request
        correction_request = get_object_or_404(
            AttendanceCorrectionRequest,
            id=request_id
        )

        # Cập nhật trạng thái
        correction_request.response_type = 'rejected'
        correction_request.processed_at = datetime.now()
        correction_request.processed_by = request.user
        correction_request.response_reason = reason
        correction_request.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Đã từ chối yêu cầu thành công'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@admin_required
def attendance_correction_history(request):

    # Lấy các tham số filter
    status = request.GET.get('status', '')
    month = request.GET.get('month', '')
    per_page = request.GET.get('per_page', '10')

    # Query base
    queryset = AttendanceCorrectionRequest.objects.filter(~Q(response_type='pending')).select_related(
        'attendance_tracking__staff',
        'processed_by'
    ).order_by('-created_at')

    # Filter theo trạng thái
    if status:
        queryset = queryset.filter(response_type=status)

    # Filter theo tháng
    if month:
        try:
            month = int(month)
            current_year = datetime.now().year
            _, last_day = monthrange(current_year, month)
            
            start_date = datetime(current_year, month, 1)
            end_date = datetime(current_year, month, last_day, 23, 59, 59)
            
            queryset = queryset.filter(
                created_at__range=(start_date, end_date)
            )
        except ValueError:
            pass

    months = list(range(1, 13))

    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10

    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'months': months,
        'month_filter': month,
        'status_filter': status,
        'per_page': per_page
    }

    return render(
        request,
        'attendance_correction_history.html',
        context
    )

@login_required
def attendant_request_history(request):
    # Lấy các tham số filter
    status = request.GET.get('status', '')
    month = request.GET.get('month', '')
    per_page = request.GET.get('per_page', '10')

    # Query base - chỉ lấy yêu cầu của staff đang đăng nhập
    queryset = AttendanceCorrectionRequest.objects.filter(
        attendance_tracking__staff__user=request.user
    ).select_related(
        'attendance_tracking',
        'processed_by'
    ).order_by('-created_at')

    # Filter theo trạng thái
    if status:
        queryset = queryset.filter(response_type=status)

    # Filter theo tháng
    if month:
        try:
            month = int(month)
            current_year = datetime.now().year
            _, last_day = monthrange(current_year, month)
            
            start_date = datetime(current_year, month, 1)
            end_date = datetime(current_year, month, last_day, 23, 59, 59)
            
            queryset = queryset.filter(
                created_at__range=(start_date, end_date)
            )
        except ValueError:
            pass

    # Tạo danh sách tháng để hiển thị trong dropdown
    months = list(range(1, 13))

    # Phân trang
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10

    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'months': months,
        'month_filter': month,
        'status_filter': status,
        'per_page': per_page
    }

    return render(
        request,
        'attendant_request_history.html',
        context
    )

@login_required
def get_attendance_status(request):
    try:
        staff = StaffProfile.objects.filter(user=request.user).first()
        today = datetime.now().date()
        
        attendance = AttendanceTracking.objects.filter(
            staff=staff,
            date_work=today
        ).first()
        
        return JsonResponse({
            'has_checkin': attendance is not None,
            'checkin_time': attendance.checkin.strftime('%H:%M') if attendance else None,
            'checkout_time': attendance.checkout.strftime('%H:%M') if attendance and attendance.checkout else None
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def check_attendance(request):
    try:
        staff = StaffProfile.objects.filter(user=request.user).first()
        today = datetime.now().date()
        current_time = datetime.now().time()
        
        attendance, created = AttendanceTracking.objects.get_or_create(
            staff=staff,
            date_work=today,
            defaults={
                'checkin': current_time,
                'is_late': current_time > time(8, 0)
            }
        )
        
        if not created:
            attendance.checkout = current_time
            checkin_datetime = datetime.combine(today, attendance.checkin)
            checkout_datetime = datetime.combine(today, current_time)
            working_hours = (checkout_datetime - checkin_datetime).total_seconds() / 3600
            attendance.total_working = round(working_hours, 2)
            attendance.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Đã check-out thành công!',
                'checkout_time': current_time.strftime('%H:%M')
            })
        
        return JsonResponse({
            'status': 'success',
            'message': 'Đã check-in thành công!',
            'checkin_time': current_time.strftime('%H:%M')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


