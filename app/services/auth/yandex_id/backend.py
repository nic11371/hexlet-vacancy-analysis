import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from app.services.auth.users.models import UserIdentity

User = get_user_model()


class YandexBackend(BaseBackend):
    """
    Ауф через Яндекс:
    - Обменивает code на токен
    - Получает user info
    - Создаёт или возвращает User
    """

    def authenticate(self, request, code=None, **kwargs):
        if code is None:
            return None
        # обмен code -> token
        res = requests.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_CLIENT_ID,
                "client_secret": settings.YANDEX_CLIENT_SECRET,
            },
        )
        try:
            res.raise_for_status()
        except requests.RequestException:
            return None
        token = res.json().get("access_token")
        if not token:
            return None

        # запрос профиля
        info_res = requests.get(
            "https://login.yandex.ru/info",
            params={"format": "json"},
            headers={"Authorization": f"OAuth {token}"},
        )
        try:
            info_res.raise_for_status()
        except requests.RequestException:
            return None
        info = info_res.json()
        email = info.get("default_email")
        # устойчивый идентификатор пользователя у Яндекса
        provider_user_id = str(info.get("id") or info.get("psuid") or email or "")
        if not provider_user_id:
            return None

        # если identity уже существует — возвращаем связанного пользователя
        identity = (
            UserIdentity.objects.select_related("user")
            .filter(provider="yandex", provider_user_id=provider_user_id)
            .first()
        )
        if identity:
            user = identity.user
        else:
            link_to_user = kwargs.get("link_to_user")
            if link_to_user is not None:
                user = link_to_user
            else:
                # создать/найти пользователя по email (если есть)
                defaults = {
                    "first_name": info.get("first_name", ""),
                    "last_name": info.get("last_name", ""),
                }
                if email:
                    user, _ = User.objects.get_or_create(email=email, defaults=defaults)
                else:
                    # без email создать пользователя в нашей модели нельзя
                    return None

            # создать identity для пользователя
            UserIdentity.objects.create(
                user=user,
                provider="yandex",
                provider_user_id=provider_user_id,
                email=email,
                email_verified=bool(email),
                profile=info,
            )

        # подсказка для обновления имени/фамилии
        if request is not None:
            suggest = {
                "first_name": info.get("first_name", ""),
                "last_name": info.get("last_name", ""),
            }
            request.session["yandex_profile_suggested"] = suggest

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
