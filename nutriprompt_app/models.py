from django.db import models


class IAGeneratedResponse(models.Model):
    SOURCE_CHOICES = [
        ("fallback", "Fallback estructurado"),
        ("openai", "IA · OpenAI"),
        ("gemini", "IA · Gemini"),
        ("mock", "Modo demo"),
        ("manual", "Manual"),
    ]

    servicio = models.CharField(
        max_length=100,
        default="NutriPrompt",
        verbose_name="Servicio",
    )

    usuario = models.CharField(
        max_length=100,
        default="Bea",
        verbose_name="Usuario",
    )

    paciente = models.CharField(
        max_length=100,
        verbose_name="Paciente / cliente",
    )

    entrada_usuario = models.TextField(
        verbose_name="Entrada del usuario",
        help_text="Datos estructurados introducidos en el formulario.",
    )

    resultado_ia = models.TextField(
        verbose_name="Resultado generado",
        help_text="Respuesta generada en formato JSON serializado.",
    )

    source_type = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default="fallback",
        db_index=True,
        verbose_name="Fuente de generación",
    )

    html_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Archivo HTML",
    )

    pdf_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Archivo PDF",
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Fecha de creación",
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Respuesta generada por IA"
        verbose_name_plural = "Respuestas generadas por IA"
        indexes = [
            models.Index(fields=["servicio", "fecha_creacion"]),
            models.Index(fields=["paciente", "fecha_creacion"]),
            models.Index(fields=["source_type", "fecha_creacion"]),
        ]

    def __str__(self) -> str:
        return f"{self.paciente} · {self.servicio} · {self.fecha_creacion:%d/%m/%Y %H:%M}"

    @property
    def has_html(self) -> bool:
        return bool(self.html_file)

    @property
    def has_pdf(self) -> bool:
        return bool(self.pdf_file)

    @property
    def has_files(self) -> bool:
        return self.has_html or self.has_pdf