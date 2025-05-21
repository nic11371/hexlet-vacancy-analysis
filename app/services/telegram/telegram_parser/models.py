from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Vacancy(models.Model):
    name = models.CharField(
        max_length=255, verbose_name=('vacancy_name')
    )
    company = models.CharField(
        max_length=255, verbose_name=('company')
    )
    city = models.CharField(
        max_length=255, verbose_name=('city')
    )
    salary = models.CharField(
        max_length=255, verbose_name=('salary')
    )
    date = models.DateTimeField(verbose_name=('date'))
    link = models.CharField(
        max_length=255, verbose_name=('link')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("=Vacation=")
        verbose_name_plural = _("=Vacation=")
