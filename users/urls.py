# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView
from . import views

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Profile management - specific paths BEFORE dynamic username path
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/user-info/', views.user_info_edit, name='user_info_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/toggle-theme/', views.toggle_theme, name='toggle_theme'),
    # Dynamic username path LAST to avoid conflicts
    path('profile/<str:username>/', views.public_profile_view, name='public_profile'),
]
