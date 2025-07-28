from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpResponse
from django.shortcuts import redirect, render

User = get_user_model()


def draft_login(request):
    return render(request, "yandex_id/draft_yandex_auth.html")


def start_auth(request):
    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI,
        "state": "secure_random_string",
        "scope": "login:email login:info",
    }
    url = "https://oauth.yandex.ru/authorize?" + urlencode(params)
    return redirect(url)


def auth_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Ошибка: не передан code", status=400)

    # Обмениваем code на токен
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.YANDEX_CLIENT_ID,
        "client_secret": settings.YANDEX_CLIENT_SECRET,
    }
    token_res = requests.post("https://oauth.yandex.ru/token", data=token_data)
    token_res.raise_for_status()
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    # Запрашиваем информацию о пользователе
    user_res = requests.get(
        "https://login.yandex.ru/info",
        params={"format": "json"},
        headers={"Authorization": f"OAuth {access_token}"},
    )
    user_res.raise_for_status()
    info = user_res.json()
    email = info.get("default_email")
    if not email:
        return HttpResponse("Не удалось получить email из Yandex", status=400)

    # Логиним или создаём своего пользователя
    user, created = User.objects.get_or_create(email=email)
    if created:
        user.set_unusable_password()
        user.save()

    login(request, user)
    return redirect("yandex_login")
