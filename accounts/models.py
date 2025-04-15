from django.db import models
from django.contrib.auth.models import User

class SecurityQuestions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    question_1 = models.CharField(max_length=200)
    answer_1 = models.CharField(max_length=200)
    question_2 = models.CharField(max_length=200)
    answer_2 = models.CharField(max_length=200)