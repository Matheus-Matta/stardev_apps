from django.urls import path
from .views import LoginView, LogoutView, VerifyView, GetView

urlpatterns = [
    path("auth/login",  LoginView.as_view(),  name="auth_login"),
    path("auth/logout", LogoutView.as_view(), name="auth_logout"),
    path("auth/verify", VerifyView.as_view(), name="auth_verify"),

    path("<str:model_name>/<int:pk>", GetView.as_view(), name="get")
]
