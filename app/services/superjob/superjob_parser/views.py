import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from .models import SuperJob


def superjob_list(request):
    SuperJob.objects.all().delete()
    keyword = 'Python'
    town = 'Москва'
    count = 4

    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {"X-Api-App-Id": "v3.r.139102357.df987f5ddf958483a5de626fd908a60d38c81357.87b9bc1736bea42137acdaa4fc2a9cb579ed67c3"}
    params = {
        'keyword': keyword,
        'town': town,
        'count': count,
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        saved_count = 0
        errors = []

        for item in data['objects']:
            try:
                company = item.get('client', {})
                company_name = company.get('title', '')
                company_id = company.get('id', '')
                company_city = company.get('town', '')
                salary_from = int(item.get('payment_from', 0))
                salary_to = int(item.get('payment_to', 0))
                salary_currency = item.get('currency', '')
                salary = 'По договоренности'
                if salary_from or salary_to:
                    salary_parts = []
                    if salary_from:
                        salary_parts.append(f"от {salary_from}")
                    if salary_to:
                        salary_parts.append(f"до {salary_to}")
                    if salary_currency:
                        salary_parts.append(salary_currency)
                    salary = ' '.join(salary_parts)

                description = BeautifulSoup(
                    item.get('vacancyRichText', ''),
                    'html.parser'
                ).get_text()

                experience = item.get('experience')
                education = item.get('education')
                type_of_work = item.get('type_of_work')
                place_of_work = item.get('place_of_work')
                city = item.get('town')
                SuperJob.objects.update_or_create(
                    syperjob_id=item.get('id'),
                    defaults={
                        'title': item.get('profession', ''),
                        'url': item.get('link', ''),
                        'company_name': company_name,
                        'company_id': company_id,
                        'company_city': company_city.get('title', ''),
                        'salary': salary,
                        'experience': experience.get('title', ''),
                        'type_of_work': type_of_work.get('title', ''),
                        'place_of_work': place_of_work.get('title', ''),
                        'education': education.get('title', ''),
                        'description': description,
                        'city': city.get('title', ''),
                        'address': item.get('address', ''),
                        'contacts': item.get('phone', ''),
                        'published_at': item.get('date_published', ''),
                    }
                )

                saved_count += 1

            except Exception as e:
                errors.append(f"Вакансия не была сохранена: {str(e)}")
                continue

        return JsonResponse({
            'status': 'success',
            'saved_count': saved_count,
            'errors': errors,
            'message': f'Успешно сохранено {saved_count} вакансий'
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Ошибка при парсинге: {str(e)}'
        }, status=500)
