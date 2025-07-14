from django.urls import path
from .views import (
    bienvenida,
    ver_video,
    formulario_demo,
    procesar_plan_directo,
)

urlpatterns = [
    path('', bienvenida, name='bienvenida'),  # Página de bienvenida
    path('video/', ver_video, name='ver_video'),  # Página demo con vídeo
    path('formulario/', formulario_demo, name='formulario'),  # Formulario de entrada
    path('procesar-directo/', procesar_plan_directo, name='procesar_plan_directo'),  # Generación directa del plan
]

