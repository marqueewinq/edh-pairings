from django.contrib import admin
from news.models import NewsEntry


class NewsEntryAdmin(admin.ModelAdmin):
    pass


admin.site.register(NewsEntry, NewsEntryAdmin)
