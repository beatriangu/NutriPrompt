from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import escape
from django.utils.text import slugify

from weasyprint import HTML

from nutriprompt_app.forms import (
    DIET_CHOICES,
    GOAL_CHOICES,
    KITCHEN_CHOICES,
    MEAL_CONTEXT_CHOICES,
    NutriPromptForm,
    PREFERENCE_CHOICES,
    SPECIAL_SITUATION_CHOICES,
    YES_NO_CHOICES,
)
from nutriprompt_app.models import IAGeneratedResponse
from nutriprompt_app.services.ai_generator import generate_meal_plan
from nutriprompt_app.services.profile_classifier import classify_user_profile
from nutriprompt_app.services.shopping_list_generator import generate_shopping_list
from .services.fallback_plan import generate_fallback_meal_plan

logger = logging.getLogger(__name__)

DEMO_MODE_FALLBACK = True
RESULTS_SUBDIR = "resultados"
DEFAULT_USER_LABEL = "Bea"

YES_NO_MAP = dict(YES_NO_CHOICES)
KITCHEN_MAP = dict(KITCHEN_CHOICES)
GOAL_MAP = dict(GOAL_CHOICES)
DIET_MAP = dict(DIET_CHOICES)
PREFERENCE_MAP = dict(PREFERENCE_CHOICES)
MEAL_CONTEXT_MAP = dict(MEAL_CONTEXT_CHOICES)
SPECIAL_SITUATION_MAP = dict(SPECIAL_SITUATION_CHOICES)


def home(request):
    form = NutriPromptForm()
    return render(request, "nutriprompt_app/home.html", {"form": form})


def _safe_value(value: Any, default: str = "No especificado") -> str:
    text = str(value or "").strip()
    return text or default


def _clean_numeric_string(value: Any, default: str = "No especificado") -> str:
    text = str(value or "").strip()
    return text or default


def _join_choice_labels(values: list[str], mapping: dict[str, str], default: str = "No especificadas") -> str:
    if not values:
        return default
    labels = [mapping.get(value, value) for value in values]
    return ", ".join(labels)


def _label_for_choice(value: str, mapping: dict[str, str], default: str = "No especificado") -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return default
    return mapping.get(normalized, normalized)


def _format_profile_tags(profile_tags: list[str]) -> str:
    return ", ".join(profile_tags) if profile_tags else "No detectadas"


def _to_classifier_payload(cleaned_data: dict[str, Any]) -> dict[str, str]:
    return {
        "objetivo": _label_for_choice(cleaned_data.get("objetivo"), GOAL_MAP),
        "restricciones": _join_choice_labels(cleaned_data.get("restricciones", []), DIET_MAP),
        "preferencias": _join_choice_labels(cleaned_data.get("preferencias", []), PREFERENCE_MAP, default="No especificadas"),
        "presupuesto": str(cleaned_data.get("presupuesto", "")).strip(),
        "meal_context": cleaned_data.get("meal_context", "") or "",
        "special_situation": cleaned_data.get("special_situation", "") or "",
        "needs_tupper": cleaned_data.get("needs_tupper", "") or "",
        "has_kitchen": cleaned_data.get("has_kitchen", "") or "",
        "days_away": str(cleaned_data.get("days_away", 0)).strip(),
    }


def _to_display_context(cleaned_data: dict[str, Any]) -> dict[str, str]:
    return {
        "nombre": _safe_value(cleaned_data.get("nombre")),
        "objetivo": _label_for_choice(cleaned_data.get("objetivo"), GOAL_MAP),
        "restricciones": _join_choice_labels(
            cleaned_data.get("restricciones", []),
            DIET_MAP,
            default="No especificadas",
        ),
        "preferencias": _join_choice_labels(
            cleaned_data.get("preferencias", []),
            PREFERENCE_MAP,
            default="No especificadas",
        ),
        "presupuesto": str(cleaned_data.get("presupuesto", "")).strip(),
        "meal_context": _label_for_choice(
            cleaned_data.get("meal_context"),
            MEAL_CONTEXT_MAP,
        ),
        "special_situation": _label_for_choice(
            cleaned_data.get("special_situation"),
            SPECIAL_SITUATION_MAP,
            default="No especificada",
        ),
        "needs_tupper": _label_for_choice(
            cleaned_data.get("needs_tupper"),
            YES_NO_MAP,
        ),
        "has_kitchen": _label_for_choice(
            cleaned_data.get("has_kitchen"),
            KITCHEN_MAP,
        ),
        "days_away": str(cleaned_data.get("days_away", 0)).strip(),
        "notas": _safe_value(cleaned_data.get("notas"), ""),
    }


def _build_user_input_text(display_data: dict[str, str], profile_tags: list[str]) -> str:
    return f"""
Nombre: {_safe_value(display_data.get("nombre"))}
Objetivo: {_safe_value(display_data.get("objetivo"))}
Restricciones: {_safe_value(display_data.get("restricciones"), "No especificadas")}
Preferencias: {_safe_value(display_data.get("preferencias"), "No especificadas")}
Presupuesto semanal: {_clean_numeric_string(display_data.get("presupuesto"))}
Contexto principal: {_safe_value(display_data.get("meal_context"))}
Situación especial: {_safe_value(display_data.get("special_situation"), "No especificada")}
Necesita tupper: {_safe_value(display_data.get("needs_tupper"))}
Acceso a cocina: {_safe_value(display_data.get("has_kitchen"))}
Días fuera de casa: {_clean_numeric_string(display_data.get("days_away"))}
Notas adicionales: {_safe_value(display_data.get("notas"), "No especificadas")}
Etiquetas de perfil detectadas: {_format_profile_tags(profile_tags)}
""".strip()


def _normalize_plan_data(plan_data: Any) -> list[dict[str, str]]:
    if not isinstance(plan_data, list):
        raise ValueError("El plan generado no tiene un formato válido.")

    normalized: list[dict[str, str]] = []

    for index, item in enumerate(plan_data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El elemento {index} del plan no es válido.")

        normalized_item = {
            "day": str(item.get("day", "")).strip(),
            "breakfast": str(item.get("breakfast", "")).strip(),
            "lunch": str(item.get("lunch", "")).strip(),
            "dinner": str(item.get("dinner", "")).strip(),
        }

        if not all(normalized_item.values()):
            raise ValueError(f"El día {index} contiene campos vacíos.")

        normalized.append(normalized_item)

    return normalized


def _build_day_rows(plan_data: list[dict[str, str]]) -> str:
    return "".join(
        f"""
        <tr>
            <td class="day-cell">{escape(day_data["day"])}</td>
            <td>{escape(day_data["breakfast"])}</td>
            <td>{escape(day_data["lunch"])}</td>
            <td>{escape(day_data["dinner"])}</td>
        </tr>
        """
        for day_data in plan_data
    )


def build_plan_html_table(
    plan_data: list[dict[str, str]],
    *,
    nombre: str = "",
    objetivo: str = "",
    restricciones: str = "",
    preferencias: str = "",
    presupuesto: str = "",
    meal_context: str = "",
    special_situation: str = "",
    needs_tupper: str = "",
    has_kitchen: str = "",
    days_away: str = "",
    notas: str = "",
    profile_tags: list[str] | None = None,
) -> str:
    normalized_plan = _normalize_plan_data(plan_data)
    rows_html = _build_day_rows(normalized_plan)
    tags_text = _format_profile_tags(profile_tags or [])

    info_cliente = f"""
        <section class="client-info">
            <h1>Plan semanal personalizado</h1>
            <div class="meta-grid">
                <div class="meta-item"><span class="label">Cliente</span><span class="value">{escape(_safe_value(nombre))}</span></div>
                <div class="meta-item"><span class="label">Objetivo</span><span class="value">{escape(_safe_value(objetivo))}</span></div>
                <div class="meta-item"><span class="label">Restricciones</span><span class="value">{escape(_safe_value(restricciones, "No especificadas"))}</span></div>
                <div class="meta-item"><span class="label">Preferencias</span><span class="value">{escape(_safe_value(preferencias, "No especificadas"))}</span></div>
                <div class="meta-item"><span class="label">Presupuesto semanal</span><span class="value">{escape(_clean_numeric_string(presupuesto))}</span></div>
                <div class="meta-item"><span class="label">Contexto principal</span><span class="value">{escape(_safe_value(meal_context))}</span></div>
                <div class="meta-item"><span class="label">Situación especial</span><span class="value">{escape(_safe_value(special_situation, "No especificada"))}</span></div>
                <div class="meta-item"><span class="label">¿Necesita tupper?</span><span class="value">{escape(_safe_value(needs_tupper))}</span></div>
                <div class="meta-item"><span class="label">Acceso a cocina</span><span class="value">{escape(_safe_value(has_kitchen))}</span></div>
                <div class="meta-item"><span class="label">Días fuera de casa</span><span class="value">{escape(_clean_numeric_string(days_away))}</span></div>
                <div class="meta-item" style="grid-column: 1 / -1;"><span class="label">Notas adicionales</span><span class="value">{escape(_safe_value(notas, "No especificadas"))}</span></div>
                <div class="meta-item" style="grid-column: 1 / -1;"><span class="label">Etiquetas de perfil detectadas</span><span class="value">{escape(tags_text)}</span></div>
            </div>
            <p class="disclaimer">
                Este plan es orientativo y no sustituye el asesoramiento de un profesional sanitario.
            </p>
        </section>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Plan semanal personalizado</title>
        <style>
            @page {{
                size: A4;
                margin: 16mm;
            }}

            :root {{
                --texto: #24323f;
                --texto-secundario: #5f6c76;
                --borde: #d9e2ea;
                --borde-suave: #e9eff4;
                --fondo-cabecera: #eef4f8;
                --fondo-caja: #f8fbfd;
                --fondo-fila: #fafcfd;
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                font-family: Arial, sans-serif;
                color: var(--texto);
                font-size: 13px;
                line-height: 1.5;
                margin: 0;
            }}

            h1 {{
                margin: 0 0 12px 0;
                color: #1f3b57;
                font-size: 24px;
                line-height: 1.2;
            }}

            .client-info {{
                margin-bottom: 22px;
                padding: 16px;
                border: 1px solid var(--borde);
                border-radius: 10px;
                background: var(--fondo-caja);
            }}

            .meta-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 10px;
            }}

            .meta-item {{
                border: 1px solid var(--borde-suave);
                border-radius: 8px;
                background: #ffffff;
                padding: 10px;
            }}

            .label {{
                display: block;
                margin-bottom: 4px;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                color: var(--texto-secundario);
                letter-spacing: 0.02em;
            }}

            .value {{
                display: block;
                color: var(--texto);
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}

            .disclaimer {{
                margin: 14px 0 0;
                font-size: 11px;
                color: var(--texto-secundario);
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
                font-size: 12px;
            }}

            thead {{
                display: table-header-group;
            }}

            tbody {{
                display: table-row-group;
            }}

            tr {{
                page-break-inside: avoid;
            }}

            th, td {{
                border: 1px solid var(--borde);
                padding: 10px;
                vertical-align: top;
                text-align: left;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}

            th {{
                background-color: var(--fondo-cabecera);
                color: #1f3b57;
                font-weight: bold;
            }}

            tbody tr:nth-child(even) td {{
                background-color: var(--fondo-fila);
            }}

            th:first-child,
            td.day-cell {{
                width: 14%;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        {info_cliente}
        <table>
            <thead>
                <tr>
                    <th>Día</th>
                    <th>Desayuno</th>
                    <th>Comida</th>
                    <th>Cena</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """


def _run_fallback_plan(
    classifier_data: dict[str, str],
    profile_tags: list[str],
    texto_cliente: str,
) -> tuple[list[dict[str, str]], str]:
    try:
        fallback_plan_data = generate_fallback_meal_plan(
            nombre=classifier_data["nombre"],
            objetivo=classifier_data["objetivo"],
            restricciones=classifier_data["restricciones"],
            preferencias=classifier_data["preferencias"],
            presupuesto=classifier_data["presupuesto"],
            meal_context=classifier_data["meal_context"],
            special_situation=classifier_data["special_situation"],
            needs_tupper=classifier_data["needs_tupper"],
            has_kitchen=classifier_data["has_kitchen"],
            days_away=classifier_data["days_away"],
            profile_tags=profile_tags,
        )
    except TypeError:
        logger.warning(
            "generate_fallback_meal_plan no acepta keyword args. Se intentará con texto_cliente."
        )
        fallback_plan_data = generate_fallback_meal_plan(texto_cliente)

    normalized_fallback = _normalize_plan_data(fallback_plan_data)
    logger.info("Fallback personalizado generado correctamente.")
    return normalized_fallback, "fallback"


def _generate_plan_data(
    *,
    classifier_data: dict[str, str],
    profile_tags: list[str],
    texto_cliente: str,
) -> tuple[list[dict[str, str]], str]:
    if DEMO_MODE_FALLBACK:
        logger.warning("DEMO_MODE_FALLBACK=True. Se usará el fallback personalizado.")
        return _run_fallback_plan(classifier_data, profile_tags, texto_cliente)

    try:
        plan_data, provider = generate_meal_plan(texto_cliente)
        normalized_plan = _normalize_plan_data(plan_data)
        logger.info("Plan generado correctamente con provider='%s'.", provider)
        return normalized_plan, provider

    except Exception as exc:
        logger.exception(
            "La generación principal con IA ha fallado. Se usará fallback. Error: %s",
            exc,
        )
        try:
            return _run_fallback_plan(classifier_data, profile_tags, texto_cliente)
        except Exception as fallback_exc:
            logger.exception("El fallback también ha fallado: %s", fallback_exc)
            raise ValueError(
                "No se ha podido generar un plan válido ni con la IA ni con el sistema de respaldo."
            ) from fallback_exc


def _save_plan_files(nombre: str, tabla_html: str) -> dict[str, str]:
    output_dir = Path(settings.MEDIA_ROOT) / RESULTS_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    safe_name = slugify(nombre) or "cliente"

    html_filename = f"plan_{safe_name}_{timestamp}.html"
    pdf_filename = f"plan_{safe_name}_{timestamp}.pdf"

    html_path = output_dir / html_filename
    pdf_path = output_dir / pdf_filename

    html_path.write_text(tabla_html, encoding="utf-8")
    HTML(string=tabla_html, base_url=str(Path(settings.BASE_DIR))).write_pdf(str(pdf_path))

    return {
        "html_filename": html_filename,
        "pdf_filename": pdf_filename,
        "html_url": f"{settings.MEDIA_URL}{RESULTS_SUBDIR}/{html_filename}",
        "pdf_url": f"{settings.MEDIA_URL}{RESULTS_SUBDIR}/{pdf_filename}",
    }


def _classify_profile(classifier_data: dict[str, str]) -> list[str]:
    try:
        profile_tags = classify_user_profile(
            objetivo=classifier_data["objetivo"],
            restricciones=classifier_data["restricciones"],
            preferencias=classifier_data["preferencias"],
            presupuesto=classifier_data["presupuesto"],
            meal_context=classifier_data["meal_context"],
            special_situation=classifier_data["special_situation"],
            needs_tupper=classifier_data["needs_tupper"],
            has_kitchen=classifier_data["has_kitchen"],
            days_away=classifier_data["days_away"],
        )
        if not isinstance(profile_tags, list):
            logger.warning("El clasificador ha devuelto un valor no válido. Se usará lista vacía.")
            return []
        return profile_tags

    except Exception as exc:
        logger.exception(
            "La clasificación de perfil ha fallado. Se continuará sin etiquetas. Error: %s",
            exc,
        )
        return []


def _build_result_context(
    *,
    display_data: dict[str, str],
    profile_tags: list[str],
    shopping_list: dict[str, list[str]],
    source_type: str,
    archivos: dict[str, str],
    tabla_html: str,
) -> dict[str, Any]:
    return {
        "tabla_html": tabla_html,
        "pdf_url": archivos["pdf_url"],
        "html_url": archivos["html_url"],
        "nombre": display_data["nombre"],
        "source_type": source_type,
        "profile_tags": profile_tags,
        "shopping_list": shopping_list,
        "used_fallback": source_type == "fallback",
    }


def procesar_plan_directo(request):
    if request.method != "POST":
        form = NutriPromptForm()
        return render(request, "nutriprompt_app/home.html", {"form": form})

    form = NutriPromptForm(request.POST)

    if not form.is_valid():
        return render(
            request,
            "nutriprompt_app/home.html",
            {
                "form": form,
                "error": "Revisa los campos marcados y corrige la información antes de generar el plan.",
            },
        )

    cleaned_data = form.cleaned_data
    classifier_data = {
        "nombre": cleaned_data["nombre"],
        **_to_classifier_payload(cleaned_data),
    }
    display_data = _to_display_context(cleaned_data)

    profile_tags = _classify_profile(classifier_data)
    texto_cliente = _build_user_input_text(display_data, profile_tags)

    try:
        plan_data, source_type = _generate_plan_data(
            classifier_data=classifier_data,
            profile_tags=profile_tags,
            texto_cliente=texto_cliente,
        )

        try:
            shopping_list = generate_shopping_list(plan_data)
            if not isinstance(shopping_list, dict):
                logger.warning("La lista de la compra no tiene formato dict. Se usará un dict vacío.")
                shopping_list = {}
        except Exception as exc:
            logger.exception(
                "La generación de la lista de la compra ha fallado. Se usará una vacía. Error: %s",
                exc,
            )
            shopping_list = {}

        tabla_html = build_plan_html_table(
            plan_data=plan_data,
            nombre=display_data["nombre"],
            objetivo=display_data["objetivo"],
            restricciones=display_data["restricciones"],
            preferencias=display_data["preferencias"],
            presupuesto=display_data["presupuesto"],
            meal_context=display_data["meal_context"],
            special_situation=display_data["special_situation"],
            needs_tupper=display_data["needs_tupper"],
            has_kitchen=display_data["has_kitchen"],
            days_away=display_data["days_away"],
            notas=display_data["notas"],
            profile_tags=profile_tags,
        )

        archivos = _save_plan_files(nombre=display_data["nombre"], tabla_html=tabla_html)

        resultado_guardado = {
            "plan": plan_data,
            "profile_tags": profile_tags,
            "shopping_list": shopping_list,
            "source_type": source_type,
        }

        IAGeneratedResponse.objects.create(
            servicio="NutriPrompt",
            usuario=DEFAULT_USER_LABEL,
            paciente=display_data["nombre"],
            entrada_usuario=texto_cliente,
            resultado_ia=json.dumps(resultado_guardado, ensure_ascii=False, indent=2),
            html_file=archivos["html_filename"],
            pdf_file=archivos["pdf_filename"],
        )

        logger.info(
            "Plan guardado correctamente para paciente='%s' con source='%s'.",
            display_data["nombre"],
            source_type,
        )

        return render(
            request,
            "nutriprompt_app/resultado.html",
            _build_result_context(
                display_data=display_data,
                profile_tags=profile_tags,
                shopping_list=shopping_list,
                source_type=source_type,
                archivos=archivos,
                tabla_html=tabla_html,
            ),
        )

    except Exception as exc:
        logger.exception("Error al procesar el plan para '%s'.", display_data["nombre"])
        form.add_error(None, str(exc) or "Ha ocurrido un error inesperado al generar el plan.")
        return render(
            request,
            "nutriprompt_app/home.html",
            {
                "form": form,
                "error": str(exc) or "Ha ocurrido un error inesperado al generar el plan.",
            },
        )