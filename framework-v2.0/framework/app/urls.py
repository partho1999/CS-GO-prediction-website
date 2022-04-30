"""framework URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from app import views 

urlpatterns = [
   path('',views.index,name='index'),
    path('register',views.user_register,name='register'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login',views.user_login,name='login'),
    path('logout',views.user_logout,name='logout'),
    path("profile/<int:user_id>", views.user_profile, name='profile'), 
    path('update_rank', views.update_rank, name='update_rank'),
    path('download', views.download, name='download'),
    path('predictions', views.predictions, name='predictions'),
    path('dataset', views.update_dataset, name='dataset'),   
    path('test', views.test, name='test'), 
    path('dataset_notification', views.dataset_alert_notification, name='dataset_notification'),
]
