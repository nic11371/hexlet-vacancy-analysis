from django.http import JsonResponse
from inertia import render as inertia_render
# Для себя 
from app.services.hh.hh_parser.models import Vacancy


def index(request):
    vacancies_qs = Vacancy.objects.select_related('company', 'city').all()

    vacancies = []
    for v in vacancies_qs:
        vacancy_data = {
            'id': v.id,
            'title': v.title,
            'url': v.url,
            'salary': v.salary or '',
            'experience': v.experience or '',
            'employment': v.employment or '',
            'company': {
                'id': v.company.id if v.company else None,
                'name': v.company.name if v.company else '',
            },
            'city': {
                'id': v.city.id if v.city else None,
                'name': v.city.name if v.city else '',
            } if v.city else None,
            'skills': v.skills.split(',') if v.skills else [],
        }
        vacancies.append(vacancy_data)

    return inertia_render(
        request,
        "HomePage",
        props={
            'vacancies': vacancies  # передаем массив вакансий во фронтенд
        }
    )
# Для себя 

# def index(request):
#     return inertia_render(
#         request,
#         "HomePage",
#         props={},
#     )


def custom_server_error(request):
    return JsonResponse(
        {"status": "error", "message": "Internal server error"},
        status=500
    )


def custom_not_found_error(request, exception):
    return JsonResponse(
        {"status": "error", "message": "Internal server error"},
        status=404
    )

