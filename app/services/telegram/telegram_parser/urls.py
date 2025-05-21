from .views import ListMessage, ViewMessage
from django.urls import path

urlpatterns = [
    path('', ListMessage.as_view(), name="Messages"),
    path('<int:pk>/', ViewMessage.as_view(), name="Message"),
]
