from django.contrib import admin
from .models import DemoVideo

@admin.register(DemoVideo)
class DemoVideoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'nombre_archivo', 'creado')
    list_filter = ('creado',)
    search_fields = ('titulo', 'descripcion')
    ordering = ('-creado',)

    def nombre_archivo(self, obj):
        return obj.archivo.name.split('/')[-1]

    nombre_archivo.short_description = "Archivo"
