
from django.db import models

class DemoVideo(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='videos_demo/')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
