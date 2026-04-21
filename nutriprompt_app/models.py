from django.db import models


class IAGeneratedResponse(models.Model):
    servicio = models.CharField(max_length=100, verbose_name="Servicio")
    usuario = models.CharField(
        max_length=100,
        default="anónimo",
        verbose_name="Nombre de usuario"
    )

    # 🔥 NUEVO → clave para tu proyecto
    paciente = models.CharField(
        max_length=100,
        verbose_name="Paciente"
    )

    entrada_usuario = models.TextField(verbose_name="Entrada del usuario")
    resultado_ia = models.TextField(verbose_name="Respuesta generada por IA")

    # 🔥 NUEVO → para enlazar con los archivos generados
    html_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Archivo HTML"
    )
    pdf_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Archivo PDF"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Respuesta generada por IA"
        verbose_name_plural = "Respuestas generadas por IA"

    def __str__(self):
        return f"{self.paciente} · {self.servicio} · {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"