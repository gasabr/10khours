"""hours URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from gauth import views
from accounts.views import (login_view, logout_view, register_view, schedule_view)
from viz.views import viz
# for managing static files
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.home, name='home'),
    
    url(r'^accounts/login/', login_view, name='login'), # why do i need accounts here?
    url(r'^register/', register_view, name='register'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^schedule/', schedule_view, name='schedule'),

    url(r'^get_creds/', views.get_creds, name='get_creds'),
    url(r'^oauth2/redirect/', views.oauth2redirect, name='oauth2redirect'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^viz/', viz, name='viz'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
