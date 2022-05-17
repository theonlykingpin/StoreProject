from django.contrib import admin
from tags.models import Tag, TaggedItem


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['label']


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    pass
