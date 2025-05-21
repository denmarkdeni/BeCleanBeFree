# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def register(request):
    reg_form = UserRegisterForm()
    login_form = UserLoginForm()
    print(request.POST)
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'register':
            reg_form = UserRegisterForm(request.POST)
            if reg_form.is_valid():
                user = reg_form.save()
                role = reg_form.cleaned_data.get('role')
                user.profile.role = role
                user.profile.save()
                messages.success(request, 'Registration successful!')
                return redirect('register') 
            else:
                messages.error(request, 'Registration failed. Please check the form.')
        elif form_type == 'login':
            login_form = UserLoginForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, 'Login successful!')
                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.profile.role == 'counselor':
                    return redirect('Counselor_dashboard')
                elif user.profile.role == 'user':
                    return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid login credentials.')

    return render(request, 'register.html', {
        'reg_form': reg_form,
        'login_form': login_form
    })

def user_logout(request):
    logout(request)
    messages.success(request, 'Logout Successful!')
    return redirect('register')

def user_dashboard(request):
    return render(request, 'user_dashboard.html')

def counselor_dashboard(request):
    return render(request, 'counselor_dashboard.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')