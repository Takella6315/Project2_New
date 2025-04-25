from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='dashboard.index'),
    path('adjust-budget/', views.adjust_budget, name='dashboard.adjust_budget'),
    path('add-budget-category/', views.add_budget_category, name='dashboard.add_budget_category'),
    path('profile', views.profile, name='dashboard.profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
]