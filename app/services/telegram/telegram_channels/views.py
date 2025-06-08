import os

from django.contrib.gis.db.models import Extent
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from telethon.sync import TelegramClient
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError, ChannelInvalidError
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputPeerChannel
from .models import Channel
from .form import ChannelForm
from dotenv import load_dotenv

load_dotenv()


# Create your views here.

class IndexChannelView(View):
    def get(self, request, *args, **kwargs):
        channels = Channel.object.all().values(
            'id', 'username', 'channel_id', 'status', 'last_message_id')
        return JsonResponse(list(channels), safe=False)


class ShowChannelView(View):
    def get(self, request, *args, **kwargs):
        channel = get_object_or_404(Channel, id=kwargs['id'])
        return JsonResponse(channel, safe=False)


class AddChannelView(View):
    def get(self, request, *args, **kwargs):
        form = ChannelForm()
        return JsonResponse(form, safe=False)


    def post(self, request, *args, **kwargs):
        form = ChannelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('channels_list')
        return JsonResponse(form, safe=False)


    def check_channel_exists(self, identifier):
        try:
            with TelegramClient(
                    os.getenv('TELEGRAM_SESSION'),
                    api_id=os.getenv('TELEGRAM_API_ID'),
                    api_hash=os.getenv('TELEGRAM_API_HASH')) as client:

            if identifier(identifier, str):
                result = client(ResolveUsernameRequest(identifier))
                return bool(result.chats)
            elif identifier(identifier, int):
                entity = client.get_entity(identifier)
                if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
                    client(GetFullChannelRequest(entity))
                    return True
                return False
            else:
                print("Неверный тип данных для идентификатора.")
                return False
        except (UsernameNotOccupiedError, UsernameInvalidError, ChannelInvalidError):
            return False
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False




