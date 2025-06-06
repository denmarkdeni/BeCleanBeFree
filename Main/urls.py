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

    path('upload/awareness/', views.upload_awareness_post, name='upload_awareness'),
    path('upload/news/', views.upload_news_post, name='upload_news'),
    path('upload/recovery/', views.upload_recovery_tip, name='upload_recovery'),
    path('upload/quiz/', views.upload_quiz, name='upload_quiz'),
    path('upload/question/', views.upload_question, name='upload_question'),

    path('upload/report/', views.upload_report, name='upload_report'),

    path('quiz/attend/', views.attend_quiz, name='attend_quiz'),
    path('quiz/result/', views.quiz_result, name='quiz_result'),

    path('view/awareness/', views.view_awareness_posts, name='view_awareness_posts'),
    path('view/news/', views.view_news_posts, name='view_news_posts'),
    path('view/recovery/', views.view_recovery_tips, name='view_recovery_tips'),
    path('view/post/<str:model_type>/<int:post_id>/', views.view_post_details, name='view_post_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)