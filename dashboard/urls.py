from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='dashboard.index'),
    path('adjust-budget/', views.adjust_budget, name='dashboard.adjust_budget'),
    path('add-budget-category/', views.add_budget_category, name='dashboard.add_budget_category'),
    path('add-transaction/', views.add_transaction, name='dashboard.add_transaction'),
    path('connect-stripe/', views.create_stripe_connect_link, name='dashboard.connect_stripe'),
    path('stripe-return/', views.stripe_return_view, name='dashboard.stripe_return'),
    path('stripe-refresh/', views.stripe_refresh_view, name='dashboard.stripe_refresh'),
    path('profile', views.profile, name='dashboard.profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('category/<int:category_id>/delete/', views.delete_budget_category, name='delete_budget_category'),

]