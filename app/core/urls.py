from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required
from . import views
from .views import LoginView, index, LogoutView, ChangePasswordView


urlpatterns = [
    path("", RedirectView.as_view(url="index", permanent=False)),
    path("index/", login_required(index), name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
