from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def login_view(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect(get_success_url(request.user))
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        try:
            # Lấy username từ email
            user = User.objects.get(email=email)
            # Xác thực với username và password
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                
                if not remember_me:
                    request.session.set_expiry(0)
                    
                return redirect(get_success_url(user))
            else:
                return render(request, 'login.html', {
                    'error': 'Invalid email or password'
                })
                
        except User.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'No account found with this email'
            })
            
    return render(request, 'login.html')

def get_success_url(user):
    if user.is_superuser:
        return reverse('home:dashboard')
    elif user.is_staff:
        return reverse('home:dashboard_staff')
    else:
        return reverse('home:dashboard_staff')

@login_required
def logout_view(request):
    logout(request)
    return redirect('authentication:login')
