from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Kiểm tra đã đăng nhập chưa
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để tiếp tục.')
            return redirect('authentication:login')
        
        # Kiểm tra có phải admin không (sử dụng is_superuser)
        if not request.user.is_superuser:
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('home:dashboard_staff')  # Chuyển hướng về dashboard của staff
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view 