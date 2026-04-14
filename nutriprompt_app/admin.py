from django.contrib import admin
from .models import IAGeneratedResponse

@admin.register(IAGeneratedResponse)
class IAGeneratedResponseAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'usuario', 'fecha_creacion', 'resumen_entrada')
    list_filter = ('servicio', 'fecha_creacion')
    search_fields = ('servicio', 'usuario', 'entrada_usuario', 'resultado_ia')
    ordering = ('-fecha_creacion',)

    def resumen_entrada(self, obj):
        return obj.entrada_usuario[:50] + '...' if len(obj.entrada_usuario) > 50 else obj.entrada_usuario

    resumen_entrada.short_description = "Entrada usuario"

