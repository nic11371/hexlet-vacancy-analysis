import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpResponse
from django.shortcuts import redirect, render

User = get_user_model()


def draft_login(request):
    """
    Рендерит страницу с кнопкой входа через Yandex ID и показывает данные пользователя,
    если он залогинен.
    """
    context = {}
    if request.user.is_authenticated:
        context["yandex_user"] = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }
    return render(request, "yandex_id/draft_yandex_auth.html", context)


def start_auth(request):
    """
    Генерирует state, сохраняет его в сессии и
    перенаправляет пользователя на страницу авторизации Яндекс.
    """
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI,
        "state": state,
        "scope": "login:email login:info",
    }
    url = "https://oauth.yandex.ru/authorize?" + urlencode(params)
    return redirect(url)


def auth_callback(request):
    """
    Обрабатывает callback от Яндекса: проверяет state, обменивает code на токен,
    запрашивает информацию о пользователе, сохраняет его в БД и логинит.
    """
    # Шаг 1: проверка state и получение кода
    code_or_response = _validate_state_and_get_code(request)
    if isinstance(code_or_response, HttpResponse):
        return code_or_response
    code = code_or_response

    # Шаг 2: обмен code на access_token
    token_or_response = _exchange_token_for_access_token(code)
    if isinstance(token_or_response, HttpResponse):
        return token_or_response
    access_token = token_or_response

    # Шаг 3: запрос инфы о пользователе
    info_or_response = _fetch_user_info(access_token)
    if isinstance(info_or_response, HttpResponse):
        return info_or_response
    info = info_or_response

    # Шаг 4: создание или обновление пользователя
    user_or_response = _get_or_create_user(info)
    if isinstance(user_or_response, HttpResponse):
        return user_or_response
    user = user_or_response

    # Шаг 5: логиним пользователя
    login(request, user)
    return redirect("yandex_login")


def _validate_state_and_get_code(request):
    returned_state = request.GET.get("state")
    saved_state = request.session.pop("oauth_state", None)
    if not returned_state or returned_state != saved_state:
        return HttpResponse("Invalid OAuth state", status=400)
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Ошибка: не передан code", status=400)
    return code


def _exchange_token_for_access_token(code):
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.YANDEX_CLIENT_ID,
        "client_secret": settings.YANDEX_CLIENT_SECRET,
    }
    try:
        response = requests.post("https://oauth.yandex.ru/token", data=token_data)
        response.raise_for_status()
    except requests.RequestException as e:
        return HttpResponse(f"Error obtaining token: {e}", status=400)

    token_json = response.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return HttpResponse("Не удалось получить access_token", status=400)
    return access_token


def _fetch_user_info(access_token):
    try:
        response = requests.get(
            "https://login.yandex.ru/info",
            params={"format": "json"},
            headers={"Authorization": f"OAuth {access_token}"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return HttpResponse(f"Error fetching user info: {e}", status=400)
    return response.json()


def _get_or_create_user(info):
    email = info.get("default_email")
    if not email:
        return HttpResponse("Не удалось получить email из Yandex", status=400)
    defaults = {
        "first_name": info.get("first_name", ""),
        "last_name": info.get("last_name", ""),
    }
    user, created = User.objects.get_or_create(email=email, defaults=defaults)
    if not created:
        updated = False
        if user.first_name != defaults["first_name"]:
            user.first_name = defaults["first_name"]
            updated = True
        if user.last_name != defaults["last_name"]:
            user.last_name = defaults["last_name"]
            updated = True
        if updated:
            user.save()
    return user
