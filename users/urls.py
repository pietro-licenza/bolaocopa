from django.urls import path

from .views import CustomLoginView, CustomLogoutView, DashboardView, LandingView, RegisterView

urlpatterns = [
    path('', LandingView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]