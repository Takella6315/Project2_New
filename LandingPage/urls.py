from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='LandingPage.index'),
    path('about', views.about, name='LandingPage.about'),
]
