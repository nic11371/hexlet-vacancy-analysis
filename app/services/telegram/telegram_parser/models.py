from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class TelegramPost(models.Model):
    channel_username = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.channel_username}"
    # name = models.CharField(
    #     max_length=255, verbose_name=('vacancy_name')
    # )
    # company = models.CharField(
    #     max_length=255, verbose_name=('company')
    # )
    # city = models.CharField(
    #     max_length=255, verbose_name=('city')
    # )
    # salary = models.CharField(
    #     max_length=255, verbose_name=('salary')
    # )
    # date = models.DateTimeField(verbose_name=('date'))
    # link = models.CharField(
    #     max_length=255, verbose_name=('link')
    # )
    #
    # def __str__(self):
    #     return self.name
    #
    # class Meta:
    #     verbose_name = _("=Vacation=")
    #     verbose_name_plural = _("=Vacation=")
