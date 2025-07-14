from django import forms

class FormularioClienteForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100)
    edad = forms.IntegerField(label="Edad")
    peso = forms.DecimalField(label="Peso (kg)", min_value=0)
    altura = forms.DecimalField(label="Altura (cm)", min_value=0)
    presupuesto = forms.DecimalField(label="Presupuesto semanal (€)", min_value=0)
    ejercicio = forms.CharField(label="Horas de ejercicio disponible", required=False)
    cocina = forms.IntegerField(label="Tiempo para cocinar (min/día)", min_value=0)
    
    RESTRICCIONES_CHOICES = [
        ("sin_gluten", "Sin gluten"),
        ("sin_lactosa", "Sin lactosa"),
        ("vegetariano", "Vegetariano"),
        ("no_pescado_azul", "No pescado azul"),
        ("digestiones_pesadas", "Digestiones pesadas"),
    ]
    restricciones = forms.MultipleChoiceField(
        label="Restricciones alimentarias",
        choices=RESTRICCIONES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    OBJETIVO_CHOICES = [
        ("perder_peso", "Perder peso"),
        ("ganar_energia", "Ganar energía"),
        ("comer_saludable", "Comer más saludable"),
    ]
    objetivo = forms.ChoiceField(
        label="Objetivo principal",
        choices=OBJETIVO_CHOICES,
        widget=forms.Select
    )

    comentarios = forms.CharField(
        label="Comentarios adicionales",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
