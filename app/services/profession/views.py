from django.shortcuts import get_object_or_404
from inertia import render
from django.core.paginator import Paginator
from .models import Profession
from django.views import View
from django.views.decorators.csrf import csrf_exempt


class ProfessionView(View):

    def listing(self, request, *args, **kwargs):
        professions = Profession.objects.all()
        paginator = Paginator(professions, 25)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        vacancies = [
            {
                "id": v.id,
                "title": title,
                "company": v.company,
                "url": v.url,
            }
            for v in page_obj.object_list
        ]

        props = {
            "profession": {
                "id": professions.id,
                "name": professions.name,
                "slug": professions.slug
            },
            "vacancies": {
                "data": vacancies,
                }
            }

        return render(request, "ProfessionPage", props)
