from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BudgetCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True) # Description of item added
    date = models.DateField(default=timezone.now) # Default = today
    created_at = models.DateTimeField(auto_now_add=True) # Date added

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - ${self.amount} on {self.date}"

    class Meta:
        ordering = ['-date', '-created_at']