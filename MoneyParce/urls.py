"""
URL configuration for MoneyParce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.LandingPage, name='LandingPage')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='LandingPage')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from dashboard import views
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('LandingPage.urls')),
    path('dashboard/', include('dashboard.urls')),
    # path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'MoneyParce/static'))
