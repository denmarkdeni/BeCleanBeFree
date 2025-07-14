from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('counselor', 'Counselor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', default='profiles/user-icon.png')
    specialization = models.CharField(max_length=255, blank=True, null=True)
    availability = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class AwarenessPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='awareness_images/', blank=True, null=True)
    source_link = models.URLField(blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)  # Admin moderation

    def __str__(self):
        return self.title
    
class NewsPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    source_link = models.URLField(blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"News: {self.title}"

class RecoveryTipPost(models.Model):
    CATEGORY_CHOICES = [
        ('nutrition', 'Nutrition'),
        ('mental', 'Mental Health'),
        ('physical', 'Physical Health'),
        ('medicine', 'Medicine'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()
    image = models.ImageField(upload_to='recovery_images/', blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    source_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"

class Quiz(models.Model):
    CATEGORY_CHOICES = [
        ('nutrition', 'Nutrition'),
        ('mental', 'Mental Health'),
        ('physical', 'Physical Health'),
        ('medicine', 'Medicine'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    
    def __str__(self):
        return self.question_text

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  

    def __str__(self):
        return self.option_text

class UserQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"
    
class Report(models.Model):
    CATEGORY_CHOICES = [
        ('drug', 'Drug Abuse'),
        ('crime', 'Crime'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Allow anonymous
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class ConsultationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    TYPE_CHOICES = [
        ('video', 'Video'),
        ('phone', 'Phone'),
        ('in-person', 'In-Person'),
    ]
    URGENCY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultation_requests')
    counselor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='consultation_requests')
    preferred_date = models.DateTimeField()
    consultation_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='video')
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='normal')
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.counselor.user.username} ({self.status})"

class Consultation(models.Model):
    request = models.ForeignKey(ConsultationRequest, on_delete=models.CASCADE, related_name='consultations')
    date = models.DateTimeField()
    duration = models.IntegerField()  # Duration in minutes
    notes = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation: {self.request.user.username} with {self.request.counselor.user.username}"