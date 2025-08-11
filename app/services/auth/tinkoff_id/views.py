import base64
import logging
import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View

logger = logging.getLogger(__name__)
User = get_user_model()


class TinkoffLogin(View):
    def get(self, request):
        state = secrets.token_urlsafe(32)
        request.session["state"] = state

        params = {
            "client_id": settings.TINKOFF_ID_CLIENT_ID,
            "redirect_uri": settings.TINKOFF_ID_REDIRECT_URI,
            "state": state,
            "response_type": "code",
            "scope": ",".join(settings.TINKOFF_ID_SCOPE),
        }
        auth_url = f"{settings.TINKOFF_ID_AUTH_URL}?{urlencode(params)}"
        return redirect(auth_url)


class TinkoffCallback(View):
    def _create_basic_auth_header(self):
        credentials = (
            base64.encodebytes(
                (
                    "%s:%s"
                    % (
                        settings.TINKOFF_ID_CLIENT_ID,
                        settings.TINKOFF_ID_CLIENT_SECRET,
                    )
                ).encode("utf8")
            )
            .decode("utf8")
            .replace("\n", "")
        )
        return f"Basic {credentials}"

    def _make_oauth_request(self, url, data, auth_type="Basic", token=None):
        headers = {
            "content_type": "application/x-www-form-urlencoded",
            "Authorization": (
                f"{auth_type} {token}"
                if token
                else self._create_basic_auth_header()
            ),
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            logger.error(f"Request failed to {url}: {response.status_code}")
            return None
        return response.json()

    def get(self, request):
        state = request.GET.get("state")
        if state != request.session.pop("state"):
            message = "Invalid state parameter"
            logger.error(message)
            return HttpResponse(message, status=403)

        code = request.GET.get("code")
        if not code:
            message = "Missing code parameter"
            logger.error(message)
            return HttpResponse(message, status=403)

        token_data = {
            "grant_type": "authorization_code",
            "redirect_uri": settings.TINKOFF_ID_REDIRECT_URI,
            "code": code,
        }
        token_response = self._make_oauth_request(
            settings.TINKOFF_ID_TOKEN_URL, data=token_data
        )
        if not token_response:
            return HttpResponse("Failed to get access token", status=403)

        acssess_token = token_response.get("access_token")

        introspect_data = {
            "token": acssess_token,
        }
        introspect_response = self._make_oauth_request(
            settings.TINKOFF_ID_INTROSPECT_URL,
            data=introspect_data,
        )
        if not introspect_response:
            return HttpResponse("Failed to get introspect token", status=403)

        granded_scope = set(introspect_response.get("scope", ""))
        required_scope = set(settings.TINKOFF_ID_SCOPE)
        if not required_scope.issubset(granded_scope):
            message = "Missing scope"
            logger.error(message)
            return HttpResponse(message, status=403)

        user_data = {
            "client_id": settings.TINKOFF_ID_CLIENT_ID,
            "client_secret": settings.TINKOFF_ID_CLIENT_SECRET,
        }
        user_info = self._make_oauth_request(
            settings.TINKOFF_ID_USERINFO_URL,
            data=user_data,
            auth_type="Bearer",
            token=acssess_token,
        )
        if not user_info:
            return HttpResponse("Failed to get user info", status=403)

        email = user_info.get("email")
        if not email:
            message = "User has no email"
            logger.error(message)
            return HttpResponse(message, status=403)

        user, created = User.objects.get_or_create(email=email)
        if created:
            logger.info(f"Create new user account for: [{email}]")
        else:
            logger.info(f"User account already exists for: [{email}]")

        login(
            request, user, backend="django.contrib.auth.backends.ModelBackend"
        )
        return redirect("/")
