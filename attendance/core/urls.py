from django.urls import path
from . import views

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('api/register-face/', views.FaceRegistrationAPI.as_view(), name='register-face'),
    path('api/login-face/', views.FaceLoginAPI.as_view(), name='login-face'),
]