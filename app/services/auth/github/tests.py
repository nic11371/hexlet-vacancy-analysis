from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import resolve, reverse

from app.services.auth.github import views
from app.services.auth.users import exceptions as custom_ex

User = get_user_model()


class GithubURLTests(TestCase):
    """
    проверяем, что маршруты и имена URL-ов корректны.
    """

    def test_urls_resolve(self):
        self.assertEqual(resolve("/auth/github/").func, views.draft_login)
        self.assertEqual(resolve("/auth/github/start/").func, views.start_auth)
        self.assertEqual(resolve("/auth/github/callback/").func, views.auth_callback)
        # новые адаптеры форм
        self.assertEqual(
            resolve("/auth/github/email/register/").func.__name__, "email_register"
        )
        self.assertEqual(
            resolve("/auth/github/email/login/").func.__name__, "email_login"
        )

    def test_reverse_names(self):
        self.assertEqual(reverse("github_login"), "/auth/github/")
        self.assertEqual(reverse("github_auth"), "/auth/github/start/")
        self.assertEqual(reverse("github_callback"), "/auth/github/callback/")
        self.assertEqual(
            reverse("github_email_register"), "/auth/github/email/register/"
        )
        self.assertEqual(reverse("github_email_login"), "/auth/github/email/login/")


class GithubViewsTests(TestCase):
    """
    проверки draft-страницы, старта OAuth, callback-а.
    """

    def setUp(self):
        self.client = Client()

    # ----- draft_login ------------------------------------------------------

    def test_draft_login_shows_link(self):
        resp = self.client.get(reverse("github_login"))
        self.assertContains(resp, "Войти через GitHub")

    # ----- start_auth -------------------------------------------------------

    def test_start_auth_redirects(self):
        resp = self.client.get(reverse("github_auth"))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp["Location"].startswith("https://github.com/login/oauth/authorize"),
            resp["Location"],
        )
        # state должен появиться в сессии
        self.assertIn("oauth_state", self.client.session)

    # ----- auth_callback: невалидный state ----------------------------------

    def test_auth_callback_invalid_state(self):
        url = reverse("github_callback") + "?state=wrong&code=any"
        resp = self.client.get(url)
        self.assertContains(resp, "Invalid OAuth state", status_code=400)

    # ----- auth_callback: backend вернул None -------------------------------

    def test_auth_callback_authentication_failed(self):
        """
        если GithubBackend ничего не вернул, получаем 400.
        """
        # сначала запрашиваем старт, чтобы появился правильный state
        _ = self.client.get(reverse("github_auth"))
        state = self.client.session["oauth_state"]

        with patch("app.services.auth.github.views.authenticate", return_value=None):
            resp = self.client.get(
                reverse("github_callback") + f"?state={state}&code=badcode"
            )
        self.assertContains(resp, "Authentication failed", status_code=400)

    # ----- auth_callback: успешный OAuth-flow -------------------------------

    @patch("app.services.auth.github.backend.requests.get")
    @patch("app.services.auth.github.backend.requests.post")
    def test_full_oauth_flow(self, mock_post, mock_get):
        """
        проверяем happy-path: обмен code -> token, получение профиля,
        сохранение пользователя, логин и редирект.
        """
        # мокаем запрос code  ->  token
        mock_post.return_value = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"access_token": "gh_token"},
        )

        # мокаем запрос профиля
        def _mock_get(url, *args, **kwargs):
            if url.endswith("/user"):
                return SimpleNamespace(
                    raise_for_status=lambda: None,
                    json=lambda: {"login": "octocat", "name": "Octo Cat", "email": None},
                )
            elif url.endswith("/user/emails"):
                return SimpleNamespace(
                    raise_for_status=lambda: None,
                    json=lambda: [
                        {"email": "octo@example.com", "verified": True, "primary": True}
                    ],
                )
            raise AssertionError("Unexpected URL " + url)

        mock_get.side_effect = _mock_get

        # генерируем state (start_auth) — чтобы прошла проверка
        resp_start = self.client.get(reverse("github_auth"))
        self.assertEqual(resp_start.status_code, 302)
        state = self.client.session["oauth_state"]

        # вызываем callback с правильным state & любым code
        resp_cb = self.client.get(
            reverse("github_callback") + f"?state={state}&code=abc"
        )
        self.assertRedirects(resp_cb, reverse("github_login"))

        # убеждаемся, что пользователь создан и данные записаны
        user = User.objects.get(email="octo@example.com")
        self.assertEqual((user.first_name, user.last_name), ("Octo", "Cat"))

    # ----- регистрация -----------------------------------

    def test_email_register_get_not_allowed(self):
        resp = self.client.get(reverse("github_email_register"))
        self.assertEqual(resp.status_code, 405)  # require_POST

    @patch("app.services.auth.github.views.register_user")
    def test_email_register_success(self, mock_register):
        mock_register.return_value = 42  # user id
        resp = self.client.post(
            reverse("github_email_register"),
            data={
                "email": "user@example.com",
                "password": "Password2025",
                "passwordAgain": "Password2025",
                "acceptTerms": "on",
            },
        )
        self.assertRedirects(resp, reverse("github_login"))

    @patch("app.services.auth.github.views.register_user")
    def test_email_register_validation_error(self, mock_register):
        mock_register.side_effect = custom_ex.ValidationError("bad input")
        resp = self.client.post(
            reverse("github_email_register"),
            data={
                "email": "bad",
                "password": "123",
                "passwordAgain": "456",
                "acceptTerms": "on",
            },
        )
        self.assertRedirects(resp, reverse("github_login"))

    # ----- вход ------------------------------------------

    def test_email_login_get_not_allowed(self):
        resp = self.client.get(reverse("github_email_login"))
        self.assertEqual(resp.status_code, 405)

    def test_email_login_success(self):
        user = User.objects.create_user(
            email="user@example.com", password="Password2025"
        )
        self.assertTrue(user.is_active)

        resp = self.client.post(
            reverse("github_email_login"),
            data={"email": "user@example.com", "password": "Password2025"},
        )
        self.assertRedirects(resp, reverse("github_login"))
        # после логина сессия содержит _auth_user_id
        self.assertEqual(int(self.client.session.get("_auth_user_id")), user.pk)

    def test_email_login_invalid_credentials(self):
        User.objects.create_user(email="user@example.com", password="Password2025")
        resp = self.client.post(
            reverse("github_email_login"),
            data={"email": "user@example.com", "password": "wrong"},
        )
        self.assertRedirects(resp, reverse("github_login"))
        self.assertIsNone(self.client.session.get("_auth_user_id"))
