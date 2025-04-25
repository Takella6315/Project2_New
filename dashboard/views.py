# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, BudgetCategory  # Import BudgetCategory
from django.contrib.auth.decorators import login_required
from .forms import AdjustBudgetForm, AddCategoryForm
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage


@login_required
def index(request):
    template_data = {}
    if hasattr(request.user, 'userprofile'):
        template_data['monthly_budget'] = request.user.userprofile.monthly_budget
    else:
        template_data['monthly_budget'] = 0  # Or some other default value

    budget_categories = BudgetCategory.objects.filter(user=request.user)
    template_data['budget_categories'] = budget_categories
    template_data['total_spent'] = sum(cat.amount_spent for cat in budget_categories)

    return render(request, 'dashboard/index.html', {'template_data': template_data})
@login_required
def adjust_budget(request):
    if request.method == 'POST':
        form = AdjustBudgetForm(request.POST)
        if form.is_valid():
            new_budget = form.cleaned_data['new_budget']
            user_profile = request.user.userprofile
            user_profile.monthly_budget = new_budget
            user_profile.save()
            return JsonResponse({'status': 'success', 'new_budget': new_budget})
        else:
            return JsonResponse({'status': 'error', 'error': form.errors.as_json()}, status=400)
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)

@login_required
def add_budget_category(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category_limit = form.cleaned_data['category_limit']
            category_spent = form.cleaned_data['category_spent']

            budget_category = BudgetCategory(
                user=request.user,
                name=category_name,
                budget_limit=category_limit,
                amount_spent=category_spent,
            )
            budget_category.save()

            #  Return the new category data so it can be displayed by the javascript.
            return JsonResponse({
                'status': 'success',
                'category_name': category_name,
                'category_limit': category_limit,
                'category_spent': category_spent,
                'category_id': budget_category.id, #  include the ID
            })
        else:
            return JsonResponse({'status': 'error', 'error': form.errors.as_json()}, status=400)
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)

@login_required
def profile(request):
    user_profile = request.user.userprofile
    budget_categories = BudgetCategory.objects.filter(user=request.user)
    template_data = {}
    template_data['title'] = 'Profile'
    return render(request, 'dashboard/profile.html', {'template_data': template_data})

@login_required
def upload_profile_picture(request):
    if request.method == "POST" and request.FILES.get('profile_picture'):
        user_profile = request.user.userprofile
        profile_picture = request.FILES['profile_picture']
        fs = FileSystemStorage()
        filename = fs.save(f"profile_pictures/{request.user.id}/{profile_picture.name}", profile_picture)
        user_profile.profile_picture = fs.url(filename)
        user_profile.save()
        return JsonResponse({'status': 'success', 'image_url': user_profile.profile_picture})
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)