from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home y formulario
    path('plan/', views.procesar_plan_directo, name='generar_plan'),
]