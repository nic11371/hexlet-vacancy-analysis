from django.shortcuts import render
from django.views.generic import DetailView
from django_filters.views import FilterView
# from .filters import MessageFilter
from .models import TelegramPost, Vacancy
from django.views import View
from django.http import JsonResponse
from .telegram_client import TelegramParser
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy
import asyncio


# Create your views here.
class ParseChannelView(View):
    async def get(self, request, *args, **kwargs):
        channel = request.GET.get('channel', 'pythonrabota')
        limit = int(request.GET.get('limit', 10))

        parser = TelegramParser()
        await parser.fetch_posts(channel_username=channel, limit=limit)
        return JsonResponse({'status': 'done'})


class ParseVacancyView(View):
    def get(self, request, *args, **kwargs):
        data = list(TelegramPost.objects.values('text', 'date'))
        return JsonResponse(data, safe=False)



