# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, BudgetCategory, Transaction
from django.contrib.auth.decorators import login_required
from .forms import AdjustBudgetForm, AddCategoryForm, TransactionForm
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.db.models import F, Sum



@login_required
def index(request):
    template_data = {}
    if hasattr(request.user, 'userprofile'):
        template_data['monthly_budget'] = request.user.userprofile.monthly_budget
    else:
        template_data['monthly_budget'] = 0

    budget_categories = BudgetCategory.objects.filter(user=request.user)
    template_data['budget_categories'] = budget_categories
    template_data['total_spent'] = sum(cat.amount_spent for cat in budget_categories)

    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')[:10] # Get last 10
    template_data['recent_transactions'] = recent_transactions

    transaction_form = TransactionForm(user=request.user)
    template_data['transaction_form'] = transaction_form

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
            try:
                category_name = form.cleaned_data['category_name']
                category_limit = form.cleaned_data['category_limit']

                budget_category = BudgetCategory(
                    user=request.user,
                    name=category_name,
                    budget_limit=category_limit,
                )
                budget_category.save()

                return JsonResponse({
                    'status': 'success',
                    'category_name': category_name,
                    'category_limit': f"{budget_category.budget_limit:.2f}",
                    'category_spent': "0.00",
                    'category_id': budget_category.id,
                })
            except Exception as e:
                 return JsonResponse({'status': 'error', 'error': f'An error occurred saving the category: {str(e)}'}, status=500)
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'status': 'error', 'error': 'Form validation failed', 'form_errors': errors}, status=400)
    return JsonResponse({'status': 'error', 'error': 'Invalid request method'}, status=400)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()

                category = transaction.category
                category.amount_spent = F('amount_spent') + transaction.amount
                category.save(update_fields=['amount_spent'])
                category.refresh_from_db() 

                
                total_spent_updated = BudgetCategory.objects.filter(user=request.user).aggregate(total=Sum('amount_spent'))['total'] or 0

                
                return JsonResponse({
                    'status': 'success',
                    'transaction': {
                        'id': transaction.id,
                        'category_name': transaction.category.name,
                        'category_id': transaction.category.id,
                        'amount': f"{transaction.amount:.2f}", 
                        'description': transaction.description or '', 
                        'date': transaction.date.strftime('%Y-%m-%d'),
                    },
                    'updated_category_spent': f"{category.amount_spent:.2f}",
                    'total_spent': f"{total_spent_updated:.2f}",
                })
            except Exception as e:
                 return JsonResponse({'status': 'error', 'error': f'An error occurred: {str(e)}'}, status=500)
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'status': 'error', 'error': 'Form validation failed', 'form_errors': errors}, status=400)
    return JsonResponse({'status': 'error', 'error': 'Invalid request method'}, status=400)

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