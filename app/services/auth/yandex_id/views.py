import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from app.services.auth.users import exceptions as custom_ex
from app.services.auth.users.logic.registration import register_user
from app.services.auth.users.logic.validators import normalize_email

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
    обрабатывает callback от Яндекса:
    валидирует state, вызывает YandexBackend через authenticate и логинит.
    """
    # проверка state и получение кода
    returned_state = request.GET.get("state")
    saved_state = request.session.pop("oauth_state", None)
    if not returned_state or returned_state != saved_state:
        return HttpResponse("Invalid OAuth state", status=400)

    code = request.GET.get("code")
    if not code:
        return HttpResponse("Ошибка: не передан code", status=400)

    # аутентификация через кастомный бэкенд
    user = authenticate(request, code=code)
    if user is None:
        return HttpResponse("Authentication failed", status=400)

    # логин и редирект обратно
    login(request, user)
    return redirect("yandex_login")


@require_POST
def email_register(request):
    """
    Вызывает register_user для html форм.
    """
    email = (request.POST.get("email") or "").strip()
    password = request.POST.get("password") or ""
    password_again = request.POST.get("passwordAgain") or ""
    accept = request.POST.get("acceptTerms") in ("on", "true", "1", True)

    data = {
        "email": email,
        "password": password,
        "passwordAgain": password_again,
        "acceptTerms": accept,
        "domain": get_current_site(request).domain,
    }

    try:
        _user_id = register_user(data)
        messages.success(request, "Регистрация прошла. Проверьте почту для активации.")
    except custom_ex.ValidationError as e:
        messages.error(request, e.message)
    except custom_ex.CreateUserError as e:
        messages.error(request, e.message)
    except custom_ex.SendEmailError as e:
        messages.error(request, e.message)
    except custom_ex.CustomBaseError as e:
        messages.error(request, e.message)

    return redirect("yandex_login")


@require_POST
def email_login(request):
    """
    Логин по почте (EmailAuthBackend).
    """
    email = normalize_email(request.POST.get("email") or "")
    password = request.POST.get("password") or ""

    if not (email and password):
        messages.error(request, "Email and password required")
        return redirect("yandex_login")

    user = authenticate(request, email=email, password=password)
    if user is None:
        messages.error(request, "Invalid credential")
        return redirect("yandex_login")

    if not getattr(user, "is_active", False):
        messages.error(request, "User in not active")
        return redirect("yandex_login")

    login(request, user)
    messages.success(request, "Вход выполнен.")
    return redirect("yandex_login")
