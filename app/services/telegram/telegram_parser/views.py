from django.shortcuts import render
from django.views.generic import DetailView
from django_filters.views import FilterView
# from .filters import MessageFilter
from .models import TelegramPost
from django.views import View
from django.http import JsonResponse
from .telegram_client import TelegramParser
import asyncio


# Create your views here.
class ParseChannelView(View):
    async def get(self, request, *args, **kwargs):
        channel = request.GET.get('channel', 'KiselevaBiz')
        limit = int(request.GET.get('limit', 5))

        parser = TelegramParser()
        await parser.fetch_posts(channel_username=channel, limit=limit)
        return JsonResponse({'status': 'done'})
