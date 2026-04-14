from django.db import models

class DemoVideo(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    archivo = models.FileField(upload_to='videos_demo/', verbose_name="Archivo de vídeo")
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")

    class Meta:
        ordering = ['-creado']
        verbose_name = "Demo de vídeo"
        verbose_name_plural = "Demos de vídeo"

    def __str__(self):
        return self.titulo

    @property
    def nombre_archivo(self):
        return self.archivo.name.split('/')[-1]

