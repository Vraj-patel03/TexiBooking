"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('drivers/', views.drivers_view, name='drivers'),
    path('drivers/<int:driver_id>/delete/', views.driver_delete, name='driver_delete'),
    path('drivers/<int:driver_id>/', views.driver_detail, name='driver_detail'),
    path('users/', views.users_view, name='users'),
    path('bookings/', views.bookings_view, name='bookings'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/add/', views.user_create, name='user_create'),
    
]