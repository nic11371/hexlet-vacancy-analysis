from types import SimpleNamespace
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import resolve, reverse

from app.services.auth.yandex_id import views


class YandexIDURLTests(TestCase):
    def test_urls_resolve(self):
        self.assertEqual(resolve("/auth/yandex/").func, views.draft_login)
        self.assertEqual(resolve("/auth/yandex/start/").func, views.start_auth)
        self.assertEqual(resolve("/auth/yandex/callback/").func, views.auth_callback)

    def test_reverse_names(self):
        self.assertEqual(reverse("yandex_login"), "/auth/yandex/")
        self.assertEqual(reverse("yandex_auth"), "/auth/yandex/start/")
        self.assertEqual(reverse("yandex_callback"), "/auth/yandex/callback/")


class YandexIDViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_draft_login_shows_link(self):
        resp = self.client.get(reverse("yandex_login"))
        self.assertContains(resp, "Войти через Yandex ID")

    def test_start_auth_redirects(self):
        resp = self.client.get(reverse("yandex_auth"))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].startswith("https://oauth.yandex.ru/authorize"))

    def test_auth_callback_invalid_state(self):
        url = reverse("yandex_callback") + "?state=wrong&code=any"
        resp = self.client.get(url)
        self.assertContains(resp, "Invalid OAuth state", status_code=400)

    @patch("app.services.auth.yandex_id.views.requests.get")
    @patch("app.services.auth.yandex_id.views.requests.post")
    def test_full_oauth_flow(self, mock_post, mock_get):
        # Мокаем обмен code->token
        mock_post.return_value = SimpleNamespace(
            raise_for_status=lambda: None, json=lambda: {"access_token": "token"}
        )
        # Мокаем запрос user info
        mock_get.return_value = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {
                "default_email": "test@yandex.com",
                "first_name": "Ivan",
                "last_name": "Ivanov",
            },
        )
        # Запускаем flow: старт и callback
        resp1 = self.client.get(reverse("yandex_auth"))
        self.assertEqual(resp1.status_code, 302)
        state = self.client.session["oauth_state"]

        resp2 = self.client.get(reverse("yandex_callback") + f"?state={state}&code=abc")
        # После успешного callback — редирект обратно на draft
        self.assertRedirects(resp2, reverse("yandex_login"))

        # Проверяем, что пользователь создался
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(email="test@yandex.com")
        self.assertEqual(user.first_name, "Ivan")
        self.assertEqual(user.last_name, "Ivanov")
