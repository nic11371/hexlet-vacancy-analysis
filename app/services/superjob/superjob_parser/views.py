import os

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from dotenv import load_dotenv

from ...hh.hh_parser.models import Platform, Vacancy, City, Company
from datetime import datetime

load_dotenv()
SECRET_KEY = os.getenv('SJ_KEY')


def superjob_list(request):
    #SuperJob.objects.all().delete()
    keyword = 'Python'
    town = 'Moscow'
    count = 4

    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {"X-Api-App-Id": SECRET_KEY}
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

                company, city = None, None

                platform, created = Platform.objects.get_or_create(name=Platform.SUPER_JOB)
                if company_name:
                    company, created = Company.objects.get_or_create(name=company_name)

                city_name = item.get('town').get('title')
                if city_name:
                    city, created = City.objects.get_or_create(name=city_name)

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


                Vacancy.objects.update_or_create(
                    platform_vacancy_id=f'{Platform.SUPER_JOB}{item.get('id')}',
                    defaults={
                        'platform': platform,
                        'city': city,
                        'company': company,
                        'platform_vacancy_id': f'{Platform.SUPER_JOB}{item.get('id')}',
                        'title': item.get('profession', ''),
                        'url': item.get('link', ''),
                        'salary': salary,
                        'experience': experience.get('title', ''),
                        'schedule': type_of_work.get('title', ''),
                        'employment': type_of_work.get('title', ''),
                        'education': education.get('title', ''),
                        'description': description,
                        'skills': item.get('candidat'),
                        'address': item.get('address', ''),
                        'contacts': item.get('phone', ''),
                        'published_at': datetime.fromtimestamp(item.get('date_published', '')),
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
