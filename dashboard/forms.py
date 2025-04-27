from django import forms
from .models import BudgetCategory, Transaction

class AdjustBudgetForm(forms.Form):
    new_budget = forms.DecimalField(label='New Monthly Budget', min_value=0)

class AddCategoryForm(forms.Form):
    category_name = forms.CharField(label='Category Name', max_length=255)
    category_limit = forms.DecimalField(label='Budget Limit', min_value=0)

class TransactionForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = BudgetCategory.objects.filter(user=user)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description', 'date']
        labels = {
            'amount': 'Amount ($)',
            'description': 'Description (Optional)',
            'date': 'Date',
            'category': 'Category'
        }

# class AdjustBudgetForm(forms.Form):
#     new_budget = forms.IntegerField(
#         label='New Monthly Budget',
#         min_value=0,  # Ensure the budget is not negative
#         required=True,
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )


# class AddCategoryForm(forms.Form):
#     category_name = forms.CharField(
#         label='Category Name',
#         max_length=255,
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )
#     category_limit = forms.IntegerField(
#         label='Budget Limit',
#         min_value=0,
#         required=True,
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )
#     category_spent = forms.IntegerField(
#         label='Amount Spent',
#         min_value=0,
#         required=True,
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )