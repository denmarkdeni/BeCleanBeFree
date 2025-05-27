# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AwarenessPost, NewsPost, RecoveryTipPost

def home(request):
    awareness_posts = AwarenessPost.objects.all().order_by('-created_at')[:15]
    news_posts = NewsPost.objects.all().order_by('-created_at')[:15]
    recovery_posts_all = RecoveryTipPost.objects.all().order_by('-created_at')[:10]
    recovery_post_nutrition = RecoveryTipPost.objects.filter(category='nutrition').order_by('-created_at')[:10]
    recovery_post_mental = RecoveryTipPost.objects.filter(category='mental').order_by('-created_at')[:10]
    recovery_post_physical = RecoveryTipPost.objects.filter(category='physical').order_by('-created_at')[:10]
    recovery_post_medicine = RecoveryTipPost.objects.filter(category='medicine').order_by('-created_at')[:10]
    context = {
        'awareness_posts': awareness_posts,
        'news_posts': news_posts,
        'recovery_posts': recovery_posts_all,
        'recovery_post_nutrition': recovery_post_nutrition,
        'recovery_post_mental': recovery_post_mental,
        'recovery_post_physical': recovery_post_physical,
        'recovery_post_medicine': recovery_post_medicine,
    }
    return render(request, 'home.html', context)

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
                return redirect('dashboard')
                
            else:
                messages.error(request, 'Invalid login credentials.')

    return render(request, 'register.html', {
        'reg_form': reg_form,
        'login_form': login_form
    })

def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.profile.role == 'counselor':
            return redirect('counselor_dashboard')
        elif request.user.profile.role == 'user':
            return redirect('user_dashboard')
    else:
        return redirect('register')  
    
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

@login_required
def upload_awareness_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        # category = request.POST['category']
        image = request.FILES.get('image')
        video_link = request.POST.get('video_link')

        post = AwarenessPost.objects.create(
            title=title,
            content=content,
            image=image,
            video_link=video_link,
            posted_by=request.user,
            is_approved=False  # Wait for admin approval
        )
        messages.success(request, 'Awareness post uploaded successfully!')
        return redirect('upload_awareness') 

    return render(request, 'post_upload_pages/upload_awareness_post.html')

@login_required
def upload_news_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')
        source_link = request.POST.get('source_link')

        NewsPost.objects.create(
            title=title,
            content=content,
            image=image,
            source_link=source_link,
            posted_by=request.user,
            is_approved=False
        )
        messages.success(request, 'News post uploaded successfully!')
        return redirect('upload_news')

    return render(request, 'post_upload_pages/upload_news_post.html')

@login_required
def upload_recovery_tip(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        category = request.POST['category']
        image = request.FILES.get('image')
        video_link = request.POST.get('video_link')

        RecoveryTipPost.objects.create(
            title=title,
            content=content,
            category=category,
            image=image,
            video_link=video_link,
            posted_by=request.user,
            is_approved=False
        )
        messages.success(request, 'Recovery Tips uploaded successfully!')
        return redirect('upload_recovery')

    return render(request, 'post_upload_pages/upload_recovery_tip.html')

@login_required
def upload_quiz(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        category = request.POST['category']

        messages.success(request, 'Quiz uploaded successfully!')
        return redirect('upload_quiz')

    return render(request, 'post_upload_pages/upload_quiz.html')

def view_awareness_posts(request):
    awareness_posts = AwarenessPost.objects.all().order_by('-created_at')
    return render(request, 'view_pages/view_awareness_posts.html', {'awareness_posts': awareness_posts})

def view_news_posts(request):
    news_posts = NewsPost.objects.all().order_by('-created_at')
    return render(request, 'view_pages/view_news_posts.html', {'news_posts': news_posts})

def view_recovery_tips(request):
    recovery_tips = RecoveryTipPost.objects.all().order_by('-created_at')
    return render(request, 'view_pages/view_recovery_tips.html', {'recovery_tips': recovery_tips})

def view_post_details(request, model_type, post_id):
    if model_type == 'awareness':
        post = AwarenessPost.objects.filter(id=post_id).first()
    elif model_type == 'news':
        post = NewsPost.objects.filter(id=post_id).first()
    elif model_type == 'recovery':
        post = RecoveryTipPost.objects.filter(id=post_id).first()
    else:
        messages.error(request, 'Invalid post type.')
        return redirect('user_dashboard')
    return render(request, 'view_pages/view_post_details.html', {'post': post})

