from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from .models import SecurityQuestions
from django.contrib.auth.models import User  # Import the User model


class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))


class CustomUserCreationForm(UserCreationForm):
    monthly_budget = forms.IntegerField(
        label='Monthly Budget',
        required=False,  # Make it optional if you want
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    yearly_income = forms.IntegerField(
        label='Yearly Income',
        required=False,  # Make it optional if you want
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    SECURITY_QUESTIONS = [
        ('What was your first pet\'s name?', 'What was your first pet\'s name?'),
        ('What city were you born in?', 'What city were you born in?'),
        ('What is your mother\'s maiden name?', 'What is your mother\'s maiden name?'),
        ('What was the name of your first school?', 'What was the name of your first school?'),
    ]

    security_question_1 = forms.ChoiceField(choices=SECURITY_QUESTIONS)
    security_answer_1 = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    security_question_2 = forms.ChoiceField(choices=SECURITY_QUESTIONS)
    security_answer_2 = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'email', 'password1', 'password2',
                          'monthly_budget', 'yearly_income',
                          'security_question_1', 'security_answer_1',
                          'security_question_2', 'security_answer_2']:
            self.fields[fieldname].help_text = None
            if fieldname not in ['security_question_1', 'security_question_2']:
                self.fields[fieldname].widget.attrs.update(
                    {'class': 'form-control'}
                )


class SecurityQuestionsForm(forms.Form):
    username = forms.CharField(max_length=150)
    answer = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super(SecurityQuestionsForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'answer']:
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )


class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        for fieldname in ['new_password1', 'new_password2']:
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The passwords don't match")
        return cleaned_data

