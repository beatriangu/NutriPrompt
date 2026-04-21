from django import forms


GOAL_CHOICES = [
    ("energia", "Ganar energía"),
    ("peso", "Perder peso"),
    ("musculo", "Ganar masa muscular"),
    ("equilibrado", "Comer más equilibrado"),
]

DIET_CHOICES = [
    ("sin_gluten", "Sin gluten"),
    ("sin_lactosa", "Sin lactosa"),
    ("low_fodmap", "Bajo en FODMAPs"),
    ("vegetariano", "Vegetariano"),
    ("vegano", "Vegano"),
    ("pescetariano", "Pescetariano"),
]

PREFERENCE_CHOICES = [
    ("pollo", "Pollo"),
    ("pavo", "Pavo"),
    ("pescado", "Pescado"),
    ("huevos", "Huevos"),
    ("verduras", "Verduras"),
    ("rapido", "Comidas rápidas"),
    ("facil", "Fácil de preparar"),
    ("barato", "Presupuesto ajustado"),
]

MEAL_CONTEXT_CHOICES = [
    ("home", "En casa"),
    ("restaurant", "Restaurante / comer fuera"),
    ("travel", "Viaje"),
    ("work", "Rutina de trabajo"),
]

SPECIAL_SITUATION_CHOICES = [
    ("normal", "Rutina normal"),
    ("weekend", "Fin de semana"),
    ("travel", "Viaje"),
    ("event", "Evento / celebración"),
]

KITCHEN_CHOICES = [
    ("si", "Sí"),
    ("no", "No"),
    ("limitado", "Acceso limitado"),
]

YES_NO_CHOICES = [
    ("si", "Sí"),
    ("no", "No"),
]


class NutriPromptForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ej. Bea Lamiquiz",
                "class": "input-text",
                "autocomplete": "name",
            }
        ),
    )

    objetivo = forms.ChoiceField(
        label="Objetivo principal",
        choices=GOAL_CHOICES,
        required=True,
        widget=forms.RadioSelect(
            attrs={"class": "choice-radio"}
        ),
        help_text="Selecciona el objetivo principal que quieres priorizar esta semana.",
    )

    restricciones = forms.MultipleChoiceField(
        label="Restricciones alimentarias",
        choices=DIET_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "choice-checkbox"}
        ),
        help_text="Marca solo las restricciones que deban respetarse siempre.",
    )

    preferencias = forms.MultipleChoiceField(
        label="Preferencias",
        choices=PREFERENCE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "choice-checkbox"}
        ),
        help_text="Estas preferencias ayudan a adaptar mejor el plan a tu rutina real.",
    )

    presupuesto = forms.IntegerField(
        label="Presupuesto semanal (€)",
        min_value=0,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ej. 60",
                "class": "input-text",
                "inputmode": "numeric",
                "min": "0",
            }
        ),
    )

    meal_context = forms.ChoiceField(
        label="¿Dónde vas a comer principalmente?",
        choices=MEAL_CONTEXT_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": "input-select"}
        ),
    )

    special_situation = forms.ChoiceField(
        label="Situación especial",
        choices=SPECIAL_SITUATION_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": "input-select"}
        ),
    )

    days_away = forms.IntegerField(
        label="Días fuera de casa",
        min_value=0,
        initial=0,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ej. 2",
                "class": "input-text",
                "inputmode": "numeric",
                "min": "0",
            }
        ),
        help_text="Útil si necesitas adaptar el plan a trabajo, viajes o comidas fuera.",
    )

    has_kitchen = forms.ChoiceField(
        label="Acceso a cocina",
        choices=KITCHEN_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": "input-select"}
        ),
    )

    needs_tupper = forms.ChoiceField(
        label="¿Necesita tupper?",
        choices=YES_NO_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": "input-select"}
        ),
    )

    notas = forms.CharField(
        label="Notas adicionales",
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Ej. Cenas ligeras, poco tiempo para cocinar, prefiero repetir ingredientes, no quiero platos muy pesados por la noche...",
                "class": "input-textarea",
                "rows": 4,
            }
        ),
        help_text="Usa este espacio solo para matices o contexto especial. Lo importante ya debe quedar marcado arriba.",
    )

    accept_privacy = forms.BooleanField(
        label="He leído la información de privacidad y entiendo que el plan tiene carácter orientativo.",
        required=True,
        widget=forms.CheckboxInput(
            attrs={"class": "privacy-checkbox"}
        ),
        error_messages={
            "required": "Debes aceptar la política de privacidad antes de generar el plan.",
        },
    )

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("Introduce un nombre válido.")
        return nombre

    def clean_presupuesto(self):
        presupuesto = self.cleaned_data["presupuesto"]
        if presupuesto < 0:
            raise forms.ValidationError("El presupuesto no puede ser negativo.")
        return presupuesto

    def clean_days_away(self):
        days_away = self.cleaned_data.get("days_away")
        if days_away in (None, ""):
            return 0
        if days_away < 0:
            raise forms.ValidationError("Los días fuera de casa no pueden ser negativos.")
        return days_away

    def clean(self):
        cleaned_data = super().clean()

        restricciones = set(cleaned_data.get("restricciones", []))
        preferencias = set(cleaned_data.get("preferencias", []))

        if "vegano" in restricciones and "vegetariano" in restricciones:
            self.add_error(
                "restricciones",
                "No es necesario marcar 'Vegetariano' si ya has marcado 'Vegano'.",
            )

        if "vegano" in restricciones and "pescetariano" in restricciones:
            self.add_error(
                "restricciones",
                "Las opciones 'Vegano' y 'Pescetariano' no son compatibles entre sí.",
            )

        if "vegetariano" in restricciones and "pescetariano" in restricciones:
            self.add_error(
                "restricciones",
                "Las opciones 'Vegetariano' y 'Pescetariano' no deberían combinarse.",
            )

        if "pescado" in preferencias and "vegano" in restricciones:
            self.add_error(
                "preferencias",
                "No puedes seleccionar pescado si has marcado una alimentación vegana.",
            )

        if "huevos" in preferencias and "vegano" in restricciones:
            self.add_error(
                "preferencias",
                "No puedes seleccionar huevos si has marcado una alimentación vegana.",
            )

        if {"pollo", "pavo", "pescado"} & preferencias and "vegetariano" in restricciones:
            self.add_error(
                "preferencias",
                "Si has marcado una alimentación vegetariana, no deberías seleccionar pollo, pavo o pescado.",
            )

        return cleaned_data