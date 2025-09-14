from django.http import JsonResponse
from django.shortcuts import render
from django.views import View


class ProfileEditView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required"},
                status=401,
            )

        user = request.user
        props = {
            "id": user.id,
            "email": getattr(user, "email", None),
            "created_at": getattr(user, "created_at", None).isoformat()
            if getattr(user, "created_at", None)
            else None,
        }

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
            {"component": "ProfileEdit", "props": props},
        )
