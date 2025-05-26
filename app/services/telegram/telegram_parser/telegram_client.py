import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from .models import TelegramPost
from dotenv import load_dotenv
from asgiref.sync import sync_to_async

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

    async def fetch_posts(self, channel_username, limit=10):
        async with self.client as client:
            channel = await client.get_entity(channel_username)
            history = await client(GetHistoryRequest(
                peer=channel,
                limit=limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            for message in history.messages:
                await self.save_post(
                    channel_username,
                    message.message,
                    message.date
                )

    @sync_to_async
    def save_post(self, channel_username, text, date):
        TelegramPost.objects.get_or_create(
            channel_username=channel_username,
            defaults={
                'text': text,
                'date': date
            }
        )