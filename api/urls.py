from django.urls import path
from .views import LoginView, LogoutView, VerifyView, GetView, PostView, PutView, DeleteView, ChangePasswordView, ListView

urlpatterns = [
    path("auth/login",  LoginView.as_view(),  name="auth_login"),
    path("auth/logout", LogoutView.as_view(), name="auth_logout"),
    path("auth/verify", VerifyView.as_view(), name="auth_verify"),
    path("auth/change-password", ChangePasswordView.as_view(), name="auth-change-password"),
    
    # PLURAL: listagem com filtros
    path("<str:model_name_plural>", ListView.as_view(), name="list"),

    # CRUD unitário
    path("<str:model_name>/add",              PostView.as_view(), name="post"),
    path("<str:model_name>/<uuid:pk>",        GetView.as_view(),  name="get"),
    path("<str:model_name>/<uuid:pk>/update", PutView.as_view(),  name="put"),
    path("<str:model_name>/<uuid:pk>/delete", DeleteView.as_view(), name="delete"),
]
