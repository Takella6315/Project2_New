from django import forms


class AdjustBudgetForm(forms.Form):
    new_budget = forms.IntegerField(
        label='New Monthly Budget',
        min_value=0,  # Ensure the budget is not negative
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class AddCategoryForm(forms.Form):
    category_name = forms.CharField(
        label='Category Name',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    category_limit = forms.IntegerField(
        label='Budget Limit',
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    category_spent = forms.IntegerField(
        label='Amount Spent',
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )