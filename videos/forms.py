from django import forms

class FormularioClienteForm(forms.Form):
    # 🧍 Datos personales
    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={
            "placeholder": "Ej. Carla Rodríguez", "class": "form-control"
        })
    )
    edad = forms.IntegerField(
        label="Edad",
        min_value=0,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej. 29", "class": "form-control"
        })
    )
    peso = forms.DecimalField(
        label="Peso (kg)",
        min_value=0,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej. 68", "class": "form-control"
        })
    )
    altura = forms.DecimalField(
        label="Altura (cm)",
        min_value=0,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej. 165", "class": "form-control"
        })
    )
    presupuesto = forms.DecimalField(
        label="Presupuesto semanal (€)",
        min_value=0,
        initial=45,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej. 45", "class": "form-control"
        })
    )

    # 🏃 Ejercicio y cocina
    ejercicio = forms.CharField(
        label="Horas de ejercicio disponible",
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Ej. Lunes, miércoles y viernes de 18:00 a 19:00",
            "class": "form-control"
        })
    )
    cocina = forms.IntegerField(
        label="Tiempo para cocinar (min/día)",
        min_value=0,
        initial=30,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej. 30", "class": "form-control"
        })
    )

    # 🍽️ Restricciones
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

    # 🎯 Objetivo
    OBJETIVO_CHOICES = [
        ("perder_peso", "Perder peso"),
        ("ganar_energia", "Ganar energía"),
        ("comer_saludable", "Comer más saludable"),
    ]
    objetivo = forms.ChoiceField(
        label="Objetivo principal",
        choices=OBJETIVO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # 🗨️ Comentarios
    comentarios = forms.CharField(
        label="Comentarios adicionales",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Ej. Prefiero cenas frías, tengo digestiones pesadas, no tengo horno...",
            "class": "form-control"
        })
    )
