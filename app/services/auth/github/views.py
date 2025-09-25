import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from inertia import location

User = get_user_model()


def _validate_state(request):
    returned_state = request.GET.get("state")
    saved_state = request.session.pop("oauth_state", None)
    if not returned_state or returned_state != saved_state:
        return HttpResponse("Invalid OAuth state", status=400)
    return returned_state


def _read_code(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Ошибка: не передан code", status=400)
    return code


def _pop_oauth_flow(request, state):
    flows = request.session.get("oauth_flows", {})
    flow = flows.pop(state, {})
    request.session["oauth_flows"] = flows
    return flow


def _resolve_next_url(request, candidate):
    if candidate and url_has_allowed_host_and_scheme(
        url=candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return reverse("auth_draft")


def _apply_github_profile_if_requested(request, flow):
    if not flow.get("apply"):
        return
    suggested = request.session.get("github_profile_suggested")
    if not (suggested and request.user.is_authenticated):
        return
    first_name = (suggested.get("first_name") or "").strip()
    last_name = (suggested.get("last_name") or "").strip()
    updates = {}
    if first_name and request.user.first_name != first_name:
        updates["first_name"] = first_name
    if last_name and request.user.last_name != last_name:
        updates["last_name"] = last_name
    if updates:
        for k, v in updates.items():
            setattr(request.user, k, v)
        request.user.save(update_fields=list(updates.keys()))
    request.session.pop("github_profile_suggested", None)


def start_auth(request):
    """
    Генерирует state, сохраняет его в сессии и
    перенаправляет пользователя на страницу авторизации Github.
    + Запоминаем, откуда стартовали (next), и поддерживаем Inertia-визит.
    """

    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    # откуда вернуться
    candidate_next = request.GET.get("next") or request.META.get("HTTP_REFERER")
    is_valid_next = bool(
        candidate_next
        and url_has_allowed_host_and_scheme(
            url=candidate_next,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
    )
    next_url = candidate_next if is_valid_next else None

    # привязка next к state для нескольких вкладок
    flows = request.session.get("oauth_flows", {})
    apply_flag = (request.GET.get("apply") or "").lower() in ("1", "true", "yes")
    flows[state] = {"next": next_url, "apply": apply_flag}
    request.session["oauth_flows"] = flows

    # адрес авторизации
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
        "state": state,
    }
    url = "https://github.com/login/oauth/authorize?" + urlencode(params)

    # если вход со страницы с Inertia - 409 + X-Inertia-Location
    if request.headers.get("X-Inertia"):
        return location(url)

    return redirect(url)


def auth_callback(request):
    """
    Обрабатывает callback от Github:
    валидирует state, вызывает GithubBackend через authenticate и логинит.
    + Возвращаемся на сохранённый next (если валиден).
    """

    # проверка state
    result = _validate_state(request)
    if isinstance(result, HttpResponse):
        return result
    returned_state = result

    # чтение code
    result = _read_code(request)
    if isinstance(result, HttpResponse):
        return result
    code = result

    # ауф через свой backend
    user = authenticate(request, code=code)
    if user is None:
        return HttpResponse("Authentication failed", status=400)

    # непосредственно логин
    login(request, user)

    # достаем сохранённый next и флаги именно для этого state
    flow = _pop_oauth_flow(request, returned_state)
    next_url = _resolve_next_url(request, flow.get("next"))
    _apply_github_profile_if_requested(request, flow)
    return redirect(next_url)
