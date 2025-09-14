from django.http import JsonResponse
from django.shortcuts import render
from django.views import View


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
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required"},
                status=401,
            )

        user = request.user
        props = self._build_props(user)

        wants_json = request.GET.get(
            "format"
        ) == "json" or "application/json" in request.headers.get("Accept", "")

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
                "saved": request.GET.get("saved") == "1",
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
                {
                    "component": "ProfileEdit",
                    "props": props,
                    "errors": errors,
                },
                status=400,
            )

        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])

        props = self._build_props(user)
        wants_json = request.GET.get(
            "format"
        ) == "json" or "application/json" in request.headers.get("Accept", "")

        if wants_json:
            return JsonResponse(
                {
                    "status": "ok",
                    "component": "ProfileEdit",
                    "props": props,
                    "message": "Изменения сохранены",
                }
            )

        return render(
            request,
            "account/draft_account_edit.html",
            {"component": "ProfileEdit", "props": props, "saved": True},
        )
