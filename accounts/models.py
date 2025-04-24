# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile', primary_key=True)
    monthly_budget = models.IntegerField(default=0, blank=True, null=True)
    yearly_income = models.IntegerField(default=0, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)

    def __str__(self):
        return self.user.username

class SecurityQuestions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    question_1 = models.CharField(max_length=200)
    answer_1 = models.CharField(max_length=200)
    question_2 = models.CharField(max_length=200)
    answer_2 = models.CharField(max_length=200)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()