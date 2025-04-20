from django.contrib import admin
from .models import SecurityQuestions, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Unregister the default UserAdmin
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'monthly_budget', 'yearly_income')

    def monthly_budget(self, obj):
        return obj.userprofile.monthly_budget
    monthly_budget.short_description = 'Monthly Budget'

    def yearly_income(self, obj):
        return obj.userprofile.yearly_income
    yearly_income.short_description = 'Yearly Income'

admin.site.register(User, CustomUserAdmin)
admin.site.register(SecurityQuestions)