from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    print("Signal triggered" , instance, created)
    if created:
        if instance.is_superuser:
            Profile.objects.create(user=instance, role='admin')
        else:
            Profile.objects.create(user=instance)
    instance.profile.save()
