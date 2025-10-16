from django.contrib.postgres.fields import ArrayField
from django.db import models


class KeyWord(models.Model):
    title = ArrayField(models.CharField(
        max_length=255, verbose_name=('title'), blank=True, null=True
    ), default=list, blank=True, null=True)
    company = ArrayField(models.CharField(
        max_length=255, verbose_name=('company'), blank=True, null=True
    ), default=list, blank=True, null=True)
    salary = ArrayField(models.CharField(
        max_length=255, verbose_name=('salary'), blank=True, null=True
    ), default=list, blank=True, null=True)
    schedule = ArrayField(models.CharField(
        max_length=255, verbose_name=('schedule'), blank=True, null=True
    ), default=list, blank=True, null=True)
    city = ArrayField(models.CharField(
        max_length=255, verbose_name=('city'), blank=True, null=True
    ), default=list, blank=True, null=True)
    experience = ArrayField(models.CharField(
        max_length=255, verbose_name=('experience'), blank=True, null=True
    ), default=list, blank=True, null=True)
    address = ArrayField(models.CharField(
        max_length=255, verbose_name=('address'), blank=True, null=True
    ), default=list, blank=True, null=True)
    description = ArrayField(models.CharField(
        max_length=255, verbose_name=('description'), blank=True, null=True
    ), default=list, blank=True, null=True)

    def __str__(self):
        return 'Telegram keywords'
