from django.urls import path
from .views import profession_page


urlpatterns = [
    path("<slug:profession_slug>/", ProfessionView, name='profession_page')
]