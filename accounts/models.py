from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    monthly_budget = models.IntegerField(default=0, blank=True, null=True)
    yearly_income = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.user.username

class SecurityQuestions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    question_1 = models.CharField(max_length=200)
    answer_1 = models.CharField(max_length=200)
    question_2 = models.CharField(max_length=200)
    answer_2 = models.CharField(max_length=200)