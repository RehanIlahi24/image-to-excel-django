from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path,include
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path("login/", views.login, name="login-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", views.logout, name="logout-user"),
    path("change-password/", views.change_password, name="change-password-user"),
]
