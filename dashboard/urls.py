from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='dashboard.index'),
    path('adjust-budget/', views.adjust_budget, name='dashboard.adjust_budget'),
    path('add-budget-category/', views.add_budget_category, name='dashboard.add_budget_category'),
    path('add-transaction/', views.add_transaction, name='dashboard.add_transaction'),
    path('profile', views.profile, name='dashboard.profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('category/<int:category_id>/delete/', views.delete_budget_category, name='delete_budget_category'),
    path('fetch-transactions/', views.fetch_and_log_transactions, name='fetch_transactions'),
    path('uncategorized-transactions/', views.list_uncategorized_transactions, name='uncategorized_transactions'),
    path('categorize-transaction/<int:transaction_id>/', views.categorize_transaction, name='categorize_transaction')
]