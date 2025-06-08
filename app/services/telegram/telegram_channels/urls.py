from django.urls import path
from .views import IndexChannelView, AddChannelView, ShowChannelView, DeleteChannelView


urlpatterns = [
    path('', IndexChannelView.as_View(), name='channels_list'),
    path('add/', AddChannelView.as_View(), name='channels_add'),
    path('show/<int:id>', AddChannelView.as_View(), name='channels_show'),
    path('delete/<int:id>', DeleteChannelView.as_View(), name='channels_delete'),
]
