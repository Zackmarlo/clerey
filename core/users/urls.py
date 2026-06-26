from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, UserProfileView, AdminDashboardView, UserDashboardView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('profile/', UserProfileView.as_view()),
    path('dashboard/admin/', AdminDashboardView.as_view()),
    path('dashboard/me/', UserDashboardView.as_view()),
]