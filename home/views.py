from django.shortcuts import render
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from leave.models import Leave
from staff.models import StaffProfile
from attendance.models import AttendanceTracking
from reviews.models import Salary
# from nghiphep.models import LeaveRequest  # Giả sử model nghỉ phép của bạn là LeaveRequest
from authentication.decorators import admin_required

@admin_required
def dashboard(request):
    # Tổng số nhân viên
    total_employees = StaffProfile.objects.count()
    
    # Thống kê chấm công hôm nay
    today = timezone.now().date()
    today_attendance = AttendanceTracking.objects.filter(date_work=today)
    total_attendance = today_attendance.count()
    on_time_attendance = today_attendance.filter(is_late=False).count()
    
    # Tính tỉ lệ đi làm đúng giờ
    attendance_rate = (on_time_attendance / total_attendance * 100) if total_attendance > 0 else 0
    
    # Số lượng yêu cầu nghỉ phép đang chờ duyệt
    pending_leaves = Leave.objects.filter(
        status='Đang chờ',
        created_at__month=today.month,
        created_at__year=today.year
    ).count()
    
    total_salary = Salary.objects.filter(
        pay_date__month=today.month,
        pay_date__year=today.year
    ).aggregate(total=Sum('total_salary'))['total'] or 0
    
    context = {
        'total_employees': total_employees,
        'total_attendance': total_attendance,
        'on_time_attendance': on_time_attendance,
        'attendance_rate': round(attendance_rate, 1),
        'pending_leaves': pending_leaves,
        'total_salary': total_salary,
        # Thêm thông tin chi tiết
        'attendance_stats': {
            'on_time': on_time_attendance,
            'late': total_attendance - on_time_attendance,
            'total': total_attendance,
        },
    }
    
    return render(request, 'home.html', context)

def dashboard_staff(request):
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Lấy thông tin đi trễ trong tháng
    late_stats = AttendanceTracking.objects.filter(
        staff__user=request.user,
        date_work__month=current_month,
        date_work__year=current_year,
        is_late=True
    ).aggregate(
        late_days=Count('id')
    )

    # Lấy số lượng yêu cầu nghỉ phép trong tháng
    leave_count = Leave.objects.filter(
        staff=request.user.staff_profile,
        created_at__month=current_month,
        created_at__year=current_year
    ).count()

    context = {
        'current_month': today.strftime('%m/%Y'),
        'late_days': late_stats['late_days'] or 0,
        'leave_requests': leave_count,
        'staff': request.user
    }

    return render(request, 'home_staff.html', context)
