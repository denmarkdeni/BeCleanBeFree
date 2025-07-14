"""
URL configuration for Main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clean_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/counselor/', views.counselor_dashboard, name='counselor_dashboard'),

    path('user_management', views.user_management, name='user_management'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    path('post-management/', views.post_management, name='post_management'),
    path('approve-post/<str:post_type>/<int:post_id>/', views.approve_post, name='approve_post'),
    path('delete-post/<str:post_type>/<int:post_id>/', views.delete_post, name='delete_post'),

    path('report-management/', views.report_management, name='report_management'),
    path('resolve-report/<int:report_id>/', views.resolve_report, name='resolve_report'),
    path('delete-report/<int:report_id>/', views.delete_report, name='delete_report'),

    path('consultations-list/', views.consultations_list, name='consultations_list'),

    path('user-profile/', views.user_profile, name='user_profile'),
    path('counselor-profile/', views.counselor_profile, name='counselor_profile'),

    path('upload/awareness/', views.upload_awareness_post, name='upload_awareness'),
    path('upload/news/', views.upload_news_post, name='upload_news'),
    path('upload/recovery/', views.upload_recovery_tip, name='upload_recovery'),
    path('upload/quiz/', views.upload_quiz, name='upload_quiz'),
    path('upload/question/', views.upload_question, name='upload_question'),

    path('upload/report/', views.upload_report, name='upload_report'),

    path('quiz/attend/', views.attend_quiz, name='attend_quiz'),
    path('quiz/result/', views.quiz_result, name='quiz_result'),
    path('question-details/', views.question_details, name='question_details'),

    path('view/awareness/', views.view_awareness_posts, name='view_awareness_posts'),
    path('view/news/', views.view_news_posts, name='view_news_posts'),
    path('view/recovery/', views.view_recovery_tips, name='view_recovery_tips'),
    path('view/post/<str:model_type>/<int:post_id>/', views.view_post_details, name='view_post_details'),

    path('counselors/', views.counselors_list, name='counselors_list'),
    path('request-consultation/<int:counselor_id>/', views.request_consultation, name='request_consultation'),
    path('consultation-history/', views.user_consultation_history, name='user_consultation_history'),
    path('submit-feedback/<int:consultation_id>/', views.submit_feedback, name='submit_feedback'),
    path('counselor-appointments/', views.counselor_appointments, name='counselor_appointments'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('consultation-details/<int:request_id>/', views.consultation_details, name='consultation_details'),
    path('counselor-consultation-history/', views.counselor_consultation_history, name='counselor_consultation_history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)