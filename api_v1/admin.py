from django.contrib import admin
from api_v1.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'price')
