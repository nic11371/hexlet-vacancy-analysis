import asyncio
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from app.services.telegram.telegram_channels.models import Channel
from app.services.telegram.telegram_parser.views import TelegramParserView

load_dotenv()


class Command(BaseCommand):
    help = 'Запускает Telegram слушатель'

    def handle(self, *args, **kwargs):
        asyncio.run(self.start_listener())

    async def start_listener(self):
        parser = TelegramParserView()
        await parser.initialize()  # Инициализация клиента
        print("слушатель телеграм работает!")
        channels = await sync_to_async(
            lambda: list(
                Channel.objects.filter(status='active').values_list(
                    'username', flat=True)))()
        tasks = [parser.channel_listener(channel) for channel in channels]
        await asyncio.gather(*tasks)
        print("слушатель телеграм не работает")
