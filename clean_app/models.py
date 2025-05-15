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
    profile_pic = models.ImageField(upload_to='profiles/', default='static/images/user-icon.png')

    def __str__(self):
        return f"{self.user.username} ({self.role})"
