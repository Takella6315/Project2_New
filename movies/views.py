# movies/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, BudgetCategory  # Import BudgetCategory
from django.contrib.auth.decorators import login_required
from .forms import AdjustBudgetForm, AddCategoryForm
from django.http import JsonResponse


@login_required
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies

    # Get the user's monthly budget
    if hasattr(request.user, 'userprofile'):
        template_data['monthly_budget'] = request.user.userprofile.monthly_budget
    else:
        template_data['monthly_budget'] = 0  # Or some other default value

    # Get the user's budget categories
    template_data['budget_categories'] = BudgetCategory.objects.filter(user=request.user)

    return render(request, 'movies/index.html', {'template_data': template_data})



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

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)
