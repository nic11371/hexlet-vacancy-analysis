import datetime

from asgiref.sync import sync_to_async
import uuid
from app.services.hh.hh_parser.models import Vacancy, Platform, Company, City


class SaveDataVacancy:
    @sync_to_async
    def save_vacancy(self, parsed, date):

        platform_vacancy_id =  f'{Platform.TELEGRAM}{uuid.uuid4()}'
        city, company = None, None

        platform, created = Platform.objects.get_or_create(name=Platform.TELEGRAM)
        if parsed['company']:
            company, created = Company.objects.get_or_create(name=parsed['company'])
        if parsed['city']:
            city, created = City.objects.get_or_create(name=parsed['city'])

        Vacancy.objects.update_or_create(
            platform_vacancy_id=platform_vacancy_id,
            defaults={
                'platform': platform,
                'city': city,
                'company': company,
                'platform_vacancy_id': platform_vacancy_id,
                'title': parsed['title'],
                'salary': parsed['salary'],
                'url': parsed['link'],
                'experience': parsed['experience'],
                'schedule': parsed['schedule'],
                'work_format': parsed['work_format'],
                'skills': parsed['skills'],
                'description': parsed['description'],
                'address': parsed['address'],
                'contacts': parsed['phone'],
                'published_at': datetime.datetime.now(),
            }
        )
        print("Запись в модель")
