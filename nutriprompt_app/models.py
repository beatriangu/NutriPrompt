from __future__ import annotations

from django.db import models


class IAGeneratedResponse(models.Model):
    SOURCE_CHOICES = [
        ("fallback", "Motor nutricional estructurado"),
        ("openai", "IA · OpenAI"),
        ("gemini", "IA · Gemini"),
        ("mock", "Modo demo"),
        ("manual", "Manual"),
    ]

    servicio = models.CharField(max_length=100, default="NutriPrompt")
    usuario = models.CharField(max_length=100, default="Bea")
    paciente = models.CharField(max_length=100, verbose_name="Paciente / cliente")

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

    html_file = models.CharField(max_length=255, blank=True, null=True)
    pdf_file = models.CharField(max_length=255, blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

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


class SmartIntakeAnalysis(models.Model):
    INTAKE_TYPE_CHOICES = [
        ("nutrition_pdf", "PDF de nutricionista / pauta nutricional"),
        ("product_label", "Producto o etiqueta"),
        ("pantry_image", "Foto de despensa"),
        ("fridge_image", "Foto de nevera"),
        ("ingredient_image", "Ingrediente concreto"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("processed", "Procesado"),
        ("failed", "Fallido"),
    ]

    intake_type = models.CharField(
        max_length=40,
        choices=INTAKE_TYPE_CHOICES,
        db_index=True,
        verbose_name="Tipo de entrada",
    )

    original_file = models.FileField(
        upload_to="vision/uploads/",
        verbose_name="Archivo original",
    )

    extracted_text = models.TextField(
        blank=True,
        verbose_name="Texto extraído",
    )

    detected_items = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Elementos detectados",
    )

    detected_restrictions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Restricciones detectadas",
    )

    detected_warnings = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Alertas detectadas",
    )

    structured_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen estructurado",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name="Estado",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Fecha de creación",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Análisis Smart Intake"
        verbose_name_plural = "Análisis Smart Intake"
        indexes = [
            models.Index(fields=["intake_type", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_intake_type_display()} · {self.get_status_display()} · {self.created_at:%d/%m/%Y %H:%M}"

    @property
    def is_processed(self) -> bool:
        return self.status == "processed"

    @property
    def has_warnings(self) -> bool:
        return bool(self.detected_warnings)

    @property
    def has_detected_items(self) -> bool:
        return bool(self.detected_items)