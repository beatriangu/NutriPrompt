from django.urls import path
from . import views

app_name = "nutriprompt_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("generar-plan/", views.procesar_plan_directo, name="procesar_plan_directo"),
    path("vision/", views.vision_upload, name="vision_upload"),
]