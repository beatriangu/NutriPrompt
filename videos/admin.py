from django.contrib import admin
from .models import DemoVideo

@admin.register(DemoVideo)
class DemoVideoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creado')
