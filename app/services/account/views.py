from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from inertia import render as inertia_render


class ProfileEditView(View):
    def _build_props(self, user):
        return {
            "id": user.id,
            "email": getattr(user, "email", None),
            "first_name": getattr(user, "first_name", None),
            "last_name": getattr(user, "last_name", None),
            "created_at": getattr(user, "created_at", None).isoformat()
            if getattr(user, "created_at", None)
            else None,
        }

    def get(self, request):
        wants_json = request.GET.get(
            "format"
        ) == "json" or "application/json" in request.headers.get("Accept", "")
        wants_inertia = bool(request.headers.get("X-Inertia"))

        # исходная ссылка для возврата после сохранения
        candidate_next = request.GET.get("next") or request.META.get("HTTP_REFERER")
        next_url = (
            candidate_next
            if (
                candidate_next
                and url_has_allowed_host_and_scheme(
                    url=candidate_next,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                )
            )
            else None
        )

        if not request.user.is_authenticated:
            if wants_json or wants_inertia:
                return JsonResponse(
                    {"status": "error", "message": "Authentication required"},
                    status=401,
                )
            return render(request, "account/draft_account_edit.html", {"next": next_url})

        user = request.user
        props = self._build_props(user)

        if wants_inertia:
            return inertia_render(request, "ProfileEdit", props)

        if wants_json:
            return JsonResponse(
                {"status": "ok", "component": "ProfileEdit", "props": props}
            )

        return render(
            request,
            "account/draft_account_edit.html",
            {
                "component": "ProfileEdit",
                "props": props,
                "next": next_url,
            },
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required"},
                status=401,
            )

        user = request.user

        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()

        errors = {}
        if len(first_name) > 150:
            errors["first_name"] = "Максимальная длина — 150 символов"
        if len(last_name) > 150:
            errors["last_name"] = "Максимальная длина — 150 символов"

        if errors:
            props = self._build_props(user)
            props.update({"first_name": first_name, "last_name": last_name})
            wants_json = request.GET.get(
                "format"
            ) == "json" or "application/json" in request.headers.get("Accept", "")
            wants_inertia = bool(request.headers.get("X-Inertia"))
            if wants_inertia:
                return inertia_render(
                    request,
                    "ProfileEdit",
                    {**props, "errors": errors},
                    status=422,
                )

            if wants_json:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Validation error",
                        "errors": errors,
                        "props": props,
                    },
                    status=400,
                )

            return render(
                request,
                "account/draft_account_edit.html",
                {"component": "ProfileEdit", "props": props, "errors": errors},
                status=400,
            )

        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])

        wants_json = request.GET.get(
            "format"
        ) == "json" or "application/json" in request.headers.get("Accept", "")
        if wants_json:
            props = self._build_props(user)
            return JsonResponse(
                {
                    "status": "ok",
                    "component": "ProfileEdit",
                    "props": props,
                    "message": "Изменения сохранены",
                }
            )

        messages.success(request, "Изменения сохранены")

        # возврат после сохранения
        candidate_next = request.POST.get("next") or request.META.get("HTTP_REFERER")
        if candidate_next and url_has_allowed_host_and_scheme(
            url=candidate_next,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            url = candidate_next
        else:
            url = reverse("account_profile_edit")

        resp = redirect(url)
        resp.status_code = 303
        return resp
