from django.db import models

# Create your models here.


class KeyWord(models.Model):
    title = models.CharField(
        max_length=255, verbose_name=('title'), blank=True, null=True
    )
    company = models.CharField(
        max_length=255, verbose_name=('company'), blank=True, null=True
    )
    salary = models.CharField(
        max_length=255, verbose_name=('salary'), blank=True, null=True
    )
    schedule = models.CharField(
        max_length=255, verbose_name=('schedule'), blank=True, null=True
    )
    city = models.CharField(
        max_length=255, verbose_name=('city'), blank=True, null=True
    )
    experience = models.CharField(
        max_length=255, verbose_name=('experience'), blank=True, null=True
    )
    address = models.CharField(
        max_length=255, verbose_name=('address'), blank=True, null=True
    )
    description = models.CharField(
        max_length=255, verbose_name=('description'), blank=True, null=True
    )

    def __str__(self):
        return self.title
