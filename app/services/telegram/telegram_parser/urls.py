from .views import ParseChannelView, ParseVacancyView
from django.urls import path

urlpatterns = [
    path('', ParseChannelView.as_view(), name="Messages"),
    path('vacancy/', ParseVacancyView.as_view(), name="Vacancy"),
]
