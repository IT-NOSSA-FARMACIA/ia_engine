from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from task_engine.metrics.cards import resume_executions

import re

PASSWORD_REGEX_RULES = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"


def index(request):
    time_to_search = int(request.GET.get("time", 0))
    dashboard_data = resume_executions(time_to_search, request.user)
    return render(request, "index.html", dashboard_data)


class LoginView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next_url")
        user = authenticate(username=username, password=password)
        if user and password:
            login(request, user)
        else:
            messages.error(request, "Atenção: usuário ou senha inválido.")
        if next_url:
            return redirect(next_url)
        return redirect(reverse("index"))

    def get(self, request: HttpRequest) -> HttpResponse:
        next_url = request.GET.get("next", "")
        return render(request, "login.html", {"next_url": next_url})


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect(reverse("login"))


class ChangePasswordView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "change-password.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        password = request.POST.get("password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")
        if authenticate(username=request.user.username, password=password):
            if new_password == confirm_new_password:
                if new_password != password:
                    password_regex_rules = re.compile(PASSWORD_REGEX_RULES)
                    if re.fullmatch(password_regex_rules, new_password):
                        user = User.objects.get(username=request.user.username)
                        user.set_password(new_password)
                        user.save()
                        login(request, user)
                        messages.success(request, "Senha alterada com sucesso")
                    else:
                        messages.error(
                            request,
                            "A nova senha deve conter números e letras, maiúculas e minúsculas, e ter no minímo 8 caracteres",
                        )
                else:
                    messages.error(
                        request, "A nova senha deve ser diferente da senha atual"
                    )
            else:
                messages.error(
                    request, "A nova senha e a confirmação de senha devem ser iguais"
                )
        else:
            messages.error(request, "Senha inválida")
        return redirect(reverse("change-password"))
