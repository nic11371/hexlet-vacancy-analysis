from .views import ParseChannelView
from django.urls import path

urlpatterns = [
    path('', ParseChannelView.as_view(), name="Messages"),
    # path('<int:pk>/', ViewMessage.as_view(), name="Message"),
]
