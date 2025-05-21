from django.shortcuts import render
from django.views.generic import DetailView
from django_filters.views import FilterView
from .filters import MessageFilter
from .models import Vacancy

# Create your views here.


class ViewMessage(DetailView):
    pass


class ListMessage():
    pass
