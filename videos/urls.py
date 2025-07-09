from django.urls import path
from .views import (
    ver_video,
    formulario_demo,
    generar_plan,
    procesar_plan,
    cargando
)

urlpatterns = [
    path('', ver_video, name='ver_video'),  # Página principal con el vídeo demo
    path('formulario/', formulario_demo, name='formulario'),  # Formulario bonito
    path('generar-plan/', generar_plan, name='generar_plan'),  # Paso intermedio
    path('procesar-plan/', procesar_plan, name='procesar_plan'),  # Generar plan IA
    path('cargando/', cargando, name='cargando'),

]
