# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import BudgetCategory, Transaction
from django.contrib.auth.decorators import login_required
from .forms import AdjustBudgetForm, AddCategoryForm, TransactionForm
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.db.models import F, Sum
from django.utils import timezone
import datetime
from django.urls import reverse
from django.contrib import messages
from accounts.models import UserProfile
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

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

    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')[:10]
    template_data['recent_transactions'] = recent_transactions

    transaction_form = TransactionForm(user=request.user)
    template_data['transaction_form'] = transaction_form

    today = timezone.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday()) # Monday = start of week
    start_of_month = today.replace(day=1)

    # Calculate Today's Spending
    today_spending_agg = Transaction.objects.filter(
        user=request.user,
        date=today
    ).aggregate(total=Sum('amount'))
    template_data['today_spent'] = today_spending_agg['total'] or 0

    week_spending_agg = Transaction.objects.filter(
        user=request.user,
        date__gte=start_of_week,
        date__lte=today 
    ).aggregate(total=Sum('amount'))
    template_data['week_spent'] = week_spending_agg['total'] or 0

    month_spending_agg = Transaction.objects.filter(
        user=request.user,
        date__gte=start_of_month,
        date__lte=today 
    ).aggregate(total=Sum('amount'))
    template_data['month_spent'] = month_spending_agg['total'] or 0

    return render(request, 'dashboard/index.html', {'template_data': template_data})

@login_required
def create_stripe_connect_link(request):
    """
    Creates Stripe Express account (if needed) and an Account Link
    for Onboarding, then redirects the user to Stripe.
    UserProfile model used to store the stripe_account_id.
    """
    print(f"DEBUG: Stripe Key from settings: '{settings.STRIPE_SECRET_KEY}'") # Add this line
    stripe.api_key = settings.STRIPE_SECRET_KEY # Ensure this line exists too
    user = request.user

    try:
        user_profile = user.userprofile
        stripe_account_id = user_profile.stripe_account_id
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found. Cannot link Stripe account.")
        return redirect('dashboard.index')
    except Exception as e:
         messages.error(request, f"Error accessing user profile: {e}")
         print(f"Error accessing profile for user {user.id}: {e}")
         return redirect('dashboard.index')

    try:
        if not stripe_account_id:
            account = stripe.Account.create(
                type="express",
                email=user.email,
                capabilities={
                   'card_payments': {'requested': True},
                   'transfers': {'requested': True},
                },
            )
            stripe_account_id = account.id
            try:
                user_profile.stripe_account_id = stripe_account_id
                user_profile.save(update_fields=['stripe_account_id'])
                print(f"Saved Stripe Account ID {stripe_account_id} for user {user.id}")
            except Exception as e:
                 print(f"Could not save Stripe ID for user {user.id}: {e}")
                 messages.warning(request, "Could not save Stripe account link reference. Please try again later if needed.")
            print(f"Created Stripe Account: {stripe_account_id}")

        # Define return/refresh URLs (absolute URLs are needed)
        # Ensure these URL names match your dashboard/urls.py
        refresh_url = request.build_absolute_uri(reverse('dashboard.stripe_refresh'))
        return_url = request.build_absolute_uri(reverse('dashboard.stripe_return'))

        account_link = stripe.AccountLink.create(
            account=stripe_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        return redirect(account_link.url)

    except stripe.error.StripeError as e:
        messages.error(request, f"Could not connect to Stripe: {str(e)}")
        print(f"Stripe Error: {e}")
        return redirect('dashboard.index')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        print(f"General Error: {e}")
        return redirect('dashboard.index')
    
@login_required
def stripe_return_view(request):
    messages.info(request, "Returned from Stripe onboarding.")
    return render(request, 'dashboard/stripe_return.html')

@login_required
def stripe_refresh_view(request):
    messages.warning(request, "Stripe connection link expired/was invalid. Please try connecting again.")
    return redirect('dashboard.index')

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


@login_required
def delete_budget_category(request, category_id):

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return a standard HTTP response or an error if accessed directly
        return HttpResponseBadRequest("Invalid request type. AJAX required.")

    try:
        category = get_object_or_404(BudgetCategory, pk=category_id, user=request.user)

        if Transaction.objects.filter(category=category).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot delete category: It has associated transactions. Please reassign or delete them first.'
            }, status=400) # 400 Bad Request is appropriate here

        category_name = category.name # Store name for the success message
        category.delete()

        return JsonResponse({
            'status': 'success',
            'message': f'Category "{category_name}" deleted successfully.'

        })

    except BudgetCategory.DoesNotExist:

        return JsonResponse({'status': 'error', 'message': 'Category not found or you do not have permission to delete it.'}, status=404)
    except Exception as e:

        print(f"Error deleting category {category_id} for user {request.user.id}: {e}") # Basic print for development
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)
