from __future__ import annotations

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
    ("", "Selecciona una opción"),
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
    ("", "Selecciona una opción"),
    ("si", "Sí"),
    ("no", "No"),
    ("limitado", "Acceso limitado"),
]

YES_NO_CHOICES = [
    ("", "Selecciona una opción"),
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
                "class": "form-control",
                "autocomplete": "name",
                "aria-label": "Nombre de la persona para personalizar el plan",
            }
        ),
        error_messages={
            "required": "Introduce tu nombre para personalizar el plan.",
            "max_length": "El nombre no puede superar los 100 caracteres.",
        },
    )

    objetivo = forms.ChoiceField(
        label="Objetivo principal",
        choices=GOAL_CHOICES,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                "class": "form-radio",
            }
        ),
        help_text="Elige el objetivo más importante para orientar la propuesta semanal.",
        error_messages={
            "required": "Selecciona un objetivo principal.",
        },
    )

    restricciones = forms.MultipleChoiceField(
        label="Restricciones alimentarias",
        choices=DIET_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-checkbox",
            }
        ),
        help_text=(
            "Marca solo las restricciones que deban respetarse siempre. "
            "Si tienes una pauta médica o nutricional, úsala como referencia principal."
        ),
    )

    preferencias = forms.MultipleChoiceField(
        label="Preferencias",
        choices=PREFERENCE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-checkbox",
            }
        ),
        help_text="Ayudan a que el plan sea más realista, práctico y fácil de seguir.",
    )

    presupuesto = forms.IntegerField(
        label="Presupuesto semanal (€)",
        min_value=0,
        max_value=500,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ej. 60",
                "class": "form-control",
                "inputmode": "numeric",
                "min": "0",
                "max": "500",
                "aria-label": "Presupuesto semanal aproximado en euros",
            }
        ),
        help_text="Indica un presupuesto aproximado para adaptar la lista de la compra.",
        error_messages={
            "required": "Indica tu presupuesto semanal aproximado.",
            "min_value": "El presupuesto no puede ser negativo.",
            "max_value": "Introduce un presupuesto realista.",
            "invalid": "Introduce una cantidad válida.",
        },
    )

    meal_context = forms.ChoiceField(
        label="¿Dónde vas a comer principalmente?",
        choices=MEAL_CONTEXT_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        help_text="Ayuda a adaptar el plan a comidas en casa, trabajo, viaje o restaurantes.",
    )

    special_situation = forms.ChoiceField(
        label="Situación especial",
        choices=SPECIAL_SITUATION_CHOICES,
        required=False,
        initial="normal",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        help_text="Indica si esta semana tiene algún contexto especial.",
    )

    days_away = forms.IntegerField(
        label="Días fuera de casa",
        min_value=0,
        max_value=7,
        initial=0,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ej. 2",
                "class": "form-control",
                "inputmode": "numeric",
                "min": "0",
                "max": "7",
            }
        ),
        help_text="Útil si necesitas adaptar comidas de trabajo, viajes o cenas fuera.",
        error_messages={
            "min_value": "Los días fuera de casa no pueden ser negativos.",
            "max_value": "Una semana tiene como máximo 7 días.",
            "invalid": "Introduce un número válido.",
        },
    )

    has_kitchen = forms.ChoiceField(
        label="Acceso a cocina",
        choices=KITCHEN_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        help_text="Indica si podrás cocinar o solo preparar comidas sencillas.",
    )

    needs_tupper = forms.ChoiceField(
        label="¿Necesitas tupper?",
        choices=YES_NO_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        help_text="Ayuda a proponer comidas transportables y fáciles de organizar.",
    )

    notas = forms.CharField(
        label="Notas adicionales",
        required=False,
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                "placeholder": (
                    "Ej. Cenas ligeras, poco tiempo para cocinar, usar lo que tengo en casa, "
                    "evitar ajo y cebolla, seguir pauta del nutricionista..."
                ),
                "class": "form-textarea",
                "rows": 4,
            }
        ),
        help_text=(
            "Añade aquí matices importantes. Si tienes indicaciones de un profesional, "
            "puedes resumirlas para que la propuesta las tenga en cuenta."
        ),
        error_messages={
            "max_length": "Las notas no pueden superar los 1000 caracteres.",
        },
    )

    accept_privacy = forms.BooleanField(
        label=(
            "He leído la información de privacidad y entiendo que NutriPrompt genera "
            "una propuesta orientativa que no sustituye el asesoramiento de un profesional "
            "sanitario o nutricional."
        ),
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        error_messages={
            "required": (
                "Debes aceptar que el plan es orientativo y no sustituye el asesoramiento "
                "de un profesional sanitario o nutricional."
            ),
        },
    )

    def clean_nombre(self) -> str:
        nombre = self.cleaned_data.get("nombre", "").strip()

        if len(nombre) < 2:
            raise forms.ValidationError("Introduce un nombre válido.")

        return nombre

    def clean_days_away(self) -> int:
        days_away = self.cleaned_data.get("days_away")

        if days_away in (None, ""):
            return 0

        if days_away < 0:
            raise forms.ValidationError("Los días fuera de casa no pueden ser negativos.")

        if days_away > 7:
            raise forms.ValidationError("No puede haber más de 7 días fuera de casa en una semana.")

        return days_away

    def clean_notas(self) -> str:
        notas = self.cleaned_data.get("notas", "")
        return notas.strip()

    def clean(self) -> dict:
        cleaned_data = super().clean()

        restricciones = set(cleaned_data.get("restricciones") or [])
        preferencias = set(cleaned_data.get("preferencias") or [])

        meal_context = cleaned_data.get("meal_context")
        special_situation = cleaned_data.get("special_situation")
        days_away = cleaned_data.get("days_away") or 0
        has_kitchen = cleaned_data.get("has_kitchen")
        needs_tupper = cleaned_data.get("needs_tupper")

        if "vegano" in restricciones and "vegetariano" in restricciones:
            self.add_error(
                "restricciones",
                "Si marcas 'Vegano', no hace falta marcar también 'Vegetariano'.",
            )

        if "vegano" in restricciones and "pescetariano" in restricciones:
            self.add_error(
                "restricciones",
                "Las opciones 'Vegano' y 'Pescetariano' no son compatibles.",
            )

        if "vegetariano" in restricciones and "pescetariano" in restricciones:
            self.add_error(
                "restricciones",
                "Elige solo una opción: vegetariano o pescetariano.",
            )

        if "vegano" in restricciones and {"pescado", "huevos", "pollo", "pavo"} & preferencias:
            self.add_error(
                "preferencias",
                "Si marcas alimentación vegana, evita seleccionar pescado, huevos, pollo o pavo.",
            )

        if "vegetariano" in restricciones and {"pollo", "pavo", "pescado"} & preferencias:
            self.add_error(
                "preferencias",
                "Si marcas alimentación vegetariana, evita seleccionar pollo, pavo o pescado.",
            )

        if "pescetariano" in restricciones and {"pollo", "pavo"} & preferencias:
            self.add_error(
                "preferencias",
                "Si marcas alimentación pescetariana, evita seleccionar pollo o pavo.",
            )

        if meal_context in {"travel", "restaurant", "work"} and days_away == 0:
            cleaned_data["days_away"] = 1

        if days_away > 0 and not meal_context:
            self.add_error(
                "meal_context",
                "Indica dónde comerás principalmente si vas a estar días fuera de casa.",
            )

        if meal_context == "travel" and not has_kitchen:
            self.add_error(
                "has_kitchen",
                "Indica si tendrás acceso a cocina durante el viaje.",
            )

        if meal_context == "work" and not needs_tupper:
            self.add_error(
                "needs_tupper",
                "Indica si necesitas preparar tupper para adaptar mejor el plan.",
            )

        if special_situation == "travel" and days_away == 0:
            cleaned_data["days_away"] = 1

        return cleaned_data