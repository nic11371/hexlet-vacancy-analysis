import os
import asyncio
import re
from telethon.sync import TelegramClient
from telethon import events
from .models import TelegramPost, KeyWord, Vacancy
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand


load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = os.getenv('TELEGRAM_SESSION')


class TelegramParser:
    def __init__(self, api_id=API_ID, api_hash=API_HASH, session_name=SESSION_NAME):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, system_version="4.10.5 beta x64")


    async def fetch_posts(self, channel_username, limit=1):
        async with self.client as client:
            channel = await client.get_entity(channel_username)
            print(f"Парсим канал: {channel_username}, limit={limit}")
            count = 0
            async for message in client.iter_messages(channel, limit=limit):
                print(f"Сообщение: {message.id}, текст: {message.message}")
                count += 1
                await self.save_post(
                    message.id,
                    channel_username,
                    message.message,
                    message.date
                )
        print(f"Загружено сообщений: {count}")



    # async def run_listener(self, channel_username):
    #     @self.client.on(events.NewMessage(chats=channel_username))
    #     async def new_post_handler(event):
    #         await self.fetch_posts(channel_username, limits=1)
    #
    #     await self.client.start()
    #     await self.client.run_until_disconnected()

    @sync_to_async
    def save_post(self, message_id, channel_username, text, date):
        TelegramPost.objects.get_or_create(
            message_id=message_id,
            channel_username=channel_username,
            defaults={
                'text': text,
                'date': date
            }
        )

    def parse_vacancy_from_text(self, text):
        lines = text.strip().splitlines()

        data = {
            'name': None,
            'company': None,
            'city': None,
            'salary': None,
            'link': None,
            'phone': None
        }
        print('Начало парсинга')


        data['name'] = lines[0].strip()

        for line in lines:
            if 'Компания' in line:
                data['company'] = line.split('Компания:')[-1].strip()

            elif 'ЗП' in line or 'Зарплата' in line:
                data['salary'] = line.split(':')[-1].strip()

            elif 'Формат' in line:
                data['city'] = line.split('Формат:')[-1].strip()

            elif 'Связаться с HR' in line:
                match = re.search(r'@[\w\d_]+', line)
                if match:
                    data['phone'] = match.group()

        print('Конец парсинга')
            # Минимальная проверка на валидность

        return data


    @sync_to_async
    def save_vacancy(self, parsed, date):
        Vacancy.objects.get_or_create(
            name=parsed['name'],
            company=parsed['company'],
            defaults={
                'city': parsed['city'],
                'salary': parsed['salary'],
                'date': date,
                'link': parsed['link'],
                'phone': parsed['phone'],
            }
        )
        print("Запись в модель")

    async def run_listener(self, channel_username):
        @self.client.on(events.NewMessage(chats=channel_username))
        async def new_post_handler(event):
            message = event.message.message
            parsed = self.parse_vacancy_from_text(message)
            if parsed:
                await self.save_vacancy(parsed, event.message.date)
                print("Сохранено в БД")

        await self.client.start()
        await self.client.run_until_disconnected()
