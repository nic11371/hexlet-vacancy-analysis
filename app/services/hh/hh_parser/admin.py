from django.contrib import admin

from .models import Vacancy


def custom_title_filter_factory(filter_cls, title):
    class Wrapper(filter_cls):
        def __new__(cls, *args, **kwargs):
            instance = filter_cls(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company__name',
        'city',
        'salary',
        'experience',
        'platform__name',
        'published_at',
    )
    search_fields = ('title', 'company__name', 'city__name', 'platform__name', 'skills')
    list_filter = (
        ('platform', custom_title_filter_factory(admin.RelatedFieldListFilter, 'Platform')),
        'city', 'experience', 'schedule', 'employment'
    )
    ordering = ('-published_at',)
    readonly_fields = ('created_at', 'platform')

    fieldsets = (
        ('Description', {
            'fields': (
                'platform', 'title', 'company', 'url', 'salary', 'experience',
                'employment', 'work_format', 'schedule', 'skills', 'description',
            )
        }),
        ('Location', {
            'fields': ('city',),
            'classes': ('collapse',)
        }),
        ('Additional information', {
            'fields': ('contacts', 'published_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )

