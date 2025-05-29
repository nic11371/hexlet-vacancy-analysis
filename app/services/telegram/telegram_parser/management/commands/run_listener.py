import os
import asyncio
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from ... telegram_client import TelegramParser


load_dotenv()


API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = os.getenv('TELEGRAM_SESSION')


class Command(BaseCommand):
    help = 'Запускает Telegram слушатель'

    def handle(self, *args, **kwargs):
        parser = TelegramParser(api_id=API_ID, api_hash=API_HASH)
        print("слушатель телеграм работает!")
        asyncio.run(parser.run_listener('@cwa_my_test'))
        print("слушатель телеграм не работает")