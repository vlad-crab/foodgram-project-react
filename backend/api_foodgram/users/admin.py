from django.contrib import admin

from .models import Subscriptions


class SubscriptionsAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'

admin.site.register(Subscriptions, SubscriptionsAdmin)