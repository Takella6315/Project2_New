from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/',views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('adjust-budget/', views.adjust_budget, name='movies.adjust_budget'),
    path('add-budget-category/', views.add_budget_category, name='movies.add_budget_category'),
    path('profile', views.profile, name='movies.profile'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
]