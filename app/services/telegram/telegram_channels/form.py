from django.forms import ModelForm
from .models import Channel


class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        fields = ['channel_id', 'username']