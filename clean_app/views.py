# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AwarenessPost, NewsPost, RecoveryTipPost, Report
from .models import Quiz, Option, Question, UserQuizResult

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
    results = UserQuizResult.objects.filter(user=request.user)
    quiz_marks = sum(result.score for result in results)
    score_percentage = (quiz_marks / results.count()) * 100 if results.count() > 0 else 0
    total_cases = Report.objects.filter(user=request.user).count()
    resolved_cases = Report.objects.filter(user=request.user, is_resolved=True).count()
    unresolved_cases = Report.objects.filter(user=request.user, is_resolved=False).count()
    awareness_posts = AwarenessPost.objects.all().order_by('-created_at')[:2]
    news_posts = NewsPost.objects.all().order_by('-created_at')[:2]
    recovery_tips = RecoveryTipPost.objects.all().order_by('-created_at')[:2]
    context = {
        'quiz_marks': quiz_marks,
        'score_percentage': score_percentage,
        'total_quizzes' : results.count(),
        'total_cases': total_cases,
        'resolved_cases': resolved_cases,
        'unresolved_cases': unresolved_cases,
        'awareness_posts': awareness_posts,
        'news_posts': news_posts,
        'recovery_tips': recovery_tips,
    }
    return render(request, 'user_dashboard.html', context)

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

        Quiz.objects.create(
            title=title,
            description=description,
            category=category,
        )

        messages.success(request, 'Quiz Category uploaded successfully!')
        return redirect('upload_quiz')

    return render(request, 'post_upload_pages/upload_quiz.html')

@login_required
def upload_question(request):
    quizzes = Quiz.objects.all()
    if request.method == 'POST':
        quiz_id = request.POST.get('quiz')
        question_text = request.POST.get('question_text')
        options = request.POST.getlist('option_text')
        correct_option = request.POST.get('correct_option')

        quiz = Quiz.objects.get(id=quiz_id)
        question = Question.objects.create(quiz=quiz, question_text=question_text)

        for idx, option_text in enumerate(options):
            is_correct = str(idx) == correct_option
            Option.objects.create(question=question, option_text=option_text, is_correct=is_correct)

        messages.success(request, 'Quiz Question uploaded successfully!')
        return redirect('upload_question')

    return render(request, 'post_upload_pages/upload_question.html', {'quizzes': quizzes})

@login_required
def attend_quiz(request):
    if request.method == 'POST':
        quiz_id = request.POST.get("quiz_id")
        quiz = Quiz.objects.get(id=quiz_id)

        if UserQuizResult.objects.filter(user=request.user, quiz=quiz).exists():
            messages.error(request, 'You have already submitted this quiz.')
            return redirect('attend_quiz')
        

        for question in quiz.questions.all():
            total_score = 0 
            selected_option_id = request.POST.get(str(question.id))
            if selected_option_id:
                selected_option = Option.objects.get(id=selected_option_id)
                if selected_option.is_correct:
                    total_score += 1

            # Save each question result
            UserQuizResult.objects.create(
                user=request.user,
                question=question,
                quiz=quiz,
                score=total_score  # Optional: you can store per-question score if needed
            )

        messages.success(request, 'Quiz submitted successfully!')
        return redirect('attend_quiz')  

    # ✅ Get all quizzes the user has NOT attempted
    attended_quiz_ids = UserQuizResult.objects.filter(user=request.user).values_list('quiz_id', flat=True).distinct()
    quizzes = Quiz.objects.exclude(id__in=attended_quiz_ids).prefetch_related('questions__options')

    return render(request, 'quiz/attend_quiz.html', {'quizzes': quizzes})

@login_required
def quiz_result(request):
    results = UserQuizResult.objects.filter(user=request.user).order_by('-completed_at')
    return render(request, 'quiz/quiz_result.html', {'results': results})

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

def quiz_result(request):
    user = request.user
    results = UserQuizResult.objects.filter(user=user).order_by('-completed_at')
    Total_score = sum(result.score for result in results)

    quiz_scores = []
    for result in results:
        
        quiz_scores.append({
            'quiz_title': result.quiz.title,
            'question_text': result.question.question_text,
            'score': result.score,
            'completed_at': result.completed_at
        })

    context = {
        'quiz_scores': quiz_scores,
        'total_score': Total_score,
    }
    
    return render(request, 'quiz/quiz_result.html', context)

def upload_report(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        Report.objects.create(
            user=request.user if request.user.is_authenticated else None,
            title=title,
            category=category,
            description=description,
            image=image
        )

        messages.success(request, "Your report has been submitted successfully.")
        return redirect('upload_report')  
    
    return render(request, 'report/upload_report.html')
