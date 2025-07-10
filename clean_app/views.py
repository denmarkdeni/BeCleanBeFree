# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AwarenessPost, NewsPost, RecoveryTipPost, Report
from .models import Quiz, Option, Question, UserQuizResult, Profile, Consultation, ConsultationRequest
from django.urls import reverse
from urllib.parse import urlencode

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
            print(request.POST)
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
    consultations = ConsultationRequest.objects.filter(user=request.user).count()
    consultations_pending = ConsultationRequest.objects.filter(user=request.user, status='pending').count()
    consultations_completed = ConsultationRequest.objects.filter(user=request.user, status='completed').count()
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
        'consultations': consultations,
        'consultations_pending': consultations_pending,
        'consultations_completed': consultations_completed,
    }
    return render(request, 'user_dashboard.html', context)

@login_required
def counselor_dashboard(request):
    if request.user.profile.role != 'counselor':
        messages.error(request, 'Access denied. Only counselors can view this page.')
        return redirect('user_profile')
    
    counselor = request.user.profile
    
    total_posts = (AwarenessPost.objects.filter(posted_by=request.user).count() + 
                   NewsPost.objects.filter(posted_by=request.user).count() + 
                   RecoveryTipPost.objects.filter(posted_by=request.user).count())
    pending_posts = (AwarenessPost.objects.filter(posted_by=request.user, is_approved=False).count() + 
                    NewsPost.objects.filter(posted_by=request.user, is_approved=False).count() + 
                    RecoveryTipPost.objects.filter(posted_by=request.user, is_approved=False).count())
    approved_posts = (AwarenessPost.objects.filter(posted_by=request.user, is_approved=True).count() + 
                     NewsPost.objects.filter(posted_by=request.user, is_approved=True).count() + 
                     RecoveryTipPost.objects.filter(posted_by=request.user, is_approved=True).count())
    
    total_quizzes = Question.objects.filter(uploaded_by=request.user).count()
    quiz_responses = UserQuizResult.objects.filter(question__uploaded_by=request.user).count()
    
    total_consultations = Consultation.objects.filter(request__counselor=counselor).count()
    completed_consultations = Consultation.objects.filter(request__counselor=counselor, request__status='completed').count()
    feedbacks_taken = Consultation.objects.filter(request__counselor=counselor, feedback__isnull=False).count()
    
    context = {
        'total_posts': total_posts,
        'pending_posts': pending_posts,
        'approved_posts': approved_posts,
        'total_quizzes': total_quizzes,
        'quiz_responses': quiz_responses,
        'total_consultations': total_consultations,
        'completed_consultations': completed_consultations,
        'feedbacks_taken': feedbacks_taken,
        'consultations': Consultation.objects.all().order_by('-created_at')[:4],
    }
    return render(request, 'counselor_dashboard.html', context)

def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Only admins can view this page.')
        return redirect('user_profile')
    
    total_reports = Report.objects.count()
    resolved_reports = Report.objects.filter(is_resolved=True).count()
    rejected_reports = Report.objects.filter(is_resolved=False).count()  # Assuming unresolved reports are rejected
    
    normal_users = Profile.objects.filter(role='user').count()
    counselors = Profile.objects.filter(role='counselor').count()
    total_users = normal_users+counselors
    
    total_posts = (AwarenessPost.objects.count() + 
                   NewsPost.objects.count() + 
                   RecoveryTipPost.objects.count())
    pending_posts = (AwarenessPost.objects.filter(is_approved=False).count() + 
                    NewsPost.objects.filter(is_approved=False).count() + 
                    RecoveryTipPost.objects.filter(is_approved=False).count())
    approved_posts = (AwarenessPost.objects.filter(is_approved=True).count() + 
                     NewsPost.objects.filter(is_approved=True).count() + 
                     RecoveryTipPost.objects.filter(is_approved=True).count())
    
    context = {
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'rejected_reports': rejected_reports,
        'total_users': total_users,
        'normal_users': normal_users,
        'counselors': counselors,
        'total_posts': total_posts,
        'pending_posts': pending_posts,
        'approved_posts': approved_posts,
        'reports': Report.objects.all().order_by('-created_at')[:4],
    }
    return render(request, 'admin_dashboard.html', context)

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

def user_management(request):
    profiles = Profile.objects.all()
    return render(request, 'admin/user_management.html', {'profiles': profiles})

def activate_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'{user.username} has been activated.')
    return redirect('user_management')

def deactivate_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'{user.username} has been deactivated.')
    return redirect('user_management')

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f'{username} has been deleted.')
    return redirect('user_management')

def post_management(request):
    post_type = request.GET.get('type', 'awareness')
    if post_type == 'news':
        posts = NewsPost.objects.all()
    elif post_type == 'recovery':
        posts = RecoveryTipPost.objects.all()
    else:
        posts = AwarenessPost.objects.all()
    return render(request, 'admin/post_management.html', {'posts': posts, 'post_type': post_type})

def approve_post(request, post_type, post_id):
    if post_type == 'news':
        post = NewsPost.objects.get(id=post_id)
    elif post_type == 'recovery':
        post = RecoveryTipPost.objects.get(id=post_id)
    else:
        post = AwarenessPost.objects.get(id=post_id)
    post.is_approved = True
    post.save()
    messages.success(request, f'Post "{post.title}" has been approved.')
    return redirect(reverse('post_management') + '?' + urlencode({'type': post_type}))

def delete_post(request, post_type, post_id):
    if post_type == 'news':
        post = NewsPost.objects.get(id=post_id)
    elif post_type == 'recovery':
        post = RecoveryTipPost.objects.get(id=post_id)
    else:
        post = AwarenessPost.objects.get(id=post_id)
    title = post.title
    post.delete()
    messages.success(request, f'Post "{title}" has been deleted.')
    return redirect(reverse('post_management') + '?' + urlencode({'type': post_type}))

def report_management(request):
    reports = Report.objects.all()
    return render(request, 'admin/report_management.html', {'reports': reports})

def resolve_report(request, report_id):
    report = Report.objects.get(id=report_id)
    report.is_resolved = True
    report.save()
    messages.success(request, f'Report "{report.title}" has been resolved.')
    return redirect('report_management')

def delete_report(request, report_id):
    report = Report.objects.get(id=report_id)
    title = report.title
    report.delete()
    messages.success(request, f'Report "{title}" has been deleted.')
    return redirect('report_management')

@login_required
def user_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        bio = request.POST.get('bio')
        phone = request.POST.get('phone')
        profile_pic = request.FILES.get('profile_pic')
        profile.bio = bio
        profile.phone = phone
        if profile_pic:
            profile.profile_pic = profile_pic
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('user_profile')
    return render(request, 'profiles/user_profile.html', {'profile': profile, 'user': request.user})

@login_required
def counselor_profile(request):
    profile = request.user.profile
    if profile.role != 'counselor':
        messages.error(request, 'Access denied. Only counselors can edit this profile.')
        return redirect('user_profile')
    if request.method == 'POST':
        bio = request.POST.get('bio')
        phone = request.POST.get('phone')
        profile_pic = request.FILES.get('profile_pic')
        specialization = request.POST.get('specialization')
        availability = request.POST.get('availability')
        profile.bio = bio
        profile.phone = phone
        profile.specialization = specialization
        profile.availability = availability
        if profile_pic:
            profile.profile_pic = profile_pic
        profile.save()
        messages.success(request, 'Counselor profile updated successfully.')
        return redirect('counselor_profile')
    return render(request, 'profiles/counselor_profile.html', {'profile': profile, 'user': request.user})

@login_required
def counselors_list(request):
    counselors = Profile.objects.filter(role='counselor')
    return render(request, 'consultation/counselors_list.html', {'counselors': counselors})

@login_required
def request_consultation(request, counselor_id):
    counselor = Profile.objects.get(id=counselor_id, role='counselor')
    if request.method == 'POST':
        preferred_date = request.POST.get('preferred_date')
        consultation_type = request.POST.get('consultation_type')
        urgency = request.POST.get('urgency')
        notes = request.POST.get('notes')
        ConsultationRequest.objects.create(
            user=request.user,
            counselor=counselor,
            preferred_date=preferred_date,
            consultation_type=consultation_type,
            urgency=urgency,
            notes=notes
        )
        messages.success(request, 'Consultation request submitted successfully.')
        return redirect('counselors_list')
    return render(request, 'consultation/request_consultation.html', {'counselor': counselor})

@login_required
def user_consultation_history(request):
    consultations = Consultation.objects.filter(request__user=request.user).order_by('-date')
    return render(request, 'consultation/user_consultation_history.html', {'consultations': consultations})

@login_required
def submit_feedback(request, consultation_id):
    consultation = Consultation.objects.get(id=consultation_id, request__user=request.user)
    if consultation.request.status != 'completed':
        messages.error(request, 'Feedback can only be submitted for completed consultations.')
        return redirect('user_consultation_history')
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        rating = request.POST.get('rating')
        consultation.feedback = feedback
        consultation.rating = rating
        consultation.save()
        messages.success(request, 'Feedback submitted successfully.')
        return redirect('user_consultation_history')
    return render(request, 'consultation/submit_feedback.html', {'consultation': consultation})

@login_required
def counselor_appointments(request):
    if request.user.profile.role != 'counselor':
        messages.error(request, 'Access denied. Only counselors can view appointments.')
        return redirect('user_profile')
    requests = ConsultationRequest.objects.filter(counselor=request.user.profile).order_by('-created_at')
    return render(request, 'consultation/counselor_appointments.html', {'requests': requests})

@login_required
def accept_request(request, request_id):
    if request.user.profile.role != 'counselor':
        messages.error(request, 'Access denied. Only counselors can accept requests.')
        return redirect('user_profile')
    consultation_request = ConsultationRequest.objects.get(id=request_id, counselor=request.user.profile)
    consultation_request.status = 'accepted'
    consultation_request.save()
    messages.success(request, 'Consultation request accepted.')
    return redirect('counselor_appointments')

@login_required
def reject_request(request, request_id):
    if request.user.profile.role != 'counselor':
        messages.error(request, 'Access denied. Only counselors can reject requests.')
        return redirect('user_profile')
    consultation_request = ConsultationRequest.objects.get(id=request_id, counselor=request.user.profile)
    consultation_request.status = 'rejected'
    consultation_request.save()
    messages.success(request, 'Consultation request rejected.')
    return redirect('counselor_appointments')

@login_required
def consultation_details(request, request_id):
    if request.user.profile.role != 'counselor':
        messages.error(request, 'Access denied. Only counselors can view consultation details.')
        return redirect('user_profile')
    consultation_request = ConsultationRequest.objects.get(id=request_id, counselor=request.user.profile)
    consultation = Consultation.objects.filter(request=consultation_request).first()
    if request.method == 'POST' and consultation_request.status == 'accepted' and not consultation:
        date = request.POST.get('date')
        duration = request.POST.get('duration')
        notes = request.POST.get('notes')
        Consultation.objects.create(
            request=consultation_request,
            date=date,
            duration=duration,
            notes=notes
        )
        consultation_request.status = 'completed'
        consultation_request.save()
        messages.success(request, 'Consultation completed successfully.')
        return redirect('counselor_appointments')
    return render(request, 'consultation/consultation_details.html', {'consultation_request': consultation_request, 'consultation': consultation})

@login_required
def counselor_consultation_history(request):
    if request.user.profile.role != 'counselor':
        messages.error(request, 'Access denied. Only counselors can view consultation history.')
        return redirect('user_profile')
    consultations = Consultation.objects.filter(request__counselor=request.user.profile).order_by('-date')
    print(consultations ,1)
    print(consultations ,1)
    return render(request, 'consultation/counselor_consultation_history.html', {'consultations': consultations})

@login_required
def consultations_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Only admins can view this page.')
        return redirect('user_profile')
    consultations = ConsultationRequest.objects.all().order_by('-created_at')
    return render(request, 'admin/consultations_list.html', {'consultations': consultations})