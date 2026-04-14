from django.urls import path
from .views import ver_video, formulario_demo, procesar_plan_directo

urlpatterns = [
    path('video/', ver_video, name='ver_video'),
    path('formulario/', formulario_demo, name='formulario_demo'),
    path('procesar-directo/', procesar_plan_directo, name='procesar_plan_directo'),
]


