"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from apps.users.views import LoginView, LogoutView, RegisterView, ContactView, ActivateView
from apps.copywriting.views import FilePolicyAPI, DeleteFileView, FileFinishView
import xadmin

urlpatterns = [

    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    
    path('accounts/', include('allauth.urls')),
    path('googleoauth/',include('google_auth.urls')),
    
    path('contact/', ContactView.as_view(), name="contact"),
    path('activate/', ActivateView.as_view(), name="activate"),
    path('api/files/policy/', FilePolicyAPI.as_view(), name="api_policy"),
    path('api/files/delete/', DeleteFileView.as_view(), name='delete-complete'),
    path('api/files/finish/', FileFinishView.as_view(), name="finish"),
    path('callback_oauth',include('apps.users.urls') ,name='oauth'),

    # 个人中心
    url(r'^users/', include(('apps.users.urls', "users"), namespace="users")),
    url(r'^copywriting/', include(('apps.copywriting.urls', "copywriting"), namespace="copywriting")),
    url(r'^chat/', include(('apps.chat.urls', "chat"), namespace="chat")),
]
